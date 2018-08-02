
INSTALLED_APPS_THIRD_PARTIES = [
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',

    # Health check
    'health_check',
    'health_check.db',
]

INSTALLED_APPS_LOCAL = [
    '{{ name_app }}',
]

INSTALLED_APPS = INSTALLED_APPS_DJANGO + INSTALLED_APPS_THIRD_PARTIES + \
    INSTALLED_APPS_LOCAL
