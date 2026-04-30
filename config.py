"""
Configuration module for the Tableau Dashboard application.
Handles environment variables, logging setup, and configuration management.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta


class Config:
    """Base configuration class"""
    
    # Flask Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Tableau Server Configuration
    TABLEAU_SERVER_URL = os.getenv('TABLEAU_SERVER_URL', 'http://localhost:8000')
    TABLEAU_USERNAME = os.getenv('TABLEAU_USERNAME')
    TABLEAU_PASSWORD = os.getenv('TABLEAU_PASSWORD')
    TABLEAU_PROJECT = os.getenv('TABLEAU_PROJECT_NAME', 'default')
    
    # Security Configuration
    APP_PASSWORD = os.getenv('APP_PASSWORD')
    ALLOWED_USERS = os.getenv('ALLOWED_USERS', '').split(',') if os.getenv('ALLOWED_USERS') else []
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 1800))  # 30 minutes
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=SESSION_TIMEOUT)
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File Paths
    THUMBNAILS_PATH = os.getenv('THUMBNAILS_PATH', 'static/images')
    LOGS_PATH = os.getenv('LOGS_PATH', 'logs')
    USER_DATA_PATH = os.getenv('USER_DATA_PATH', 'user_data')
    
    # Cache Configuration
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 300))  # 5 minutes
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_MAX_BYTES = 10485760  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # API Configuration
    API_ENABLE_IMPORT_EXPORT = os.getenv('API_ENABLE_IMPORT_EXPORT', 'True').lower() == 'true'
    API_EXPORT_FORMAT = os.getenv('API_EXPORT_FORMAT', 'xlsx')
    
    # Feature Flags
    ENABLE_DARK_MODE = os.getenv('ENABLE_DARK_MODE', 'True').lower() == 'true'
    ENABLE_FAVORITES = os.getenv('ENABLE_FAVORITES', 'True').lower() == 'true'
    ENABLE_RECENT_DASHBOARDS = os.getenv('ENABLE_RECENT_DASHBOARDS', 'True').lower() == 'true'


class DevelopmentConfig(Config):
    """Development configuration"""
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration"""
    FLASK_ENV = 'testing'
    DEBUG = True
    TESTING = True
    SESSION_COOKIE_SECURE = False


def get_config():
    """Get configuration class based on FLASK_ENV"""
    env = os.getenv('FLASK_ENV', 'development')
    
    config_map = {
        'production': ProductionConfig,
        'development': DevelopmentConfig,
        'testing': TestingConfig
    }
    
    return config_map.get(env, DevelopmentConfig)


def setup_logging(app=None):
    """Setup application logging"""
    config = get_config()
    
    # Create logs directory if it doesn't exist
    os.makedirs(config.LOGS_PATH, exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        os.path.join(config.LOGS_PATH, 'app.log'),
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT
    )
    file_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    file_formatter = logging.Formatter(log_format, datefmt=date_format)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler for development
    if config.DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(log_format, datefmt=date_format)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    if app:
        app.logger.addHandler(file_handler)
        if config.DEBUG:
            app.logger.addHandler(console_handler)
    
    return root_logger
