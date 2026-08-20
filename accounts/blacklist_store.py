import threading
import time
import uuid

from django.db import IntegrityError
from django.utils.timezone import now as django_now

from accounts.models import (
    KIND_LIMIT,
    KIND_LOGIN,
    KIND_MANUAL,
    KIND_RATE,
    BlacklistEntry,
)

ALL_KINDS = (KIND_MANUAL, KIND_RATE, KIND_LOGIN, KIND_LIMIT)

KIND_LABELS = {
    KIND_MANUAL: 'Manual',
    KIND_RATE: 'Rate limit',
    KIND_LOGIN: 'Login attempts',
    KIND_LIMIT: 'Total requests',
}

LOCAL_IPS = frozenset({'127.0.0.1', '::1', 'localhost'})

_cache_lock = threading.Lock()
_cache = {'loaded_at': 0.0, 'by_kind': {}, 'all': frozenset()}


def _entry_to_dict(entry):
    return {
        '_id': str(entry.pk),
        'ip': entry.ip,
        'kind': entry.kind,
        'note': entry.note,
        'created_at': entry.created_at,
    }


def is_local_ip(ip):
    value = (ip or '').strip().lower()
    return value in LOCAL_IPS


def _invalidate_lookup_cache():
    with _cache_lock:
        _cache['loaded_at'] = 0.0


def _load_cache(force=False):
    now = time.monotonic()
    with _cache_lock:
        if not force and _cache['loaded_at'] and now - _cache['loaded_at'] < 1.0:
            return _cache

    by_kind = {kind: set() for kind in ALL_KINDS}
    all_ips = set()
    for entry in BlacklistEntry.objects.only('ip', 'kind').iterator():
        by_kind[entry.kind].add(entry.ip)
        all_ips.add(entry.ip)

    with _cache_lock:
        _cache['by_kind'] = {k: frozenset(v) for k, v in by_kind.items()}
        _cache['all'] = frozenset(all_ips)
        _cache['loaded_at'] = time.monotonic()
        return _cache


def get_ips_for_kind(kind):
    cache = _load_cache()
    return cache['by_kind'].get(kind, frozenset())


def is_ip_blocked(ip):
    cache = _load_cache()
    return (ip or '').strip() in cache['all']


def get_block_reasons(ip):
    ip = (ip or '').strip()
    if not ip:
        return []
    cache = _load_cache()
    reasons = []
    for kind in ALL_KINDS:
        if ip in cache['by_kind'].get(kind, frozenset()):
            reasons.append(KIND_LABELS.get(kind, kind))
    return reasons


def get_block_reasons_map():
    cache = _load_cache()
    result = {}
    for kind in ALL_KINDS:
        label = KIND_LABELS.get(kind, kind)
        for blocked_ip in cache['by_kind'].get(kind, frozenset()):
            result.setdefault(blocked_ip, []).append(label)
    return result


def add_blacklist_ip(ip, kind, note='', *, invalidate=True):
    ip = (ip or '').strip()
    if not ip or kind not in ALL_KINDS or is_local_ip(ip):
        return False

    try:
        BlacklistEntry.objects.create(
            ip=ip,
            kind=kind,
            note=note or '',
            created_at=django_now(),
        )
    except IntegrityError:
        return False

    if invalidate:
        _invalidate_lookup_cache()
    return True


def remove_blacklist_entry(entry_id):
    entry_id = (entry_id or '').strip()
    if not entry_id:
        return False

    try:
        entry_uuid = uuid.UUID(entry_id)
    except ValueError:
        return False

    deleted, _ = BlacklistEntry.objects.filter(pk=entry_uuid).delete()
    if deleted:
        _invalidate_lookup_cache()
    return bool(deleted)


def remove_blacklist_ip(ip, kind=None):
    ip = (ip or '').strip()
    if not ip:
        return 0

    queryset = BlacklistEntry.objects.filter(ip=ip)
    if kind in ALL_KINDS:
        queryset = queryset.filter(kind=kind)
    deleted, _ = queryset.delete()
    if deleted:
        _invalidate_lookup_cache()
    return deleted


def list_blacklist_entries(kind=None):
    queryset = BlacklistEntry.objects.all()
    if kind in ALL_KINDS:
        queryset = queryset.filter(kind=kind)
    return [_entry_to_dict(entry) for entry in queryset]
