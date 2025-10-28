from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    """User model for tracking user sessions and preferences"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), unique=True, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='user', lazy=True, cascade='all, delete-orphan')
    feedback = db.relationship('Feedback', backref='user', lazy=True, cascade='all, delete-orphan')

class Prediction(db.Model):
    """Model for storing prediction requests and results"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Input data
    sentiment_score = db.Column(db.Float, nullable=False)
    hrv = db.Column(db.Float, nullable=False)
    sleep_hours = db.Column(db.Float, nullable=False)
    activity = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    work_study_hours = db.Column(db.Float, nullable=False)
    
    # Prediction results
    predicted_status = db.Column(db.String(20), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    low_probability = db.Column(db.Float, nullable=False)
    moderate_probability = db.Column(db.Float, nullable=False)
    high_probability = db.Column(db.Float, nullable=False)
    
    # Metadata
    processing_time_ms = db.Column(db.Float, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Crisis detection
    crisis_detected = db.Column(db.Boolean, default=False)
    crisis_confidence = db.Column(db.Float, nullable=True)

class Feedback(db.Model):
    """Model for storing user feedback on predictions"""
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id'), nullable=True)
    
    # Feedback data
    prediction_accurate = db.Column(db.Boolean, nullable=False)
    actual_status = db.Column(db.String(20), nullable=True)
    feedback_text = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Integer, nullable=True)  # 1-5 scale
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)

class SystemMetrics(db.Model):
    """Model for storing system performance metrics"""
    __tablename__ = 'system_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Performance metrics
    avg_processing_time_ms = db.Column(db.Float, nullable=False)
    total_predictions = db.Column(db.Integer, nullable=False)
    error_rate = db.Column(db.Float, nullable=False)
    
    # Model metrics
    model_accuracy = db.Column(db.Float, nullable=True)
    feature_importance = db.Column(db.JSON, nullable=True)
    
    # Time period
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SecurityEvent(db.Model):
    """Model for storing security-related events"""
    __tablename__ = 'security_events'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Event details
    event_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    description = db.Column(db.Text, nullable=False)
    
    # Request details
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    request_path = db.Column(db.String(200), nullable=True)
    request_method = db.Column(db.String(10), nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime, nullable=True)

# Database utility functions
def init_db(app):
    """Initialize database with app context"""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully")

def get_user_by_session(session_id):
    """Get or create user by session ID"""
    user = User.query.filter_by(session_id=session_id).first()
    if not user:
        user = User(session_id=session_id)
        db.session.add(user)
        db.session.commit()
    return user

def save_prediction(user_id, input_data, prediction_result, processing_time, ip_address=None, user_agent=None):
    """Save prediction to database"""
    prediction = Prediction(
        user_id=user_id,
        sentiment_score=input_data['Sentiment_Score'],
        hrv=input_data['HRV'],
        sleep_hours=input_data['Sleep_Hours'],
        activity=input_data['Activity'],
        age=input_data['Age'],
        gender=input_data['Gender'],
        work_study_hours=input_data['Work_Study_Hours'],
        predicted_status=prediction_result['prediction'],
        confidence_score=max(prediction_result['probabilities'].values()),
        low_probability=prediction_result['probabilities'].get('Low', 0),
        moderate_probability=prediction_result['probabilities'].get('Moderate', 0),
        high_probability=prediction_result['probabilities'].get('High', 0),
        processing_time_ms=processing_time * 1000,
        ip_address=ip_address,
        user_agent=user_agent,
        crisis_detected=prediction_result.get('crisis_detected', False),
        crisis_confidence=prediction_result.get('crisis_confidence')
    )
    
    db.session.add(prediction)
    db.session.commit()
    return prediction

def save_feedback(user_id, prediction_id, accurate, actual_status=None, feedback_text=None, rating=None):
    """Save user feedback"""
    feedback = Feedback(
        user_id=user_id,
        prediction_id=prediction_id,
        prediction_accurate=accurate,
        actual_status=actual_status,
        feedback_text=feedback_text,
        rating=rating
    )
    
    db.session.add(feedback)
    db.session.commit()
    return feedback
