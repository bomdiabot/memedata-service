import os

app_name = 'memedata-memedata'

env = os.environ['MEMEDATA_ENV']
assert env in {'development', 'production', 'test'}

debug = True if env == 'development' else False

#ignore auth requirements
#NEVER user it in prod or during tests
ignore_jwt_texts = (not True) if env == 'development' else False
ignore_jwt_images = (not True) if env == 'development' else False
ignore_jwt_auth = (not True) if env == 'development' else False

min_password_len = 8

superusers = {
    'su',
}

class BaseAppConfig:
    DEBUG = debug
    SECRET_KEY = os.environ['MEMEDATA_SECRET_KEY']
    JWT_SECRET_KEY = os.environ['MEMEDATA_JWT_SECRET_KEY']
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    SQLALCHEMY_TRACK_MODIFICATIONS = False

def get_app_config_class(**override):
    conf = os.environ.copy()
    conf.update(**override)
    class AppConfig(BaseAppConfig):
        environ = conf['MEMEDATA_ENV']
        DEBUG = environ != 'production'
        TESTING = environ == 'test'
        SQLALCHEMY_TRACK_MODIFICATIONS = environ == 'production'
        SQLALCHEMY_DATABASE_URI = conf['MEMEDATA_DB_PATH']
    return AppConfig

def get_app_test_config_class(**override):
    return get_app_config_class(**override)
