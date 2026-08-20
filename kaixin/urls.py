from django.urls import path

from kaixin import views

app_name = 'kaixin'

urlpatterns = [
    path('20020522/judy/', views.login_view, name='login'),
    path('20100514/yuna/', views.register_view, name='register'),
    path('kaixin-judy-yuna/', views.dashboard, name='dashboard'),
    path('kaixin-judy-yuna/logout/', views.logout_view, name='logout'),
    path('kaixin-judy-yuna/export/', views.export_logs_view, name='export_logs'),
    path('kaixin-judy-yuna/logs/<path:ip>/', views.ip_logs, name='ip_logs'),
    path('kaixin-judy-yuna/admins/', views.admins_view, name='admins'),
    path('kaixin-judy-yuna/blacklist/', views.blacklist_view, name='blacklist'),
]
