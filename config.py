"""
Flask config
"""
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Base config class
    """
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URL = os.environ['DATABASE_URL']
    CELERY_BROKER_URL = os.environ['CELERY_BROKER_URL']
    CELERY_BACKEND_URL = os.environ['CELERY_BACKEND_URL']


class ProductionConfig(Config):
    """
    Config for production
    """
    DEBUG = False


class StagingConfig(Config):
    """
    Staging config
    """
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    """
    Development config
    """
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    """
    Config for testing
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URL = os.environ['DATABASE_TEST_URL']
