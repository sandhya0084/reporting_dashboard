import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dashboard.db'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('sandhyachirumamilla6@gmail.com')
    MAIL_PASSWORD = os.environ.get('wzhs otqk iqfy bznp')
    ADMINS = ['admin@example.com']

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}