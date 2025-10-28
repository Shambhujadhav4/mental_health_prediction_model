from flask import jsonify, request
import traceback
from datetime import datetime
import logging
from config import Config

class MentalHealthError(Exception):
    """Base exception for mental health prediction errors"""
    def __init__(self, message, error_code=None, user_message=None):
        self.message = message
        self.error_code = error_code
        self.user_message = user_message or message
        super().__init__(self.message)

class ValidationError(MentalHealthError):
    """Raised when input validation fails"""
    def __init__(self, field, value, message):
        self.field = field
        self.value = value
        super().__init__(
            f"Validation error for {field}: {message}",
            error_code="VALIDATION_ERROR",
            user_message=f"Invalid {field}: {message}"
        )

class ModelError(MentalHealthError):
    """Raised when model prediction fails"""
    def __init__(self, message):
        super().__init__(
            message,
            error_code="MODEL_ERROR",
            user_message="Unable to process your request. Please try again."
        )

class CrisisDetectionError(MentalHealthError):
    """Raised when crisis detection is triggered"""
    def __init__(self, message):
        super().__init__(
            message,
            error_code="CRISIS_DETECTED",
            user_message="Please seek immediate professional help. Contact emergency services or a mental health professional."
        )

def validate_input_data(data):
    """Comprehensive input validation"""
    errors = []
    
    # Required fields check
    required_fields = Config.FEATURE_COLUMNS
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
            continue
            
        value = data[field]
        
        # Type and range validation
        if field == 'Sentiment_Score':
            try:
                val = float(value)
                if not (0 <= val <= 1):
                    errors.append(f"Sentiment_Score must be between 0 and 1, got {val}")
            except (ValueError, TypeError):
                errors.append(f"Sentiment_Score must be a number, got {type(value).__name__}")
                
        elif field == 'HRV':
            try:
                val = float(value)
                if val < 0:
                    errors.append(f"HRV cannot be negative, got {val}")
                elif val > 200:  # Reasonable upper bound
                    errors.append(f"HRV seems unusually high ({val}), please verify")
            except (ValueError, TypeError):
                errors.append(f"HRV must be a number, got {type(value).__name__}")
                
        elif field == 'Sleep_Hours':
            try:
                val = float(value)
                if val < 0:
                    errors.append(f"Sleep_Hours cannot be negative, got {val}")
                elif val > 24:
                    errors.append(f"Sleep_Hours cannot exceed 24, got {val}")
            except (ValueError, TypeError):
                errors.append(f"Sleep_Hours must be a number, got {type(value).__name__}")
                
        elif field == 'Activity':
            try:
                val = int(value)
                if val < 0:
                    errors.append(f"Activity cannot be negative, got {val}")
                elif val > 100000:  # Reasonable upper bound
                    errors.append(f"Activity seems unusually high ({val}), please verify")
            except (ValueError, TypeError):
                errors.append(f"Activity must be a whole number, got {type(value).__name__}")
                
        elif field == 'Age':
            try:
                val = int(value)
                if val < 0:
                    errors.append(f"Age cannot be negative, got {val}")
                elif val > 120:
                    errors.append(f"Age seems unusually high ({val}), please verify")
            except (ValueError, TypeError):
                errors.append(f"Age must be a whole number, got {type(value).__name__}")
                
        elif field == 'Gender':
            if value not in ['Male', 'Female']:
                errors.append(f"Gender must be 'Male' or 'Female', got '{value}'")
                
        elif field == 'Work_Study_Hours':
            try:
                val = float(value)
                if val < 0:
                    errors.append(f"Work_Study_Hours cannot be negative, got {val}")
                elif val > 24:
                    errors.append(f"Work_Study_Hours cannot exceed 24, got {val}")
            except (ValueError, TypeError):
                errors.append(f"Work_Study_Hours must be a number, got {type(value).__name__}")
    
    if errors:
        raise ValidationError("input_data", data, "; ".join(errors))
    
    return True

def handle_error(error):
    """Centralized error handling"""
    logger = logging.getLogger(__name__)
    
    if isinstance(error, MentalHealthError):
        logger.warning(f"MentalHealthError: {error.message}")
        return jsonify({
            'error': error.user_message,
            'error_code': error.error_code,
            'timestamp': datetime.utcnow().isoformat()
        }), 400
    
    elif isinstance(error, ValidationError):
        logger.warning(f"ValidationError: {error.message}")
        return jsonify({
            'error': error.user_message,
            'error_code': error.error_code,
            'field': error.field,
            'timestamp': datetime.utcnow().isoformat()
        }), 400
    
    else:
        # Log unexpected errors
        logger.error(f"Unexpected error: {str(error)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({
            'error': 'An unexpected error occurred. Please try again later.',
            'error_code': 'INTERNAL_ERROR',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

def create_success_response(prediction, probabilities, disclaimer, chatbot_message, processing_time):
    """Create standardized success response"""
    return jsonify({
        'prediction': prediction,
        'probabilities': probabilities,
        'disclaimer': disclaimer,
        'model_accuracy': 'This model has a cross-validation accuracy of 80.8%.',
        'chatbot_message': chatbot_message,
        'processing_time_ms': round(processing_time * 1000, 2),
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'success'
    })

def check_crisis_conditions(prediction, probabilities):
    """Check if prediction indicates crisis conditions"""
    if prediction == "Low" and probabilities.get("Low", 0) > Config.CRISIS_THRESHOLD:
        raise CrisisDetectionError(
            f"High confidence prediction of low mental health status detected. "
            f"Confidence: {probabilities.get('Low', 0):.2%}"
        )
    return False
