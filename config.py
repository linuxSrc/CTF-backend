import os
import secrets
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # PostgreSQL URL from Render
    SQLALCHEMY_DATABASE_URI = 'postgresql://admin:1EPkSVMTCkHepz9HaUwwL2glUXmFTrIK@dpg-csrgcp0gph6c73b5qt4g-a.oregon-postgres.render.com:5432/ctf_backend_db'
    
    # Handle Render's postgres:// URL format
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_size': 5,
        'max_overflow': 10,
        'pool_timeout': 30,
        'pool_recycle': 1800,
        'connect_args': {
            'sslmode': 'require',
            'connect_timeout': 10
        }
    }