SECRET_KEY = 'if879=^09&04tze)0i3$_6mv!z3_m1#mcivm^($t_wm878z*lx'

DEBUG = True
ALLOWED_HOSTS = ['www.dblfree.com', 'dblfree.com', '142.93.123.12', 'localhost', '127.0.0.1']

DATABASE = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'dblfree',
    'USER': 'dblfree_user',
    'PASSWORD': 'dblfree_pass',
    'HOST': 'localhost',
    'PORT': '',
}

HCAPTCHA_SITEKEY = '2e40bbfb-53a5-4880-9f29-24bfbe84620a'
HCAPTCHA_SECRET = '0x89eE40dB92eDf18A98960C937C5A69140740296E'

HYVOR_TALK_WEBSITE = 2204

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_HOST_USER = 'gabe@dblfree.com'
EMAIL_HOST_PASSWORD = 'SveIn9U6zWJA'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'DBL Free - No Reply <noreply@dblfree.com>'
CONTACT_EMAIL = 'gabe@dblfree.com'
