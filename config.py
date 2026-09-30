import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


def _resolve_database_path():
    """Pick DB path based on environment."""
    # 1. Explicit env var wins
    env_path = os.getenv('DATABASE_PATH')
    if env_path:
        return env_path
    # 2. Render detection (Render sets RENDER=true)
    if os.getenv('RENDER') == 'true':
        return '/var/data/swachh_seva.db'
    # 3. Local default
    return 'database/swachh_seva.db'


def _resolve_upload_folder():
    """Pick upload folder based on environment."""
    env_path = os.getenv('UPLOAD_FOLDER')
    if env_path:
        return env_path
    if os.getenv('RENDER') == 'true':
        return '/var/data/uploads'
    return 'uploads'


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-me')

    # Database & uploads
    DATABASE_PATH = _resolve_database_path()
    UPLOAD_FOLDER = _resolve_upload_folder()

    # Groq AI
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b')

    # File uploads
    MAX_UPLOAD_SIZE_MB = int(os.getenv('MAX_UPLOAD_SIZE_MB', '5'))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # CORS
    CORS_ORIGINS = [
        o.strip() for o in os.getenv(
            'CORS_ORIGINS',
            'http://127.0.0.1:5000,http://localhost:5000'
        ).split(',') if o.strip()
    ]

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'

    # File upload validation
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
    ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}

    # Business defaults (overridable via system_settings table)
    DEFAULT_REPORT_REWARD = 5
    DEFAULT_PICKUP_REWARD = 3
    DEFAULT_PAGE_SIZE = 20


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = 'database/test_swachh_seva.db'


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}


def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    return config_map.get(env, DevelopmentConfig)