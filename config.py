import os
from datetime import datetime

class Config:
    """Configuration class for the mental health prediction app"""
    
    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///mental_health.db')
    
    # Security configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', '60'))
    
    # Model configuration
    MODEL_PATH = 'mental_health_model_final.pkl'
    SCALER_PATH = 'scaler_final.pkl'
    LE_GENDER_PATH = 'le_gender_final.pkl'
    LE_TARGET_PATH = 'le_target_final.pkl'
    
    # Feature columns
    FEATURE_COLUMNS = ['Sentiment_Score', 'HRV', 'Sleep_Hours', 'Activity', 'Age', 'Gender', 'Work_Study_Hours']
    
    # Mental health status mapping
    HEALTH_STATUS_MAPPING = {0: "Low", 1: "Moderate", 2: "High"}
    
    # Crisis detection threshold
    CRISIS_THRESHOLD = 0.8  # If prediction confidence is above 80% for Low status
    
    # Professional guidance URLs
    CRISIS_HOTLINES = {
        'US': '988',
        'UK': '116 123',
        'CA': '1-833-456-4566',
        'AU': '13 11 14'
    }
