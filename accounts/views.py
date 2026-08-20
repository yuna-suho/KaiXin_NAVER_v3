import re

from django.conf import settings
from django.shortcuts import redirect, render
from django.utils.timezone import now as django_now

from accounts.policy_store import get_blacklist_policy
from accounts.request_log_store import insert_request_log

SUPPORTED_LANGUAGES = {'ko', 'en'}
WINDOWS_NT_NAMES = {
    '10.0': 'Windows 10/11',
    '6.3': 'Windows 8.1',
    '6.2': 'Windows 8',
    '6.1': 'Windows 7',
    '6.0': 'Windows Vista',
    '5.1': 'Windows XP',
}


def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '') or 'unknown'


def _match_group(pattern, text, flags=0):
    match = re.search(pattern, text, flags)
    return match.group(1) if match else ''


def get_device_info(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '') or ''
    ua = user_agent.lower()
    device_model = ''

    if any(token in ua for token in ('ipad', 'tablet', 'kindle', 'silk')):
        device_type = 'Tablet'
    elif any(token in ua for token in ('mobi', 'iphone', 'android', 'windows phone')):
        device_type = 'Mobile'
    else:
        device_type = 'Desktop'

    android_version = _match_group(r'Android\s+([0-9]+(?:\.[0-9]+)*)', user_agent)
    ios_version = _match_group(r'(?:iPhone OS|CPU OS|CPU iPhone OS)\s+([0-9_]+)', user_agent)
    windows_nt = _match_group(r'Windows NT\s+([0-9.]+)', user_agent)
    mac_version = _match_group(r'Mac OS X\s+([0-9_]+)', user_agent)
    chromeos_version = _match_group(r'CrOS\s+\w+\s+([0-9.]+)', user_agent)

    if android_version:
        os_name = f'Android {android_version}'
        # Example: Linux; Android 14; SM-S918B Build/...
        device_model = _match_group(
            r'Android\s+[0-9.]+;\s*([^;)]+?)(?:\s+Build/|;|\))',
            user_agent,
        ).strip()
        if device_model.upper() == 'K':
            device_model = ''
    elif ios_version:
        os_name = f'iOS {ios_version.replace("_", ".")}'
        if 'ipad' in ua:
            device_model = 'iPad'
        elif 'iphone' in ua:
            device_model = 'iPhone'
        elif 'ipod' in ua:
            device_model = 'iPod'
    elif windows_nt:
        os_name = f'{WINDOWS_NT_NAMES.get(windows_nt, "Windows")} (NT {windows_nt})'
    elif mac_version:
        os_name = f'macOS {mac_version.replace("_", ".")}'
    elif chromeos_version:
        os_name = f'Chrome OS {chromeos_version}'
    elif 'linux' in ua:
        os_name = 'Linux'
    else:
        os_name = 'Unknown'

    browser_version = ''
    if 'edg/' in ua:
        browser = 'Edge'
        browser_version = _match_group(r'Edg/([0-9.]+)', user_agent)
    elif 'opr/' in ua or 'opera' in ua:
        browser = 'Opera'
        browser_version = _match_group(r'(?:OPR|Opera)/([0-9.]+)', user_agent)
    elif 'firefox/' in ua:
        browser = 'Firefox'
        browser_version = _match_group(r'Firefox/([0-9.]+)', user_agent)
    elif 'chrome/' in ua and 'chromium' not in ua:
        browser = 'Chrome'
        browser_version = _match_group(r'Chrome/([0-9.]+)', user_agent)
    elif 'safari/' in ua and 'chrome/' not in ua:
        browser = 'Safari'
        browser_version = _match_group(r'Version/([0-9.]+)', user_agent)
    else:
        browser = 'Unknown'

    if browser_version:
        browser = f'{browser} {browser_version}'

    return {
        'user_agent': user_agent,
        'device_type': device_type,
        'device_model': device_model,
        'os_name': os_name,
        'browser': browser,
    }


def _querydict_to_dict(query_dict):
    result = {}
    for key in query_dict.keys():
        values = query_dict.getlist(key)
        result[key] = values[0] if len(values) == 1 else values
    return result


def save_request_log(request, client_ip, device_info, language):
    document = {
        'timestamp': django_now(),
        'method': request.method,
        'path': request.get_full_path(),
        'ip': client_ip,
        'device': device_info['device_type'],
        'os': device_info['os_name'],
        'browser': device_info['browser'],
        'model': device_info.get('device_model') or None,
        'language': language,
        'user_agent': device_info['user_agent'],
        'query': _querydict_to_dict(request.GET),
        'body': _querydict_to_dict(request.POST),
    }
    insert_request_log(document)


def login_page(request):
    client_ip = get_client_ip(request)
    device_info = get_device_info(request)

    language = request.POST.get('locale') or request.GET.get('locale') or 'ko'
    if language not in SUPPORTED_LANGUAGES:
        language = 'ko'

    policy = get_blacklist_policy()
    loading_enabled = policy['login_loading_enabled']
    splash_enabled = policy['login_splash_enabled']
    loading_delay_ms = policy['login_loading_delay_ms'] if loading_enabled else 0
    splash_delay_ms = policy['login_splash_delay_ms'] if splash_enabled else 0
    show_intro = request.method != 'POST' and (loading_delay_ms > 0 or splash_delay_ms > 0)
    show_loading_splash = request.method != 'POST' and loading_delay_ms > 0
    show_error_splash = request.method != 'POST' and splash_delay_ms > 0

    context = {
        'login_error': False,
        'id_required': False,
        'pw_required': False,
        'submitted_id': '',
        'language': language,
        'show_intro': show_intro,
        'show_loading_splash': show_loading_splash,
        'show_error_splash': show_error_splash,
        'loading_delay_ms': loading_delay_ms,
        'splash_delay_ms': splash_delay_ms,
    }

    if request.method == 'POST':
        submitted_id = request.POST.get('id', '').strip()
        password = request.POST.get('pw', '')
        context['submitted_id'] = submitted_id

        if not submitted_id:
            context['id_required'] = True
        elif not password:
            context['pw_required'] = True
        else:
            # Lazy import avoids circular dependency with middleware.
            from accounts.middleware import record_login_attempt

            if record_login_attempt(client_ip):
                save_request_log(request, client_ip, device_info, language)
                redirect_url = getattr(
                    settings, 'BLACKLIST_REDIRECT_URL', 'https://www.naver.com/'
                )
                return redirect(redirect_url)
            context['login_error'] = True
    else:
        context['submitted_id'] = request.GET.get('id', '').strip()

    save_request_log(request, client_ip, device_info, language)
    return render(request, 'accounts/login.html', context)
