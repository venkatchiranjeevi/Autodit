"""
Django settings for Autodit project.

Generated by 'django-admin startproject' using Django 2.2.12.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'dmyyqr%y#w)&xg^q=9habzui1kiz^sgk^31hwrc#jk+)ve#o&a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

CORS_ORIGIN_ALLOW_ALL = True


CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'session',
    'version',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'AutoditApp',
    'rest_framework'

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'AutoditApp.middleware.AutoDitAuthenticationMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Autodit.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Autodit.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'PORT': '3306',
        'CONN_MAX_AGE': 3600,  # 1 Hour
        'NAME': 'AutoDit',

        'HOST': 'stageautodit.cqu0hotxmatf.ap-south-1.rds.amazonaws.com',
        'USER': 'admin',
        'PASSWORD': 'Auto!#%dit',
    },
    'default_sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

# AWS_ACCESS_KEY_ID = "AKIATZFC3A3LGLBZMAKV"
# REGION = "ap-south-1"
# AWS_SECRET_KEY = "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"
# COGNITO_USERPOOL_ID = "ap-south-1_rlvv48z1c"
# COGNITO_APP_CLIENT_ID = "7pltei3d7c1mv81janamqovij5"
# COGNITO_USERPOOL_KEYS = [
#         {
#             "alg": "RS256",
#             "e": "AQAB",
#             "kid": "ZVv/Zq0FnFl5fBdvk0iJOze00FGCZGmGfdS3uUEeppw=",
#             "kty": "RSA",
#             "n": "omwh6SPIIdycJwTvjHOzsgFV5jxO3FTGhgMS5sec2nr5EVA2-7CaT2vcAZPru-dSkjbnNWGYdxS6W3TmYwQxi4zBqdPCy1K-QXZ4RyZ-jk9kiIiwE_4O5zd5AQG8V_MV7cJ4k3L-dQOWHWwMlPvtNeklIP2e53RM49SmnMuPlvyPfRFos0r-W1Q5qa6Wstg68SvoJM91LJkLOcVnYD-lyYqd7BGB688KktPZek8mAB52k-oszTJIro4yGiiDVjcFAGsLIx5PTMCB0V9HwKC032Tl6YvuVsZu5-krTVyhhRBh6-QiAeBNFQKYsiyDzOkvuPVlxlfvFHxECKAlBFXEKQ",
#             "use": "sig"
#         },
#         {
#             "alg": "RS256",
#             "e": "AQAB",
#             "kid": "QZl1PQ8iuWjI0mcGUT9RVcrw+FGPzwNzCQSJ0LlTiwo=",
#             "kty": "RSA",
#             "n": "vYwIqjGmqeIHyRn3Z107_voUgBTWT2pTa_TjogAZtNzAAgt6CBjjkDh-XIqkRpcX05HBQdSds4ueuuBrtPIgX-wAx7yy83s9BX8JeZWZjqw3FsacNMFFcU6QCt0DogEVxFQj5jZRQ228YXe9MLAIa0FRGJpL7k6gptyHLr0p_kA22-d8Tfkat-nd6QsFbM1ZovkY-mitSm5TWZFbppd0JuP0OiLS6ZPKddHcx4Ic9GZkZB9H36DTyOrDr-wJ5f0B5Jo3g7Aa9jWH78t3U-yLU1ckuHLmJgSDUkPUoJlAdEcPgIJwfqxqPKRkLRf3cF8I61OUy5S8JwcUey2T0Pk8vQ",
#             "use": "sig"
#         }
#     ]

AWS_ACCESS_KEY_ID = "AKIA4ZPTTOVNQFGKEJVB"
REGION = "ap-south-1"
AWS_SECRET_KEY = "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"
COGNITO_USERPOOL_ID = "ap-south-1_jWp5ts5VP"
COGNITO_APP_CLIENT_ID = "1opbkfobdiumghmq3ujreia790"
COGNITO_USERPOOL_KEYS = [
        {
            "alg": "RS256",
            "e": "AQAB",
            "kid": "FY26XRl7f+fGGRhFEFq+m1HNz1Bo/JdTSy+EWPwuRBw=",
            "kty": "RSA",
            "n": "5E6H_tdbFjlnnt6LBpykbZ8wpRQBGsIqn-xludDcWNB7Uc9qsv4gW_BZJdXv0CBa3jYiDeO7Hax_iYOkcRgtI_1sZMlLGxa5w7S60Zho_z6wqemmI68ssScKdp9CKj1s6vtcbENZgtkHVO_fUVvhAlvzLMGLEGptyz4r57h4kWdPFkNrPMkGtP0rUjg_N06ldA_8D64qepTpCQjsEZ_dka5L0YOfoOAvViI_AiXBeiXHPPS0aceSpqng2LQ8sEZyZTFm3iosKcsBV14hjP4l0Lhc4a3tj3wGYN4x22lrlTgIkeTMvwaF1oe2hWqgpfLImJCA2IgLBOf_buBlQRhbdw",
            "use": "sig"
        },
        {
            "alg": "RS256",
            "e": "AQAB",
            "kid": "GhG2ksgE1/tAWdcZ781selAy2UlGS5W/M3TOlGBNijk=",
            "kty": "RSA",
            "n": "zFogGQvrCNp62Oq7zQSkbknx5A9su80usKUcjrSI3GgjP2J8OJioYPt2Tb1xX-lfctRMTTx0eLNuuX-O6Golfvz0GuH0phO8FtKdwoHk5GVVFonCprZgMZTlEjWF66bghl_PnG7Vp9ux6aRXiuYaiYm58PMLNj4Ih1id7SVqbcEpgNoYMioziDj0YjnMhJJwstVIWjsX097z4LJOEcwKqUv0nu7koGRThBYgW5X46i4r-cfBf_oMgS3hI5gxiyqlAd3cbL_yt7wQMrxp7rAN5N2RAjTg0zHM9byDcrVNPqzliuRCLNAwel8Z7yB810vbMF4GydzunPm-rciBwWhAFQ",
            "use": "sig"
        }
    ]
