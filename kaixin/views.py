from datetime import datetime
import json

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.timezone import make_aware, get_current_timezone
from django.views.decorators.http import require_http_methods, require_POST

from accounts.blacklist_store import (
    KIND_LABELS,
    KIND_MANUAL,
    add_blacklist_ip,
    get_block_reasons,
    get_block_reasons_map,
    is_ip_blocked,
    is_local_ip,
    list_blacklist_entries,
    remove_blacklist_entry,
    remove_blacklist_ip,
)
from accounts.policy_store import (
    ensure_default_policy,
    get_blacklist_policy,
    reset_blacklist_policy,
    update_blacklist_policy,
)
from kaixin.auth import (
    PENDING_MESSAGE,
    get_current_admin,
    login_admin,
    login_required,
    logout_admin,
    superadmin_required,
)
from kaixin.store import (
    aggregate_logs_by_ip,
    count_admin_users,
    create_admin_user,
    delete_admin_user,
    delete_all_logs,
    delete_logs_for_ip,
    export_request_logs,
    find_admin_by_username,
    format_request_data,
    format_timestamp,
    list_admin_users,
    list_logs_for_ip,
    list_methods_for_ip,
    list_pending_admins,
    set_admin_approval,
)


def _base_context(request, admin=None):
    admin = admin if admin is not None else getattr(request, 'kaixin_admin', None)
    return {
        'admin': admin,
        'is_superadmin': bool(admin and admin.get('is_superadmin')),
    }


def _parse_export_datetime(raw_value):
    value = (raw_value or '').strip()
    if not value:
        return None
    for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            parsed = datetime.strptime(value, fmt)
            break
        except ValueError:
            parsed = None
    else:
        return None
    if parsed.tzinfo is None:
        parsed = make_aware(parsed, get_current_timezone())
    return parsed


def _json_export_response(payload, filename):
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    response = HttpResponse(body, content_type='application/json; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@require_http_methods(['GET', 'POST'])
def login_view(request):
    admin = get_current_admin(request)
    if admin is not None:
        if admin.get('is_approved'):
            return redirect('kaixin:dashboard')
        logout_admin(request)

    error = ''
    info = ''
    username = ''
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        user = find_admin_by_username(username) if username else None
        if user is None or not check_password(password, user.get('password_hash', '')):
            error = 'Invalid username or password.'
        elif not user.get('is_approved'):
            info = PENDING_MESSAGE
        else:
            login_admin(request, user)
            return redirect('kaixin:dashboard')

    return render(
        request,
        'kaixin/login.html',
        {
            'error': error,
            'info': info,
            'username': username,
            'has_admins': count_admin_users() > 0,
        },
    )


@require_http_methods(['GET', 'POST'])
def register_view(request):
    admin = get_current_admin(request)
    if admin is not None:
        if admin.get('is_approved'):
            return redirect('kaixin:dashboard')
        logout_admin(request)

    is_first = count_admin_users() == 0
    error = ''
    username = ''
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        password_confirm = request.POST.get('password_confirm') or ''

        if len(username) < 3:
            error = 'Username must be at least 3 characters.'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters.'
        elif password != password_confirm:
            error = 'Passwords do not match.'
        else:
            created = create_admin_user(
                username,
                make_password(password),
                is_superadmin=is_first,
                is_approved=is_first,
            )
            if created is None:
                error = 'Username is already taken.'
            elif is_first:
                login_admin(request, created)
                return redirect('kaixin:dashboard')
            else:
                messages.info(request, PENDING_MESSAGE)
                return redirect('kaixin:login')

    return render(
        request,
        'kaixin/register.html',
        {'error': error, 'username': username, 'is_first': is_first},
    )


@require_POST
def logout_view(request):
    logout_admin(request)
    return redirect('kaixin:login')


@login_required
@require_http_methods(['GET', 'POST'])
def dashboard(request):
    if request.method == 'POST':
        action = request.POST.get('action') or ''
        ip = (request.POST.get('ip') or '').strip()
        if ip and action == 'block':
            if not is_local_ip(ip):
                add_blacklist_ip(ip, KIND_MANUAL, note='manual block from request logs')
        elif ip and action == 'unblock':
            remove_blacklist_ip(ip)
        elif ip and action == 'delete':
            delete_logs_for_ip(ip)
        elif action == 'delete_all':
            delete_all_logs()
        return redirect('kaixin:dashboard')

    rows = []
    block_reasons = get_block_reasons_map()
    for item in aggregate_logs_by_ip():
        ip = item.get('_id') or 'unknown'
        local = is_local_ip(ip)
        reasons = [] if local else (block_reasons.get(ip) or [])
        rows.append(
            {
                'ip': ip,
                'count': item.get('count', 0),
                'last_seen': format_timestamp(item.get('last_seen')),
                'first_seen': format_timestamp(item.get('first_seen')),
                'devices': ', '.join(sorted(d for d in (item.get('devices') or []) if d))
                or '-',
                'is_local': local,
                'blocked': bool(reasons) or (not local and is_ip_blocked(ip)),
                'block_reason': ', '.join(reasons) if reasons else '',
            }
        )
    context = _base_context(request)
    context['rows'] = rows
    return render(request, 'kaixin/dashboard.html', context)


@login_required
@require_http_methods(['GET'])
def export_logs_view(request):
    ip = (request.GET.get('ip') or '').strip() or None
    method = (request.GET.get('method') or '').strip().upper() or None
    since_raw = request.GET.get('since')
    until_raw = request.GET.get('until')
    since = _parse_export_datetime(since_raw)
    until = _parse_export_datetime(until_raw)
    if since_raw and since is None:
        return HttpResponse(
            'Invalid since datetime. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM.',
            status=400,
            content_type='text/plain; charset=utf-8',
        )
    if until_raw and until is None:
        return HttpResponse(
            'Invalid until datetime. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM.',
            status=400,
            content_type='text/plain; charset=utf-8',
        )
    if since and until and since > until:
        return HttpResponse(
            'Since must be earlier than until.',
            status=400,
            content_type='text/plain; charset=utf-8',
        )

    logs = export_request_logs(ip=ip, method=method, since=since, until=until)
    exported_at = datetime.now(tz=get_current_timezone()).isoformat()
    payload = {
        'exported_at': exported_at,
        'filters': {
            'ip': ip,
            'method': method,
            'since': since.isoformat() if since else None,
            'until': until.isoformat() if until else None,
        },
        'count': len(logs),
        'logs': logs,
    }
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    scope = (ip or 'all').replace(':', '_').replace('/', '_')
    filename = f'request_logs_{scope}_{stamp}.json'
    return _json_export_response(payload, filename)


@login_required
@require_http_methods(['GET', 'POST'])
def ip_logs(request, ip):
    method_filter = (request.GET.get('method') or '').strip().upper()
    available_methods = list_methods_for_ip(ip)
    if method_filter and method_filter not in available_methods:
        method_filter = ''

    def _ip_logs_redirect():
        if method_filter:
            return redirect(f"{reverse('kaixin:ip_logs', kwargs={'ip': ip})}?method={method_filter}")
        return redirect('kaixin:ip_logs', ip=ip)

    if request.method == 'POST':
        action = request.POST.get('action') or ''
        if action == 'delete':
            delete_logs_for_ip(ip)
            return redirect('kaixin:dashboard')
        if action == 'block':
            if not is_local_ip(ip):
                add_blacklist_ip(ip, KIND_MANUAL, note='manual block from request logs')
            return _ip_logs_redirect()
        if action == 'unblock':
            remove_blacklist_ip(ip)
            return _ip_logs_redirect()

    logs = []
    for doc in list_logs_for_ip(ip, method=method_filter or None):
        logs.append(
            {
                'timestamp': format_timestamp(doc.get('timestamp')),
                'method': doc.get('method') or '-',
                'path': doc.get('path') or '-',
                'query': format_request_data(doc.get('query')),
                'body': format_request_data(doc.get('body')),
                'device': doc.get('device') or '-',
                'os': doc.get('os') or '-',
                'browser': doc.get('browser') or '-',
                'model': doc.get('model') or '-',
                'language': doc.get('language') or '-',
            }
        )
    context = _base_context(request)
    local = is_local_ip(ip)
    reasons = [] if local else get_block_reasons(ip)
    context.update(
        {
            'ip': ip,
            'logs': logs,
            'is_local': local,
            'blocked': bool(reasons) or (not local and is_ip_blocked(ip)),
            'block_reason': ', '.join(reasons) if reasons else '',
            'method_filter': method_filter,
            'available_methods': available_methods,
        }
    )
    return render(request, 'kaixin/ip_logs.html', context)


@superadmin_required
@require_http_methods(['GET', 'POST'])
def admins_view(request):
    if request.method == 'POST':
        admin_id = request.POST.get('admin_id') or ''
        action = request.POST.get('action') or ''
        if action == 'approve':
            set_admin_approval(admin_id, True)
        elif action == 'revoke':
            set_admin_approval(admin_id, False)
        elif action == 'delete':
            delete_admin_user(admin_id)
        return redirect('kaixin:admins')

    pending = []
    for user in list_pending_admins():
        pending.append(
            {
                'id': str(user['_id']),
                'username': user.get('username') or '-',
                'created_at': format_timestamp(user.get('created_at')),
            }
        )

    admins = []
    for user in list_admin_users():
        admins.append(
            {
                'id': str(user['_id']),
                'username': user.get('username') or '-',
                'is_superadmin': bool(user.get('is_superadmin')),
                'is_approved': bool(user.get('is_approved')),
                'created_at': format_timestamp(user.get('created_at')),
            }
        )

    context = _base_context(request)
    context.update({'pending': pending, 'admins': admins})
    return render(request, 'kaixin/admins.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def blacklist_view(request):
    error = ''
    if request.method == 'POST':
        action = request.POST.get('action') or ''
        if action == 'add':
            ip = (request.POST.get('ip') or '').strip()
            if not ip:
                error = 'IP address is required.'
            elif is_local_ip(ip):
                error = 'Local addresses cannot be blacklisted.'
            elif not add_blacklist_ip(ip, KIND_MANUAL, note='manual'):
                error = 'IP is already on this list (or could not be saved).'
            else:
                return redirect('kaixin:blacklist')
        elif action == 'delete':
            entry_id = request.POST.get('entry_id') or ''
            remove_blacklist_entry(entry_id)
            return redirect('kaixin:blacklist')
        elif action == 'save_policy':
            saved = update_blacklist_policy(
                {
                    'redirect_url': request.POST.get('redirect_url'),
                    'rate_limit_enabled': request.POST.get('rate_limit_enabled') == 'on',
                    'rate_limit_max_requests': request.POST.get('rate_limit_max_requests'),
                    'rate_limit_window_seconds': request.POST.get('rate_limit_window_seconds'),
                    'total_request_limit_enabled': request.POST.get(
                        'total_request_limit_enabled'
                    )
                    == 'on',
                    'total_request_limit_max': request.POST.get('total_request_limit_max'),
                    'login_attempt_max': request.POST.get('login_attempt_max'),
                    'login_loading_enabled': request.POST.get('login_loading_enabled') == 'on',
                    'login_loading_delay_ms': request.POST.get('login_loading_delay_ms'),
                    'login_splash_enabled': request.POST.get('login_splash_enabled') == 'on',
                    'login_splash_delay_ms': request.POST.get('login_splash_delay_ms'),
                }
            )
            if saved is None:
                error = 'Failed to save policy settings.'
            else:
                return redirect('kaixin:blacklist')
        elif action == 'reset_policy':
            if reset_blacklist_policy() is None:
                error = 'Failed to reset policy settings.'
            else:
                return redirect('kaixin:blacklist')

    policy = ensure_default_policy()

    entries = []
    for doc in list_blacklist_entries():
        kind = doc.get('kind')
        entries.append(
            {
                'id': str(doc['_id']),
                'ip': doc.get('ip') or '-',
                'reason': KIND_LABELS.get(kind, kind or '-'),
            }
        )

    context = _base_context(request)
    context.update(
        {
            'entries': entries,
            'error': error,
            'policy': policy,
        }
    )
    return render(request, 'kaixin/blacklist.html', context)
