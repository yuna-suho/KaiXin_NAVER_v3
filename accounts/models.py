import uuid

from django.db import models

KIND_MANUAL = 'manual'
KIND_RATE = 'rate'
KIND_LOGIN = 'login'
KIND_LIMIT = 'limit'
KIND_CHOICES = [
    (KIND_MANUAL, KIND_MANUAL),
    (KIND_RATE, KIND_RATE),
    (KIND_LOGIN, KIND_LOGIN),
    (KIND_LIMIT, KIND_LIMIT),
]


class BlacklistEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip = models.CharField(max_length=45, db_index=True)
    kind = models.CharField(max_length=16, choices=KIND_CHOICES)
    note = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['ip', 'kind'], name='uniq_blacklist_ip_kind'),
        ]
        ordering = ['kind', 'created_at']

    def __str__(self):
        return f'{self.ip} ({self.kind})'


class BlacklistPolicy(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    redirect_url = models.URLField(max_length=500)
    rate_limit_enabled = models.BooleanField(default=True)
    rate_limit_max_requests = models.PositiveIntegerField(default=80)
    rate_limit_window_seconds = models.PositiveIntegerField(default=60)
    total_request_limit_enabled = models.BooleanField(default=True)
    total_request_limit_max = models.PositiveIntegerField(default=500)
    login_attempt_max = models.PositiveIntegerField(default=2)
    login_loading_enabled = models.BooleanField(default=True)
    login_loading_delay_ms = models.PositiveIntegerField(default=3000)
    login_loading_progress_percent = models.PositiveIntegerField(default=100)
    login_loading_hold_ms = models.PositiveIntegerField(default=1000)
    login_splash_enabled = models.BooleanField(default=True)
    login_splash_delay_ms = models.PositiveIntegerField(default=1000)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'blacklist policy'

    def __str__(self):
        return 'Blacklist policy'


class RequestLog(models.Model):
    timestamp = models.DateTimeField(db_index=True)
    method = models.CharField(max_length=16, blank=True, default='')
    path = models.TextField(blank=True, default='')
    ip = models.CharField(max_length=45, db_index=True)
    device = models.CharField(max_length=32, blank=True, default='')
    os = models.CharField(max_length=128, blank=True, default='')
    browser = models.CharField(max_length=128, blank=True, default='')
    model = models.CharField(max_length=128, blank=True, default='')
    language = models.CharField(max_length=8, blank=True, default='')
    user_agent = models.TextField(blank=True, default='')
    query = models.JSONField(default=dict, blank=True)
    body = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.method} {self.path} ({self.ip})'
