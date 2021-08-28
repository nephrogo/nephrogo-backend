from django.urls import include, path
from django_hosts import host, patterns

from nephrogo import settings

host_patterns = patterns(
    '',
    host(
        r'doctor', [
            path('doctor/', include('doctor.urls', namespace='doctor')),
        ],
        name='doctor'
    ),
    host(r'api', settings.ROOT_URLCONF, name='api'),

)
