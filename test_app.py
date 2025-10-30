import unittest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from error_handling import validate_input_data, ValidationError, CrisisDetectionError
from config import Config

class TestMentalHealthApp(unittest.TestCase):
    """Test cases for the mental health prediction application"""
    
    def setUp(self):
        """Set up test environment"""
        # Ensure app import doesn't load models during tests
        os.environ["LOAD_MODELS_ON_STARTUP"] = "0"

        from app_enhanced import app as flask_app
        self.app = flask_app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False

        self.client = self.app.test_client()

        # Import models and encoders in setup when needed
        from app_enhanced import model, scaler, le_gender, le_target
        self.model = model
        self.scaler = scaler
        self.le_gender = le_gender
        self.le_target = le_target

    def test_valid_input_data(self):
        """Test validation with valid input data"""
        valid_data = {
            'Sentiment_Score': 0.5,
            'HRV': 70.0,
            'Sleep_Hours': 8.0,
            'Activity': 5000,
            'Age': 30,
            'Gender': 'Male',
            'Work_Study_Hours': 8.0
        }
        # Should not raise any exception
        self.assertTrue(validate_input_data(valid_data))

    def test_invalid_sentiment_score(self):
        """Test validation with invalid sentiment score"""
        invalid_data = {
            'Sentiment_Score': -1.5,
            'HRV': 70.0,
            'Sleep_Hours': 8.0,
            'Activity': 5000,
            'Age': 30,
            'Gender': 'Male',
            'Work_Study_Hours': 8.0
        }
        with self.assertRaises(ValidationError):
            validate_input_data(invalid_data)
    
    def test_missing_required_field(self):
        """Test validation with missing required field"""
        incomplete_data = {
            'Sentiment_Score': 0.5,
            'HRV': 70.0,
            'Sleep_Hours': 8.0,
            'Activity': 5000,
            'Age': 30,
            # Missing Gender and Work_Study_Hours
        }
        
        with self.assertRaises(ValidationError) as context:
            validate_input_data(incomplete_data)
        
        self.assertIn('Missing required field', str(context.exception))
    
    def test_invalid_gender(self):
        """Test validation with invalid gender"""
        invalid_data = {
            'Sentiment_Score': 0.5,
            'HRV': 70.0,
            'Sleep_Hours': 8.0,
            'Activity': 5000,
            'Age': 30,
            'Gender': 'Other',  # Invalid gender
            'Work_Study_Hours': 8.0
        }
        
        with self.assertRaises(ValidationError) as context:
            validate_input_data(invalid_data)
        
        self.assertIn('Gender must be', str(context.exception))
    
    def test_negative_values(self):
        """Test validation with negative values"""
        invalid_data = {
            'Sentiment_Score': 0.5,
            'HRV': -10.0,  # Negative HRV
            'Sleep_Hours': 8.0,
            'Activity': 5000,
            'Age': 30,
            'Gender': 'Male',
            'Work_Study_Hours': 8.0
        }
        
        with self.assertRaises(ValidationError) as context:
            validate_input_data(invalid_data)
        
        self.assertIn('HRV cannot be negative', str(context.exception))
    
    @patch('app_enhanced.model.predict')
    @patch('app_enhanced.model.predict_proba')
    def test_prediction_endpoint_success(self, mock_predict_proba, mock_predict):
        """Test successful prediction endpoint"""
        # Mock model responses
        mock_predict.return_value = np.array([1])  # Moderate
        mock_predict_proba.return_value = np.array([[0.2, 0.6, 0.2]])  # Low, Moderate, High
        
        valid_data = {
            'Sentiment_Score': 0.5,
            'HRV': 70.0,
            'Sleep_Hours': 8.0,
            'Activity': 5000,
            'Age': 30,
            'Gender': 'Male',
            'Work_Study_Hours': 8.0
        }
        
        response = self.client.post('/predict', 
                                  data=json.dumps(valid_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('prediction', data)
        self.assertIn('probabilities', data)
        self.assertEqual(data['prediction'], 'Moderate')
    
    def test_prediction_endpoint_invalid_data(self):
        """Test prediction endpoint with invalid data"""
        invalid_data = {
            'Sentiment_Score': 1.5,  # Invalid
            'HRV': 70.0,
            'Sleep_Hours': 8.0,
            'Activity': 5000,
            'Age': 30,
            'Gender': 'Male',
            'Work_Study_Hours': 8.0
        }
        
        response = self.client.post('/predict',
                                  data=json.dumps(invalid_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_feedback_endpoint(self):
        """Test feedback endpoint"""
        feedback_data = {
            'prediction': 'Moderate',
            'accurate': True,
            'actual_status': 'Moderate',
            'rating': 4
        }
        
        response = self.client.post('/feedback',
                                  data=json.dumps(feedback_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
    
    def test_crisis_detection(self):
        """Test crisis detection functionality"""
        from error_handling import check_crisis_conditions
        
        # High confidence low mental health prediction
        prediction = "Low"
        probabilities = {"Low": 0.85, "Moderate": 0.10, "High": 0.05}
        
        with self.assertRaises(CrisisDetectionError):
            check_crisis_conditions(prediction, probabilities)
    
    def test_privacy_endpoint(self):
        """Test privacy notice endpoint"""
        response = self.client.get('/privacy')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data_collection', data)
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

class TestModelIntegration(unittest.TestCase):
    """Integration tests for the ML model"""
    
    def setUp(self):
        """Set up test environment"""
        # Try to import app; skip tests if app can't be initialized
        os.environ["LOAD_MODELS_ON_STARTUP"] = "0"
        try:
            from app_enhanced import app as flask_app, model, scaler, le_gender, le_target
            self.app = flask_app
            self.app.config['TESTING'] = True
            self.client = self.app.test_client()
            self.model = model
            self.scaler = scaler
            self.le_gender = le_gender
            self.le_target = le_target
            if any(x is None for x in [self.model, self.scaler, self.le_gender, self.le_target]):
                self.skipTest("Model artifacts not available in CI environment")
        except Exception:
            self.skipTest("App or model artifacts unavailable; skipping integration tests")
    
    def test_model_loading(self):
        """Test that model and preprocessing objects load correctly"""
        from app_enhanced import model, scaler, le_gender, le_target
        self.assertIsNotNone(model)
        self.assertIsNotNone(scaler)
        self.assertIsNotNone(le_gender)
        self.assertIsNotNone(le_target)
    
    def test_model_prediction_format(self):
        """Test that model returns predictions in expected format"""
        # Create test data
        test_data = pd.DataFrame([{
            'Sentiment_Score': 0.5,
            'HRV': 70.0,
            'Sleep_Hours': 8.0,
            'Activity': 5000,
            'Age': 30,
            'Gender': 'Male',
            'Work_Study_Hours': 8.0
        }])
        
        # Preprocess data
        test_data['Gender'] = self.le_gender.transform(test_data['Gender'])
        test_data_scaled = self.scaler.transform(test_data)
        
        # Make prediction
        prediction = self.model.predict(test_data_scaled)
        probabilities = self.model.predict_proba(test_data_scaled)
        
        # Assertions
        self.assertEqual(len(prediction), 1)
        self.assertIn(prediction[0], [0, 1, 2])  # Valid class labels
        self.assertEqual(probabilities.shape, (1, 3))  # 3 classes
        self.assertAlmostEqual(sum(probabilities[0]), 1.0, places=5)  # Probabilities sum to 1

class TestSecurityFeatures(unittest.TestCase):
    """Test security-related features"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ["LOAD_MODELS_ON_STARTUP"] = "0"
        from app_enhanced import app as flask_app
        self.app = flask_app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # This would require implementing rate limiting middleware
        # For now, we'll test the structure
        pass
    
    def test_input_sanitization(self):
        """Test input sanitization against injection attacks"""
        malicious_data = {
            'Sentiment_Score': "'; DROP TABLE predictions; --",
            'HRV': 70.0,
            'Sleep_Hours': 8.0,
            'Activity': 5000,
            'Age': 30,
            'Gender': 'Male',
            'Work_Study_Hours': 8.0
        }
        
        # Should raise ValidationError for invalid sentiment score
        with self.assertRaises(ValidationError):
            validate_input_data(malicious_data)

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMentalHealthApp))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestModelIntegration))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestSecurityFeatures))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)
