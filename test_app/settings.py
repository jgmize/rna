DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db',
    }
}

USE_TZ = False
SITE_ID = 1
SECRET_KEY = 'gxxg@@juj%4=-jr5ohv3cdj6)v6p2j5e3q91naw#m&amp;&amp;dgzq-zh'

ROOT_URLCONF = 'test_app.urls'
STATIC_URL = '/static/'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'south',
    'django_nose',  # must come after south b/c south overrides test runner
    'rest_framework',
    'rest_framework.authtoken',
    'rna',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ('--nocapture', )
SOUTH_TESTS_MIGRATE = False

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS': (
        'rna.rna.serializers.HyperlinkedModelSerializerWithPkField'),

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ),

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),

    'DEFAULT_FILTER_BACKENDS': ('rna.rna.filters.TimestampedFilterBackend',)
}

RNA = {
    'BASE_URL': 'https://nucleus.paas.allizom.org/rna/',
    'LEGACY_API': False,
}
