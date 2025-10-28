import random
from locust import HttpUser, task, between

class MentalHealthPredictionUser(HttpUser):
    """Locust user class for performance testing"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a user starts"""
        self.session_id = f"test_session_{random.randint(1000, 9999)}"
    
    @task(3)
    def predict_mental_health(self):
        """Test the main prediction endpoint"""
        data = {
            "Sentiment_Score": round(random.uniform(0, 1), 3),
            "HRV": round(random.uniform(20, 100), 2),
            "Sleep_Hours": round(random.uniform(3, 12), 1),
            "Activity": random.randint(1000, 15000),
            "Age": random.randint(18, 80),
            "Gender": random.choice(["Male", "Female"]),
            "Work_Study_Hours": round(random.uniform(0, 16), 1)
        }
        
        with self.client.post(
            "/predict",
            json=data,
            headers={"Content-Type": "application/json"},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response_data = response.json()
                if "prediction" in response_data:
                    response.success()
                else:
                    response.failure("Missing prediction in response")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def submit_feedback(self):
        """Test the feedback endpoint"""
        feedback_data = {
            "prediction": random.choice(["Low", "Moderate", "High"]),
            "accurate": random.choice([True, False]),
            "rating": random.randint(1, 5)
        }
        
        with self.client.post(
            "/feedback",
            json=feedback_data,
            headers={"Content-Type": "application/json"},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def load_homepage(self):
        """Test loading the homepage"""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def test_invalid_prediction(self):
        """Test with invalid data to check error handling"""
        invalid_data = {
            "Sentiment_Score": 1.5,  # Invalid: > 1
            "HRV": -10,  # Invalid: negative
            "Sleep_Hours": 8.0,
            "Activity": 5000,
            "Age": 30,
            "Gender": "Male",
            "Work_Study_Hours": 8.0
        }
        
        with self.client.post(
            "/predict",
            json=invalid_data,
            headers={"Content-Type": "application/json"},
            catch_response=True
        ) as response:
            if response.status_code == 400:
                response.success()
            else:
                response.failure(f"Expected 400, got {response.status_code}")
