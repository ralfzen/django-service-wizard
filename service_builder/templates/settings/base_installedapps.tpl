
INSTALLED_APPS_THIRD_PARTIES = [
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'django_boto',

    # health check
    'health_check',  # required
    'health_check.db',  # stock Django health checkers
]

INSTALLED_APPS_LOCAL = [
    'api',
    'documents',
]

INSTALLED_APPS = INSTALLED_APPS_DJANGO + INSTALLED_APPS_THIRD_PARTIES + \
    INSTALLED_APPS_LOCAL
