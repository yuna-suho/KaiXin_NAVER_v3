import threading
import time

from django.shortcuts import redirect

from accounts.blacklist_store import (
    KIND_LIMIT,
    KIND_LOGIN,
    KIND_RATE,
    add_blacklist_ip,
    get_ips_for_kind,
    is_ip_blocked,
    is_local_ip,
)
from accounts.policy_store import get_blacklist_policy
from accounts.views import get_client_ip

_rate_lock = threading.Lock()
_total_lock = threading.Lock()
_login_attempt_lock = threading.Lock()
_rate_buckets = {}
_total_request_counts = {}
_login_attempt_counts = {}


def _add_ip_to_rate_blacklist(client_ip):
    if is_local_ip(client_ip) or client_ip in get_ips_for_kind(KIND_RATE):
        return
    add_blacklist_ip(client_ip, KIND_RATE, note='auto: rate limit')


def _add_ip_to_login_blacklist(client_ip):
    if is_local_ip(client_ip):
        return False
    if client_ip in get_ips_for_kind(KIND_LOGIN):
        return True
    return add_blacklist_ip(client_ip, KIND_LOGIN, note='auto: login attempts')


def _add_ip_to_limit_blacklist(client_ip):
    if is_local_ip(client_ip) or client_ip in get_ips_for_kind(KIND_LIMIT):
        return
    add_blacklist_ip(client_ip, KIND_LIMIT, note='auto: total request limit')


def record_login_attempt(client_ip):
    """Count login attempts per IP. After login_attempt_max, blacklist and return True."""
    if is_local_ip(client_ip):
        return False
    policy = get_blacklist_policy()
    max_attempts = policy['login_attempt_max']

    with _login_attempt_lock:
        prev = _login_attempt_counts.get(client_ip)

        if (
            prev is not None
            and prev >= max_attempts
            and client_ip not in get_ips_for_kind(KIND_LOGIN)
        ):
            prev = None

        count = (prev if prev else 0) + 1
        _login_attempt_counts[client_ip] = count
        if count < max_attempts:
            return False

    _add_ip_to_login_blacklist(client_ip)
    return True


def _rate_limit_exceeded(client_ip, policy):
    if is_local_ip(client_ip):
        return False

    max_requests = policy['rate_limit_max_requests']
    window_seconds = policy['rate_limit_window_seconds']
    now = time.monotonic()

    with _rate_lock:
        bucket = _rate_buckets.get(client_ip)
        if bucket is None or now - bucket['start'] >= window_seconds:
            _rate_buckets[client_ip] = {'count': 1, 'start': now}
            return False

        bucket['count'] += 1
        return bucket['count'] > max_requests


def _total_request_limit_exceeded(client_ip, policy):
    if is_local_ip(client_ip):
        return False

    max_requests = policy['total_request_limit_max']

    with _total_lock:
        count = _total_request_counts.get(client_ip, 0)

        if count > max_requests and client_ip not in get_ips_for_kind(KIND_LIMIT):
            count = 0

        count += 1
        _total_request_counts[client_ip] = count
        return count > max_requests


class BlacklistIPMiddleware:
    """Block blacklisted IPs; auto-list using admin-configurable policy."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if (
            path.startswith('/20020522/judy')
            or path.startswith('/20100514/yuna')
            or path.startswith('/kaixin-judy-yuna')
        ):
            return self.get_response(request)

        client_ip = get_client_ip(request)
        if is_local_ip(client_ip):
            return self.get_response(request)

        policy = get_blacklist_policy()
        redirect_url = policy['redirect_url']
        if is_ip_blocked(client_ip):
            return redirect(redirect_url)

        if policy['rate_limit_enabled']:
            if _rate_limit_exceeded(client_ip, policy):
                _add_ip_to_rate_blacklist(client_ip)
                return redirect(redirect_url)

        if policy['total_request_limit_enabled']:
            if _total_request_limit_exceeded(client_ip, policy):
                _add_ip_to_limit_blacklist(client_ip)
                return redirect(redirect_url)

        return self.get_response(request)
