import threading
import time

from django.conf import settings
from django.db import transaction

from accounts.models import BlacklistPolicy

POLICY_DOC_ID = 'blacklist_policy'

DEFAULT_POLICY = {
    'redirect_url': 'https://www.naver.com/',
    'rate_limit_enabled': True,
    'rate_limit_max_requests': 80,
    'rate_limit_window_seconds': 60,
    'total_request_limit_enabled': True,
    'total_request_limit_max': 500,
    'login_attempt_max': 2,
    'login_loading_enabled': True,
    'login_loading_delay_ms': 3000,
    'login_splash_enabled': True,
    'login_splash_delay_ms': 1000,
}

_cache_lock = threading.Lock()
_cache = {'loaded_at': 0.0, 'policy': None}


def _defaults_from_django_settings():
    return {
        'redirect_url': getattr(settings, 'BLACKLIST_REDIRECT_URL', DEFAULT_POLICY['redirect_url']),
        'rate_limit_enabled': bool(getattr(settings, 'RATE_LIMIT_ENABLED', True)),
        'rate_limit_max_requests': int(getattr(settings, 'RATE_LIMIT_MAX_REQUESTS', 80)),
        'rate_limit_window_seconds': int(getattr(settings, 'RATE_LIMIT_WINDOW_SECONDS', 60)),
        'total_request_limit_enabled': bool(getattr(settings, 'TOTAL_REQUEST_LIMIT_ENABLED', True)),
        'total_request_limit_max': int(getattr(settings, 'TOTAL_REQUEST_LIMIT_MAX', 500)),
        'login_attempt_max': int(getattr(settings, 'LOGIN_ATTEMPT_MAX', 2)),
        'login_loading_enabled': bool(getattr(settings, 'LOGIN_LOADING_ENABLED', True)),
        'login_loading_delay_ms': int(getattr(settings, 'LOGIN_LOADING_DELAY_MS', 3000)),
        'login_splash_enabled': bool(getattr(settings, 'LOGIN_SPLASH_ENABLED', True)),
        'login_splash_delay_ms': int(getattr(settings, 'LOGIN_SPLASH_DELAY_MS', 1000)),
    }


def _normalize_policy(raw):
    base = _defaults_from_django_settings()
    if not isinstance(raw, dict):
        return dict(base)

    redirect_url = str(raw.get('redirect_url') or base['redirect_url']).strip()
    if not redirect_url:
        redirect_url = base['redirect_url']

    def as_bool(value, default):
        if isinstance(value, bool):
            return value
        if value in (0, 1, '0', '1', 'true', 'false', 'True', 'False', 'on', 'off'):
            return str(value).lower() in ('1', 'true', 'on')
        return default

    def as_int(value, default, minimum=1):
        try:
            number = int(value)
        except (TypeError, ValueError):
            return default
        return max(minimum, number)

    return {
        'redirect_url': redirect_url,
        'rate_limit_enabled': as_bool(raw.get('rate_limit_enabled'), base['rate_limit_enabled']),
        'rate_limit_max_requests': as_int(
            raw.get('rate_limit_max_requests'), base['rate_limit_max_requests']
        ),
        'rate_limit_window_seconds': as_int(
            raw.get('rate_limit_window_seconds'), base['rate_limit_window_seconds']
        ),
        'total_request_limit_enabled': as_bool(
            raw.get('total_request_limit_enabled'), base['total_request_limit_enabled']
        ),
        'total_request_limit_max': as_int(
            raw.get('total_request_limit_max'), base['total_request_limit_max']
        ),
        'login_attempt_max': as_int(raw.get('login_attempt_max'), base['login_attempt_max']),
        'login_loading_enabled': as_bool(
            raw.get('login_loading_enabled'), base['login_loading_enabled']
        ),
        'login_loading_delay_ms': as_int(
            raw.get('login_loading_delay_ms'), base['login_loading_delay_ms'], minimum=0
        ),
        'login_splash_enabled': as_bool(
            raw.get('login_splash_enabled'), base['login_splash_enabled']
        ),
        'login_splash_delay_ms': as_int(
            raw.get('login_splash_delay_ms'), base['login_splash_delay_ms'], minimum=0
        ),
    }


def _policy_to_dict(policy):
    return {
        'redirect_url': policy.redirect_url,
        'rate_limit_enabled': policy.rate_limit_enabled,
        'rate_limit_max_requests': policy.rate_limit_max_requests,
        'rate_limit_window_seconds': policy.rate_limit_window_seconds,
        'total_request_limit_enabled': policy.total_request_limit_enabled,
        'total_request_limit_max': policy.total_request_limit_max,
        'login_attempt_max': policy.login_attempt_max,
        'login_loading_enabled': policy.login_loading_enabled,
        'login_loading_delay_ms': policy.login_loading_delay_ms,
        'login_splash_enabled': policy.login_splash_enabled,
        'login_splash_delay_ms': policy.login_splash_delay_ms,
    }


def invalidate_policy_cache():
    with _cache_lock:
        _cache['loaded_at'] = 0.0
        _cache['policy'] = None


def _get_policy_row(*, create=True):
    defaults = _defaults_from_django_settings()
    if create:
        policy, _ = BlacklistPolicy.objects.get_or_create(pk=1, defaults=defaults)
        return policy
    return BlacklistPolicy.objects.filter(pk=1).first()


def get_blacklist_policy(*, force=False):
    now = time.monotonic()
    with _cache_lock:
        if not force and _cache['policy'] is not None and now - _cache['loaded_at'] < 1.0:
            return dict(_cache['policy'])

    policy_row = _get_policy_row()
    policy = _policy_to_dict(policy_row)

    with _cache_lock:
        _cache['policy'] = dict(policy)
        _cache['loaded_at'] = time.monotonic()
    return policy


def ensure_default_policy():
    _get_policy_row()
    return get_blacklist_policy(force=True)


def reset_blacklist_policy():
    defaults = _defaults_from_django_settings()
    with transaction.atomic():
        policy_row, _ = BlacklistPolicy.objects.select_for_update().get_or_create(
            pk=1, defaults=defaults
        )
        for field, value in defaults.items():
            setattr(policy_row, field, value)
        policy_row.save()
    invalidate_policy_cache()
    return dict(defaults)


def update_blacklist_policy(updates):
    current = get_blacklist_policy(force=True)
    merged = _normalize_policy({**current, **updates})
    with transaction.atomic():
        policy_row, _ = BlacklistPolicy.objects.select_for_update().get_or_create(
            pk=1, defaults=_defaults_from_django_settings()
        )
        for field, value in merged.items():
            setattr(policy_row, field, value)
        policy_row.save()
    invalidate_policy_cache()
    return merged
