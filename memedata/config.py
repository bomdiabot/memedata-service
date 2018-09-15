import os

app_name = 'memedata'

env = os.environ.get('MEMEDATA_ENV', 'development')
assert env in {'development', 'production'}

def _is_dev():
    return env == 'development'

def _is_prod():
    return env == 'production'

def _get_var(key, default=None, conf=os.environ):
    if not _is_dev() and not key in conf:
        raise ValueError('var {} should be in env for production'.format(key))
    return conf.get(key, default)

debug = _is_dev()

#ignore auth requirements
#NEVER user it in prod or during tests
ignore_jwt_texts = (not True) if _is_dev() else False
ignore_jwt_images = (not True) if _is_dev() else False
ignore_jwt_auth = (not True) if _is_dev() else False

min_password_len = 8

superusers = {
    'su',
}

class BaseAppConfig:
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    SQLALCHEMY_TRACK_MODIFICATIONS = False

def get_app_config_class(**override_environ):
    conf = os.environ.copy()
    conf.update(**override_environ)
    class AppConfig(BaseAppConfig):
        environ = env
        DEBUG = is_dev()
        TESTING = False
        SECRET_KEY = _get_var(
            'MEMEDATA_SECRET_KEY', 'secret', conf)
        JWT_SECRET_KEY = _get_var(
            'MEMEDATA_JWT_SECRET_KEY', 'jwtsecret', conf)
        SQLALCHEMY_DATABASE_URI = _get_var(
            'MEMEDATA_DB_PATH', 'sqlite:////tmp/memedatadev.db', conf)
        SQLALCHEMY_TRACK_MODIFICATIONS = _is_prod()
    return AppConfig

def get_app_test_config_class(**override_environ):
    conf = os.environ.copy()
    conf.update(**override_environ)
    class AppTestConfig(BaseAppConfig):
        environ = 'test'
        DEBUG = True
        TESTING = True
        SECRET_KEY = 'secret'
        JWT_SECRET_KEY = 'jwtsecret'
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            'MEMEDATA_TEST_DB_PATH', 'sqlite://')
    return AppTestConfig
