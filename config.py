import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dashboard.db'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    # Read credentials from environment in production. Use sensible env var names.
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['admin@example.com']

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}