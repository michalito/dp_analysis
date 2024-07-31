# app/config.py
import os

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')
    # Add other common configurations

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    # Add other production-specific configurations

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
