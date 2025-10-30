from flask import Flask, request, jsonify, send_from_directory, session, g
import pandas as pd
import numpy as np
import joblib
import os
import time
import uuid
from datetime import datetime
import logging

# Import our new modules (simplified version without database)
from config import Config
from logging_config import setup_logging, log_prediction, log_performance, log_request_info, log_response_info
from error_handling import validate_input_data, handle_error, create_success_response, check_crisis_conditions
from medical_guidance import create_professional_guidance_response, MedicalGuidance
from security_privacy import require_security_check, validate_input_security, add_security_headers, PrivacyManager
from sentiment_analyzer import SentimentAnalyzer

app = Flask(__name__)
app.config.from_object(Config)

# Setup logging
setup_logging(app)

# Security headers
app.after_request(add_security_headers)

# Request logging
@app.before_request
def before_request():
    log_request_info()

@app.after_request
def after_request(response):
    return log_response_info(response)

# Load the model and preprocessing objects (lazily controllable via env)
model = None
scaler = None
le_gender = None
le_target = None

_load_on_startup = os.getenv("LOAD_MODELS_ON_STARTUP", "1") == "1"
if _load_on_startup:
    try:
        model = joblib.load(Config.MODEL_PATH)
        scaler = joblib.load(Config.SCALER_PATH)
        le_gender = joblib.load(Config.LE_GENDER_PATH)
        le_target = joblib.load(Config.LE_TARGET_PATH)
        app.logger.info("Model and preprocessing objects loaded successfully")
    except Exception as e:
        app.logger.error(f"Failed to load model: {str(e)}")
        raise
else:
    app.logger.info("Skipping model load on startup due to LOAD_MODELS_ON_STARTUP=0")

# Initialize sentiment analyzer
sentiment_analyzer = SentimentAnalyzer()
app.logger.info("Sentiment analyzer initialized successfully")

# Print feature importance when model is available
columns = Config.FEATURE_COLUMNS
if model is not None and hasattr(model, 'feature_importances_'):
    app.logger.info("Feature Importance:")
    for feature, importance in zip(columns, model.feature_importances_):
        app.logger.info(f"{feature}: {importance:.4f}")

# Serve the HTML file
@app.route('/')
def serve_html():
    return send_from_directory('.', 'index.html')

@app.route('/predict', methods=['POST'])
@require_security_check
@validate_input_security
@log_performance
def predict():
    try:
        # Get the input data from the request
        data = getattr(request, 'sanitized_data', request.get_json())
        
        # Validate input
        validate_input_data(data)
        
        # Get user session
        session_id = session.get('session_id', str(uuid.uuid4()))
        session['session_id'] = session_id
        
        # Convert to DataFrame
        new_data = pd.DataFrame([data], columns=Config.FEATURE_COLUMNS)
        
        # Preprocess the data
        new_data['Gender'] = le_gender.transform(new_data['Gender'])
        new_data_scaled = scaler.transform(new_data)
        
        # Predict
        start_time = time.time()
        prediction = model.predict(new_data_scaled)[0]
        probs = model.predict_proba(new_data_scaled)[0]
        processing_time = time.time() - start_time
        
        health_status = Config.HEALTH_STATUS_MAPPING
        result = health_status[prediction]
        
        # Include probabilities in the response
        prob_dict = {health_status[i]: float(prob) for i, prob in enumerate(probs)}
        
        # Check for crisis conditions
        crisis_detected = False
        crisis_confidence = None
        try:
            check_crisis_conditions(result, prob_dict)
        except Exception as e:
            crisis_detected = True
            crisis_confidence = prob_dict.get('Low', 0)
            app.logger.critical(f"Crisis detected: {str(e)}")
        
        # Add a disclaimer for borderline predictions
        max_prob = probs.max()
        disclaimer = ""
        if max_prob < 0.7:
            disclaimer = "This prediction is uncertain (confidence below 70%). Please consult a professional for an accurate assessment."
        
        # Add a simple chatbot-like message
        if result == "Low":
            chatbot_message = "It looks like you might be experiencing low mental health. Consider reaching out to a friend or professional for support."
        elif result == "Moderate":
            chatbot_message = "Your mental health seems moderate. Keep up with self-care practices, and consider talking to someone if you feel overwhelmed."
        else:  # High
            chatbot_message = "Great news! Your mental health appears to be high. Keep maintaining your healthy habits!"
        
        # Create professional guidance
        professional_guidance = create_professional_guidance_response(result, max_prob)
        
        # Log prediction for analytics
        log_prediction(
            session_id, data, result, prob_dict, processing_time, request.remote_addr
        )
        
        return create_success_response(
            result, prob_dict, disclaimer, chatbot_message, processing_time
        )
        
    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return handle_error(e)

@app.route('/feedback', methods=['POST'])
@require_security_check
@validate_input_security
def feedback():
    try:
        feedback_data = getattr(request, 'sanitized_data', request.get_json())
        
        # Simple file-based feedback logging
        with open('feedback.log', 'a') as f:
            f.write(f"{datetime.utcnow().isoformat()}: {feedback_data}\n")
        
        app.logger.info(f"Feedback received: {feedback_data}")
        
        return jsonify({
            'message': 'Feedback received successfully',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        app.logger.error(f"Feedback error: {str(e)}")
        return handle_error(e)

@app.route('/privacy', methods=['GET'])
def privacy_notice():
    """Return privacy notice"""
    privacy_manager = PrivacyManager()
    return jsonify(privacy_manager.create_privacy_notice())

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0'
    })

@app.route('/calculate_sentiment', methods=['POST'])
@require_security_check
@validate_input_security
@log_performance
def calculate_sentiment():
    """Calculate sentiment score using multiple methods"""
    try:
        data = getattr(request, 'sanitized_data', request.get_json())
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        sentiment_score = None
        method_used = None
        
        # Determine which method to use based on available data
        if 'text' in data and data['text'].strip():
            # Text-based sentiment analysis
            sentiment_score = sentiment_analyzer.calculate_text_sentiment(data['text'])
            method_used = 'text_analysis'
            
        elif 'activities' in data:
            # Behavioral sentiment analysis
            sentiment_score = sentiment_analyzer.calculate_behavioral_sentiment(data['activities'])
            method_used = 'behavioral_analysis'
            
        elif 'survey' in data:
            # Survey-based sentiment analysis
            sentiment_score = sentiment_analyzer.calculate_survey_sentiment(data['survey'])
            method_used = 'survey_analysis'
            
        else:
            # Combined analysis if multiple data sources available
            sentiment_score = sentiment_analyzer.calculate_combined_sentiment(
                text_input=data.get('text'),
                activities_data=data.get('activities'),
                survey_responses=data.get('survey')
            )
            method_used = 'combined_analysis'
        
        if sentiment_score is None:
            return jsonify({'error': 'Unable to calculate sentiment score'}), 400
        
        # Interpret the sentiment score
        interpretation = get_sentiment_interpretation(sentiment_score)
        
        response_data = {
            'sentiment_score': round(sentiment_score, 3),
            'method_used': method_used,
            'interpretation': interpretation,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'success'
        }
        
        app.logger.info(f"Sentiment calculated: {sentiment_score:.3f} using {method_used}")
        
        return jsonify(response_data)
        
    except Exception as e:
        app.logger.error(f"Sentiment calculation error: {str(e)}")
        return handle_error(e)

@app.route('/sentiment_calculator', methods=['GET'])
def serve_sentiment_calculator():
    """Serve the sentiment calculator page"""
    return send_from_directory('.', 'sentiment_calculator.html')

def get_sentiment_interpretation(score):
    """Get interpretation of sentiment score"""
    if score >= 0.7:
        return {
            'level': 'positive',
            'description': 'Positive sentiment - High mental health',
            'recommendation': 'Continue maintaining your positive outlook and healthy habits!',
            'color': 'green'
        }
    elif score <= 0.3:
        return {
            'level': 'negative',
            'description': 'Negative sentiment - Low mental health',
            'recommendation': 'Consider reaching out to a mental health professional for support.',
            'color': 'red'
        }
    else:
        return {
            'level': 'neutral',
            'description': 'Neutral sentiment - Moderate mental health',
            'recommendation': 'Monitor your mental health and consider self-care practices.',
            'color': 'blue'
        }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
