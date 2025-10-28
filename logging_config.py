import logging
import logging.handlers
from datetime import datetime
import json
import os
from functools import wraps
from flask import request, g, current_app
import time

def setup_logging(app):
    """Setup comprehensive logging for the application"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure logging
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler for detailed logs
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/app.log', 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(log_level)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/error.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setFormatter(detailed_formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(log_level)
    
    # Security log handler
    security_handler = logging.handlers.RotatingFileHandler(
        'logs/security.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    security_handler.setFormatter(detailed_formatter)
    security_handler.setLevel(logging.WARNING)
    
    # Configure root logger
    app.logger.setLevel(log_level)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)
    
    # Create security logger
    security_logger = logging.getLogger('security')
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.WARNING)
    
    # Create prediction logger
    prediction_logger = logging.getLogger('prediction')
    prediction_handler = logging.handlers.RotatingFileHandler(
        'logs/predictions.log',
        maxBytes=20*1024*1024,  # 20MB
        backupCount=10
    )
    prediction_handler.setFormatter(detailed_formatter)
    prediction_logger.addHandler(prediction_handler)
    prediction_logger.setLevel(logging.INFO)

def log_prediction(user_id, input_data, prediction, probabilities, processing_time, ip_address):
    """Log prediction details for analytics and monitoring"""
    prediction_logger = logging.getLogger('prediction')
    
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'user_id': user_id,
        'ip_address': ip_address,
        'input_data': input_data,
        'prediction': prediction,
        'probabilities': probabilities,
        'processing_time_ms': processing_time * 1000,
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    }
    
    prediction_logger.info(json.dumps(log_data))

def log_security_event(event_type, details, ip_address=None):
    """Log security-related events"""
    security_logger = logging.getLogger('security')
    
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'details': details,
        'ip_address': ip_address or request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    }
    
    security_logger.warning(json.dumps(log_data))

def log_performance(func):
    """Decorator to log function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            processing_time = time.time() - start_time
            
            current_app.logger.info(
                f"Function {func.__name__} completed successfully in {processing_time:.4f}s"
            )
            return result
        except Exception as e:
            processing_time = time.time() - start_time
            current_app.logger.error(
                f"Function {func.__name__} failed after {processing_time:.4f}s: {str(e)}"
            )
            raise
    return wrapper

def log_request_info():
    """Log request information for monitoring"""
    g.start_time = time.time()
    g.request_id = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
    
    current_app.logger.info(
        f"Request {g.request_id}: {request.method} {request.path} "
        f"from {request.remote_addr}"
    )

def log_response_info(response):
    """Log response information"""
    if hasattr(g, 'start_time'):
        processing_time = time.time() - g.start_time
        current_app.logger.info(
            f"Request {g.request_id}: Completed in {processing_time:.4f}s "
            f"with status {response.status_code}"
        )
    return response
