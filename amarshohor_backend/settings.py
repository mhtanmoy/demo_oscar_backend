"""
Django settings for amarshohor_backend project.

Generated by 'django-admin startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
from oscar.defaults import *
from pathlib import Path
from decouple import config, Csv
import os
import environ
from datetime import timedelta

env = environ.Env()


# For Django Oscar


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = ["*"]


# Application definition

# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
# ]
THIRD_PARTY_LIBRARY_APPS = [
    # 'channels',
    "drf_yasg2",
    "rest_framework",
    "oscar_invoices",
    "django_filters",
]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.flatpages",
    "django_extensions",
    "oscar.config.Shop",
    "oscar.apps.analytics.apps.AnalyticsConfig",
    # 'oscar.apps.checkout.apps.CheckoutConfig',
    "apps.checkout.apps.CheckoutConfig",
    "oscar.apps.address.apps.AddressConfig",
    "oscar.apps.shipping.apps.ShippingConfig",
    # 'oscar.apps.catalogue.apps.CatalogueConfig',
    "apps.catalogue.apps.CatalogueConfig",
    "oscar.apps.catalogue.reviews.apps.CatalogueReviewsConfig",
    "oscar.apps.communication.apps.CommunicationConfig",
    # 'oscar.apps.partner.apps.PartnerConfig',
    "apps.partner.apps.PartnerConfig",
    "oscar.apps.basket.apps.BasketConfig",
    "oscar.apps.payment.apps.PaymentConfig",
    "oscar.apps.offer.apps.OfferConfig",
    # 'oscar.apps.order.apps.OrderConfig',
    "apps.order.apps.OrderConfig",
    "apps.customer.apps.CustomerConfig",
    "oscar.apps.search.apps.SearchConfig",
    "oscar.apps.voucher.apps.VoucherConfig",
    # 'oscar.apps.wishlists.apps.WishlistsConfig',
    'apps.wishlists.apps.WishlistsConfig',
    # 'oscar.apps.dashboard.apps.DashboardConfig',
    'apps.dashboard.apps.DashboardConfig',
    'oscar.apps.dashboard.reports.apps.ReportsDashboardConfig',
    'oscar.apps.dashboard.users.apps.UsersDashboardConfig',
    'oscar.apps.dashboard.orders.apps.OrdersDashboardConfig',
    'oscar.apps.dashboard.catalogue.apps.CatalogueDashboardConfig',
    'oscar.apps.dashboard.offers.apps.OffersDashboardConfig',
    'oscar.apps.dashboard.partners.apps.PartnersDashboardConfig',
    'oscar.apps.dashboard.pages.apps.PagesDashboardConfig',
    'oscar.apps.dashboard.ranges.apps.RangesDashboardConfig',
    'oscar.apps.dashboard.reviews.apps.ReviewsDashboardConfig',
    'oscar.apps.dashboard.vouchers.apps.VouchersDashboardConfig',
    'oscar.apps.dashboard.communications.apps.CommunicationsDashboardConfig',
    'oscar.apps.dashboard.shipping.apps.ShippingDashboardConfig',

    'oscarapi',

    # 3rd-party apps that oscar depends on
    'widget_tweaks',
    'haystack',
    'treebeard',
    'sorl.thumbnail',   # Default thumbnail backend, can be replaced
    'django_tables2',

    # 'apps.extension.apps.ExtensionConfig',
    # 'oscar.apps.customer.apps.CustomerConfig'

    # # Django Oscar Promotions Lib
    # 'oscar_promotions.apps.PromotionsConfig',
    # 'oscar_promotions.dashboard.apps.PromotionsDashboardConfig',

    # custom auth
    "authentications",
    "corsheaders",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # 'allauth.socialaccount.providers.apple',
    # 'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.facebook',

    # oscar invoices
    # 'oscar_invoices',
    #stores
    # "stores",
    # "stores.dashboard",


    # oscar accounts
    "oscar_accounts.apps.AccountsConfig",
    "oscar_accounts.dashboard.apps.AccountsDashboardConfig",
    "customapp",
    "accounts",
    # geoDjango
    "django.contrib.gis",
] + THIRD_PARTY_LIBRARY_APPS

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": ("utils.response_wrapper.CustomRenderer",),
    # "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_PAGINATION_CLASS": "utils.custom_pagination.CustomPagination",
    # "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"]
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # OSCAR
    "oscar.apps.basket.middleware.BasketMiddleware",
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
    # 'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = "amarshohor_backend.urls"

AUTHENTICATION_BACKENDS = (
    "oscar.apps.customer.auth_backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # OSCAR
                "oscar.apps.search.context_processors.search_form",
                "oscar.apps.checkout.context_processors.checkout",
                "oscar.apps.communication.notifications.context_processors.notifications",
                "oscar.core.context_processors.metadata",
            ],
        },
    },
]


# Provider specific settings
# SOCIALACCOUNT_PROVIDERS = {
#     'google': {
#         # For each OAuth based provider, either add a ``SocialApp``
#         # (``socialaccount`` app) containing the required client
#         # credentials, or list them here:
#         'APP': {
#             'client_id': '123',
#             'secret': '456',
#             'key': ''
#         }
#     }
# }

WSGI_APPLICATION = "amarshohor_backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         # 'ENGINE': 'django.db.backends.sqlite3',
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


DATABASES = {
    "default": {
        # 'ENGINE': 'django.db.backends.postgresql',
        #'ENGINE': 'django.db.backends.postgresql_psycopg2',
        "ENGINE": "django.contrib.gis.db.backends.postgis",
         "NAME": config("DB_NAME"),
        #"NAME": 'amarshohor_staging_db',
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Dhaka"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"


MEDIA_URL = "/media/"

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join("static_cdn", "static_root")
MEDIA_ROOT = os.path.join("static_cdn", "media_root")


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


SITE_ID = 1

GOOGLE_MAPS_API_KEY = ""
STORES_GEOGRAPHIC_SRID = 3577
STORES_GEODETIC_SRID = 4326
STORES_MAX_SEARCH_DISTANCE = None


# OSCAR

# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
#     },
# }


GRAPH_MODELS = {
    "all_applications": True,
    "group_models": True,
}

# oscar accounts settings
OSCAR_DASHBOARD_NAVIGATION.append(
    {
        "label": "Accounts",
        "icon": "fas fa-globe",
        "children": [
            {
                "label": "Accounts",
                "url_name": "accounts_dashboard:accounts-list",
            },
            {
                "label": "Transfers",
                "url_name": "accounts_dashboard:transfers-list",
            },
            {
                "label": "Deferred income report",
                "url_name": "accounts_dashboard:report-deferred-income",
            },
            {
                "label": "Profit/loss report",
                "url_name": "accounts_dashboard:report-profit-loss",
            },
        ],
    }
)


# OSCAR PAGINATION

# OSCAR_PRODUCTS_PER_PAGE = 20

# OSCAR_OFFERS_PER_PAGE = 20

# OSCAR_REVIEWS_PER_PAGE = 20

# OSCAR_NOTIFICATIONS_PER_PAGE = 20

# OSCAR_EMAILS_PER_PAGE = 20

# OSCAR_ORDERS_PER_PAGE = 20

# OSCAR_ADDRESSES_PER_PAGE = 20

# OSCAR_STOCK_ALERTS_PER_PAGE = 20

# OSCAR_DASHBOARD_ITEMS_PER_PAGE = 20

# FCM Setup


FCM_DJANGO_SETTINGS = {
    # "FCM_SERVER_KEY": env.str("FCM_SERVER_KEY"),
    "FCM_SERVER_KEY": config("FCM_SERVER_KEY"),
    "ONE_DEVICE_PER_USER": False,
    "DELETE_INACTIVE_DEVICES": True,
}

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header"
        }
    },
    "JSON_EDITOR": True,
}

OSCAR_DEFAULT_CURRENCY = "৳"


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = "587"
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True

OSCAR_INITIAL_LINE_STATUS = "Initialized"

OSCAR_LINE_STATUS_PIPELINE = {
    "Initialized": (
        "Pending",
        "Cancelled",
    ),
    "Pending": (
        "Placed",
        "Cancelled",
    ),
    "Placed": (
        "Confirm",
        "Canceled",
    ),
    "Confirm": (
        "Picked",
        "Cancelled",
    ),
    "Picked": (
        "On the Way",
        "Cancelled",
    ),
    "On the Way": (),
    "unavailable": (),
    "Delivered": (),
    "Cancelled": (),
    "Returned": (),
}
OSCAR_INITIAL_ORDER_STATUS = "Initialized"

OSCAR_ORDER_STATUS_PIPELINE = {
    # Payment Pending
    "Initialized": (
        "Pending",
        "Cancelled",
    ),
    "Pending": (
        "Placed",
        "Cancelled",
    ),
    "Placed": (
        "Confirm",
        "Canceled",
    ),
    "Confirm": (
        "Picked",
        "Cancelled",
    ),
    "Picked": (
        "On the Way",
        "Cancelled",
    ),
    "On the Way": (),
    "unavailable": (),
    "Delivered": (),
    "Cancelled": (),
    "Returned": (),
}

OSCAR_INITIAL_ORDER_STATUS = "Initialized"
OSCAR_ORDER_STATUS_PIPELINE = {
    "Initialized": (
        "Pending",
        "Cancelled",
    ),
    "Pending": (
        "Confirm",
        "Cancelled",
    ),
    "Confirm": (
        "Picked",
        "Cancelled",
    ),
    "Picked": (
        "On the Way",
        "Cancelled",
    ),
    "On the Way": (),
    "unavailable": (),
    "Delivered": (),
    "Cancelled": (),
    "Returned": (),
}

OSCAR_ORDER_STATUS_CASCADE = {
    "Pending": (
        "Confirm",
        "Cancelled",
    ),
    "Confirm": (
        "Picked",
        "Cancelled",
    ),
    "Picked": (
        "On the Way",
        "Cancelled",
    ),
    "On the Way": ("On the Way"),
    "unavailable": ("unavailable"),
    "Delivered": ("Delivered"),
    "Cancelled": ("Cancelled"),
    "Returned": ("Returned"),
}

AUTH_USER_MODEL = "accounts.UserAccount"

# solr with haystack

HAYSTACK_CONNECTIONS = {
    "default": {
        #         "ENGINE": "haystack.backends.elasticsearch7_backend.Elasticsearch7SearchEngine",
        #         "URL": "http://es-container:9200/",
        #         "INDEX_NAME": "haystack"
    }
}

HAYSTACK_SIGNAL_PROCESSOR = "haystack.signals.RealtimeSignalProcessor"


# celery settings
CELERY_BROKER_URL = config("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Dhaka"


CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOW_METHODS = [
#     'DELETE',
#     'GET',
#     'OPTIONS',
#     'PATCH',
#     'POST',
#     'PUT',
# ]
# CORS_ALLOW_HEADERS = [
#     'accept',
#     'accept-encoding',
#     'authorization',
#     'content-type',
#     'dnt',
#     'origin',
#     'user-agent',
#     'x-csrftoken',
#     'x-requested-with',
# 

# os.environ['PATH'] = os.path.join(BASE_DIR, 'venv\Lib\site-packages\osgeo') + ';' + os.environ['PATH']
# os.environ['PROJ_LIB'] = os.path.join(BASE_DIR, 'venv\Lib\site-packages\osgeo\data\proj') + ';' + os.environ['PATH']
# GDAL_LIBRARY_PATH = os.path.join(BASE_DIR, 'venv\Lib\site-packages\osgeo\gdal304.dll')

############################## MINIO ########################
# STATIC_ROOT = 'static'
# MEDIA_ROOT = 'media'
# STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
# DEFAULT_FILE_STORAGE = "utils.storage_backends.MediaStorage"
# AWS_S3_ACCESS_KEY_ID = "VLpvIQD2VqNDnTXM"
# AWS_S3_SECRET_ACCESS_KEY = "VLpvIQD2VqNDnTXM"
# AWS_STORAGE_BUCKET_NAME = "dev"
# AWS_DEFAULT_ACL = "public-read"
# AWS_S3_CUSTOM_DOMAIN = '127.0.0.1:9000'+'/'+AWS_STORAGE_BUCKET_NAME
# AWS_LOCATION = 'static'
# STATIC_URL = "http://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
# MEDIA_URL = "http://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, 'media')
# AWS_S3_ENDPOINT_URL="http://s3:9000"
# AWS_S3_URL_PROTOCOL = "http:"

######################### AWS S3 ###############################

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_DEFAULT_ACL = "public-read"
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
# s3 static settings
STATIC_LOCATION = 'static'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
# s3 public media settings
PUBLIC_MEDIA_LOCATION = 'media'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
DEFAULT_FILE_STORAGE = 'utils.storage_backends.MediaStorage'
# s3 private media settings
# PRIVATE_MEDIA_LOCATION = 'private'
# PRIVATE_FILE_STORAGE = 'utils.storage_backends.MediaStorage'