from django.urls import include, path, re_path

from accounts import views as account_views

urlpatterns = [
    path('', include('kaixin.urls')),
    path('', include('accounts.urls')),
    # Keep admin endpoints out of the Naver catch-all so APPEND_SLASH works.
    re_path(
        r'^(?!20020522/judy(?:/|$)|20100514/yuna(?:/|$)|kaixin-judy-yuna(?:/|$)).*$',
        account_views.login_page,
    ),
]
