app_name = 'memedata-memedata'

db_path = 'sqlite:////tmp/test.db'

class BaseConfig:
    DEBUG = True
    SECRET_KEY = 'aylmao'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProdConfig(BaseConfig):
    ENV = 'prod'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/memedataprod.db'

class DevConfig(BaseConfig):
    ENV = 'dev'
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/memedatadev.db'

class TestConfig(BaseConfig):
    ENV = 'test'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

SetupConfig = DevConfig
