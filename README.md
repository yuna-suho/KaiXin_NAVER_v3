# KaiXin NAVER v3

Django 기반 프로젝트입니다. 방문자용 네이버 스타일 로그인 페이지(`accounts`)와 관리자 콘솔(`kaixin`)이 분리되어 있습니다.

## 요구 사항

- Python 3.10+
- Django 6.x (`requirements.txt` 참고)

## 설치

```bash
pip install -r requirements.txt
python manage.py migrate
```

데이터는 Django 표준 **SQLite**(`db.sqlite3`)에 저장됩니다.

## 실행

```bash
python manage.py runserver
# 외부 접속 허용
python manage.py runserver 0.0.0.0:8000
```
기본 주소: `http://127.0.0.1:8000/`

## 엔드포인트

### 방문자 (`accounts`)

| 경로 | 설명 |
|------|------|
| `/` 및 그 외 미등록 경로 | 네이버 스타일 로그인 페이지 |

- GET/POST 요청은 SQLite `accounts_requestlog` 테이블에 기록됩니다.
- URL 쿼리 `?id=아이디`로 아이디 입력칸을 미리 채울 수 있습니다. 파라미터가 없으면 빈 상태입니다.
- 접속 시 **로딩 페이지 → 네트워크 오류 안내 페이지 → 로그인 페이지** 순으로 전환됩니다.
- OS/브라우저 다크 모드(`prefers-color-scheme: dark`)에 맞춰 라이트/다크 테마가 자동 적용됩니다.

**예시**

```
http://127.0.0.1:8000/?id=myuser
http://127.0.0.1:8000/?id=myuser&locale=en
```

### 관리자 (`kaixin`)

| 경로 | 설명 |
|------|------|
| `/20020522/judy/` | Sign In |
| `/20100514/yuna/` | Sign Up |
| `/kaixin-judy-yuna/` | 대시보드 (IP별 요청 기록) |
| `/kaixin-judy-yuna/export/` | 요청 로그 JSON export (전체 또는 IP·기간 필터) |
| `/kaixin-judy-yuna/logs/<ip>/` | 해당 IP 요청 상세 |
| `/kaixin-judy-yuna/admins/` | 관리자 승인 (최고관리자만) |
| `/kaixin-judy-yuna/blacklist/` | IP 블랙리스트 · Auto-block Policy |
| `/kaixin-judy-yuna/logout/` | Sign Out |

관리자 UI 문구는 영문입니다.

## 관리자 권한

1. **첫 가입자** → 최고관리자(superadmin), 즉시 승인
2. **이후 가입자** → 승인 대기. Sign In 시 안내 메시지 표시
3. 최고관리자가 `/kaixin-judy-yuna/admins/` 에서 승인·철회·삭제

Django `createsuperuser` / `django.contrib.auth` User 모델은 사용하지 않습니다. 관리자 계정은 `kaixin_adminuser` 테이블에 저장됩니다.

## 데이터베이스 (SQLite)

| 테이블 | 용도 |
|--------|------|
| `accounts_requestlog` | 방문자 요청 로그 |
| `accounts_blacklistentry` | IP 블랙리스트 |
| `accounts_blacklistpolicy` | 자동 차단 정책 (단일 행) |
| `kaixin_adminuser` | 관리자 계정 |

DB 파일 경로: 프로젝트 루트 `db.sqlite3` (`config/settings.py` → `DATABASES`)

## IP 차단

차단 IP는 `/kaixin-judy-yuna/blacklist/` 에서 추가·삭제합니다.

자동 차단 조건(rate / total / login, redirect URL, 로그인 스플래시 시간)도 같은 페이지의 **Auto-block Policy**에서 변경할 수 있습니다.

| kind | 설명 |
|------|------|
| `manual` | 수동 차단 |
| `rate` | 짧은 시간 과다 요청 시 자동 등록 |
| `limit` | IP별 누적 요청 한도 초과 시 자동 등록 |
| `login` | 로그인 시도 한도 초과 시 자동 등록 |

차단된 IP는 policy의 redirect URL(기본: 네이버)로 리다이렉트됩니다.

- 관리자 경로(`/20020522/judy`, `/20100514/yuna`, `/kaixin-judy-yuna`)는 차단 대상에서 제외됩니다.
- 로컬 주소(`127.0.0.1`, `::1`)는 자동·수동 차단 모두 비활성화됩니다.

## 설정

`config/settings.py`에 기본값이 정의되어 있으며, **Auto-block Policy** UI에서 변경한 값은 SQLite `accounts_blacklistpolicy`에 저장됩니다.

| 항목 | settings.py 기본값 | UI 변경 |
|------|-------------------|---------|
| `BLACKLIST_REDIRECT_URL` | `https://www.naver.com/` | O |
| `RATE_LIMIT_ENABLED` | `True` | O |
| `RATE_LIMIT_MAX_REQUESTS` | `80` | O |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | O |
| `TOTAL_REQUEST_LIMIT_ENABLED` | `True` | O |
| `TOTAL_REQUEST_LIMIT_MAX` | `500` | O |
| `LOGIN_ATTEMPT_MAX` | `2` | O |
| `LOGIN_LOADING_ENABLED` | `True` | O |
| `LOGIN_LOADING_DELAY_MS` | `3000` | O |
| `LOGIN_SPLASH_ENABLED` | `True` | O |
| `LOGIN_SPLASH_DELAY_MS` | `1000` | O |

`LOGIN_LOADING_ENABLED` / `LOGIN_SPLASH_ENABLED`로 로딩·네트워크 오류 페이지 표시 여부를 켜거나 끌 수 있습니다.

`LOGIN_LOADING_DELAY_MS`는 로딩 스피너 페이지 표시 시간(밀리초)입니다. `0`이면 해당 단계를 건너뜁니다.

`LOGIN_SPLASH_DELAY_MS`는 네트워크 오류 페이지 표시 시간(밀리초)입니다. `0`이면 해당 단계를 건너뜁니다.

## 프로젝트 구조

```
├── accounts/              # 방문자 로그인 · IP 미들웨어 · SQLite 모델
│   ├── models.py          # RequestLog, BlacklistEntry, BlacklistPolicy
│   ├── templates/         # login.html, network_error_splash.html
│   └── static/            # 로그인 CSS/JS, 스프라이트
├── kaixin/                # 관리자 인증 · 대시보드 · 승인
│   └── models.py          # AdminUser
├── config/                # Django 설정 · URL
├── db.sqlite3             # SQLite DB (migrate 후 생성, gitignore)
├── manage.py
└── requirements.txt
```
