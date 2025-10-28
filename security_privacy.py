from flask import request, session, g
from functools import wraps
import hashlib
import hmac
import time
import logging
from datetime import datetime, timedelta
import re
from config import Config

class SecurityManager:
    """Comprehensive security management for the mental health prediction app"""
    
    def __init__(self):
        self.failed_attempts = {}  # In production, use Redis or database
        self.blocked_ips = set()
        self.rate_limits = {}
    
    def validate_input_security(self, data):
        """Validate input for security threats"""
        security_logger = logging.getLogger('security')
        
        # Check for SQL injection patterns
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            r"(--|\#|\/\*|\*\/)",
            r"(\b(SCRIPT|JAVASCRIPT|VBSCRIPT)\b)",
        ]
        
        for field, value in data.items():
            if isinstance(value, str):
                for pattern in sql_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        security_logger.warning(f"Potential SQL injection detected in {field}: {value}")
                        return False, f"Invalid input detected in {field}"
        
        # Check for XSS patterns
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
        ]
        
        for field, value in data.items():
            if isinstance(value, str):
                for pattern in xss_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        security_logger.warning(f"Potential XSS detected in {field}: {value}")
                        return False, f"Invalid input detected in {field}"
        
        return True, "Input validation passed"
    
    def check_rate_limit(self, ip_address):
        """Check if IP address has exceeded rate limits"""
        current_time = time.time()
        minute_window = int(current_time // 60)
        
        if ip_address not in self.rate_limits:
            self.rate_limits[ip_address] = {}
        
        if minute_window not in self.rate_limits[ip_address]:
            self.rate_limits[ip_address][minute_window] = 0
        
        self.rate_limits[ip_address][minute_window] += 1
        
        # Clean old windows
        for window in list(self.rate_limits[ip_address].keys()):
            if window < minute_window - 1:
                del self.rate_limits[ip_address][window]
        
        # Check if limit exceeded
        current_count = self.rate_limits[ip_address].get(minute_window, 0)
        if current_count > Config.RATE_LIMIT_PER_MINUTE:
            return False, f"Rate limit exceeded: {current_count} requests in current minute"
        
        return True, "Rate limit check passed"
    
    def check_failed_attempts(self, ip_address):
        """Check for suspicious activity from IP address"""
        current_time = time.time()
        
        if ip_address not in self.failed_attempts:
            self.failed_attempts[ip_address] = []
        
        # Clean old attempts (older than 1 hour)
        self.failed_attempts[ip_address] = [
            attempt for attempt in self.failed_attempts[ip_address]
            if current_time - attempt < 3600
        ]
        
        # Check if too many failed attempts
        if len(self.failed_attempts[ip_address]) > 10:
            self.blocked_ips.add(ip_address)
            return False, "IP address blocked due to suspicious activity"
        
        return True, "Failed attempts check passed"
    
    def log_failed_attempt(self, ip_address, reason):
        """Log a failed attempt"""
        current_time = time.time()
        
        if ip_address not in self.failed_attempts:
            self.failed_attempts[ip_address] = []
        
        self.failed_attempts[ip_address].append(current_time)
        
        security_logger = logging.getLogger('security')
        security_logger.warning(f"Failed attempt from {ip_address}: {reason}")
    
    def generate_csrf_token(self):
        """Generate CSRF token"""
        if 'csrf_token' not in session:
            session['csrf_token'] = hashlib.sha256(
                f"{session.get('session_id', '')}{time.time()}".encode()
            ).hexdigest()
        return session['csrf_token']
    
    def validate_csrf_token(self, token):
        """Validate CSRF token"""
        return token == session.get('csrf_token')
    
    def sanitize_user_input(self, data):
        """Sanitize user input to prevent security issues"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Remove potentially dangerous characters
                sanitized[key] = re.sub(r'[<>"\']', '', value).strip()
            else:
                sanitized[key] = value
        
        return sanitized
    
    def hash_sensitive_data(self, data):
        """Hash sensitive data for logging"""
        sensitive_fields = ['ip_address', 'user_agent']
        hashed_data = {}
        
        for key, value in data.items():
            if key in sensitive_fields and isinstance(value, str):
                hashed_data[key] = hashlib.sha256(value.encode()).hexdigest()[:8]
            else:
                hashed_data[key] = value
        
        return hashed_data

# Security decorators
def require_security_check(f):
    """Decorator to require security checks"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        security_manager = SecurityManager()
        ip_address = request.remote_addr
        
        # Check if IP is blocked
        if ip_address in security_manager.blocked_ips:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check rate limit
        rate_ok, rate_msg = security_manager.check_rate_limit(ip_address)
        if not rate_ok:
            security_manager.log_failed_attempt(ip_address, rate_msg)
            return jsonify({'error': rate_msg}), 429
        
        # Check failed attempts
        attempts_ok, attempts_msg = security_manager.check_failed_attempts(ip_address)
        if not attempts_ok:
            return jsonify({'error': attempts_msg}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def validate_input_security(f):
    """Decorator to validate input security"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.is_json:
            data = request.get_json()
            security_manager = SecurityManager()
            
            # Validate input security
            security_ok, security_msg = security_manager.validate_input_security(data)
            if not security_ok:
                security_manager.log_failed_attempt(request.remote_addr, security_msg)
                return jsonify({'error': 'Invalid input detected'}), 400
            
            # Sanitize input
            sanitized_data = security_manager.sanitize_user_input(data)
            request.sanitized_data = sanitized_data
        
        return f(*args, **kwargs)
    
    return decorated_function

# Privacy protection functions
class PrivacyManager:
    """Privacy management for user data protection"""
    
    @staticmethod
    def anonymize_user_data(data):
        """Anonymize user data for analytics"""
        anonymized = data.copy()
        
        # Remove or hash identifying information
        if 'ip_address' in anonymized:
            anonymized['ip_address'] = hashlib.sha256(
                anonymized['ip_address'].encode()
            ).hexdigest()[:8]
        
        if 'user_agent' in anonymized:
            anonymized['user_agent'] = anonymized['user_agent'][:50] + "..."
        
        return anonymized
    
    @staticmethod
    def should_retain_data(user_id, data_type):
        """Determine if data should be retained based on privacy policies"""
        # Implement data retention policies
        retention_periods = {
            'prediction': 90,  # days
            'feedback': 365,   # days
            'session': 30,     # days
        }
        
        return data_type in retention_periods
    
    @staticmethod
    def create_privacy_notice():
        """Create privacy notice for users"""
        return {
            "data_collection": "We collect minimal data necessary for prediction accuracy",
            "data_usage": "Data is used solely for improving prediction accuracy",
            "data_sharing": "We do not share personal data with third parties",
            "data_retention": "Data is retained for up to 90 days for model improvement",
            "user_rights": "You can request data deletion at any time",
            "contact": "Contact us for privacy-related questions"
        }

# Security headers middleware
def add_security_headers(response):
    """Add security headers to responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# Data encryption utilities
class DataEncryption:
    """Simple data encryption for sensitive information"""
    
    @staticmethod
    def encrypt_sensitive_data(data, key=None):
        """Encrypt sensitive data"""
        if key is None:
            key = Config.SECRET_KEY.encode()
        
        # Simple XOR encryption (in production, use proper encryption)
        encrypted = bytearray()
        key_bytes = key * (len(data) // len(key) + 1)
        
        for i, byte in enumerate(data.encode()):
            encrypted.append(byte ^ key_bytes[i])
        
        return encrypted.hex()
    
    @staticmethod
    def decrypt_sensitive_data(encrypted_data, key=None):
        """Decrypt sensitive data"""
        if key is None:
            key = Config.SECRET_KEY.encode()
        
        encrypted_bytes = bytes.fromhex(encrypted_data)
        decrypted = bytearray()
        key_bytes = key * (len(encrypted_bytes) // len(key) + 1)
        
        for i, byte in enumerate(encrypted_bytes):
            decrypted.append(byte ^ key_bytes[i])
        
        return decrypted.decode()



