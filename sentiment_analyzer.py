import re
import nltk
from textblob import TextBlob
import numpy as np
from datetime import datetime
import logging

class SentimentAnalyzer:
    """Comprehensive sentiment analysis for mental health prediction"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Download required NLTK data
        try:
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('punkt', quiet=True)
            from nltk.sentiment import SentimentIntensityAnalyzer
            self.vader_analyzer = SentimentIntensityAnalyzer()
        except:
            self.vader_analyzer = None
            self.logger.warning("NLTK VADER not available, using TextBlob only")
    
    def calculate_text_sentiment(self, text):
        """
        Calculate sentiment score from text input
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            float: Sentiment score between -1 and 1
        """
        if not text or not isinstance(text, str):
            return 0.0
        
        # Clean the text
        cleaned_text = self._clean_text(text)
        
        # Calculate sentiment using multiple methods
        scores = []
        
        # Method 1: TextBlob
        try:
            blob = TextBlob(cleaned_text)
            textblob_score = blob.sentiment.polarity
            scores.append(textblob_score)
        except Exception as e:
            self.logger.error(f"TextBlob sentiment error: {e}")
        
        # Method 2: VADER (if available)
        if self.vader_analyzer:
            try:
                vader_scores = self.vader_analyzer.polarity_scores(cleaned_text)
                vader_score = vader_scores['compound']  # -1 to 1
                scores.append(vader_score)
            except Exception as e:
                self.logger.error(f"VADER sentiment error: {e}")
        
        # Method 3: Custom keyword-based scoring
        keyword_score = self._keyword_based_sentiment(cleaned_text)
        scores.append(keyword_score)
        
        # Return average of all methods
        if scores:
            final_score = np.mean(scores)
            # Ensure score is between -1 and 1
            return max(-1.0, min(1.0, final_score))
        
        return 0.0
    
    def calculate_behavioral_sentiment(self, activities_data):
        """
        Calculate sentiment based on behavioral patterns
        
        Args:
            activities_data (dict): Dictionary containing activity information
            
        Returns:
            float: Sentiment score between 0 and 1
        """
        score = 0.5  # Start with neutral
        
        # Sleep quality impact
        sleep_hours = activities_data.get('sleep_hours', 8)
        if 7 <= sleep_hours <= 9:
            score += 0.1  # Good sleep
        elif sleep_hours < 6 or sleep_hours > 10:
            score -= 0.1  # Poor sleep
        
        # Activity level impact
        activity_level = activities_data.get('activity_level', 'moderate')
        activity_scores = {
            'low': -0.1,
            'moderate': 0.0,
            'high': 0.1
        }
        score += activity_scores.get(activity_level, 0.0)
        
        # Social interaction impact
        social_interaction = activities_data.get('social_interaction', 'moderate')
        social_scores = {
            'low': -0.15,
            'moderate': 0.0,
            'high': 0.15
        }
        score += social_scores.get(social_interaction, 0.0)
        
        # Work stress impact
        work_stress = activities_data.get('work_stress', 'moderate')
        stress_scores = {
            'low': 0.1,
            'moderate': 0.0,
            'high': -0.15
        }
        score += stress_scores.get(work_stress, 0.0)
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))
    
    def calculate_survey_sentiment(self, survey_responses):
        """
        Calculate sentiment from survey responses
        
        Args:
            survey_responses (dict): Dictionary of survey questions and answers
            
        Returns:
            float: Sentiment score between 0 and 1
        """
        total_score = 0
        question_count = 0
        
        # Common mental health survey questions and their scoring
        question_scores = {
            'mood_today': {
                'very_poor': 0.0,
                'poor': 0.25,
                'fair': 0.5,
                'good': 0.75,
                'excellent': 1.0
            },
            'energy_level': {
                'very_low': 0.0,
                'low': 0.25,
                'moderate': 0.5,
                'high': 0.75,
                'very_high': 1.0
            },
            'stress_level': {
                'very_high': 0.0,
                'high': 0.25,
                'moderate': 0.5,
                'low': 0.75,
                'very_low': 1.0
            },
            'sleep_quality': {
                'very_poor': 0.0,
                'poor': 0.25,
                'fair': 0.5,
                'good': 0.75,
                'excellent': 1.0
            },
            'social_satisfaction': {
                'very_dissatisfied': 0.0,
                'dissatisfied': 0.25,
                'neutral': 0.5,
                'satisfied': 0.75,
                'very_satisfied': 1.0
            }
        }
        
        for question, answer in survey_responses.items():
            if question in question_scores and answer in question_scores[question]:
                total_score += question_scores[question][answer]
                question_count += 1
        
        if question_count > 0:
            return total_score / question_count
        
        return 0.5  # Default neutral score
    
    def calculate_combined_sentiment(self, text_input=None, activities_data=None, survey_responses=None):
        """
        Calculate combined sentiment score from multiple sources
        
        Args:
            text_input (str): Text input for sentiment analysis
            activities_data (dict): Behavioral activity data
            survey_responses (dict): Survey response data
            
        Returns:
            float: Combined sentiment score between 0 and 1
        """
        scores = []
        weights = []
        
        # Text sentiment (weight: 0.4)
        if text_input:
            text_score = self.calculate_text_sentiment(text_input)
            # Convert from -1,1 range to 0,1 range
            text_score_normalized = (text_score + 1) / 2
            scores.append(text_score_normalized)
            weights.append(0.4)
        
        # Behavioral sentiment (weight: 0.3)
        if activities_data:
            behavior_score = self.calculate_behavioral_sentiment(activities_data)
            scores.append(behavior_score)
            weights.append(0.3)
        
        # Survey sentiment (weight: 0.3)
        if survey_responses:
            survey_score = self.calculate_survey_sentiment(survey_responses)
            scores.append(survey_score)
            weights.append(0.3)
        
        if scores:
            # Weighted average
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            total_weight = sum(weights)
            return weighted_sum / total_weight
        
        return 0.5  # Default neutral score
    
    def _clean_text(self, text):
        """Clean and preprocess text for sentiment analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?]', '', text)
        
        return text.strip()
    
    def _keyword_based_sentiment(self, text):
        """Simple keyword-based sentiment analysis"""
        positive_words = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'happy', 'joy', 'love', 'like', 'enjoy', 'pleased', 'satisfied',
            'positive', 'optimistic', 'hopeful', 'confident', 'energetic',
            'motivated', 'excited', 'grateful', 'thankful', 'blessed'
        ]
        
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate',
            'sad', 'depressed', 'angry', 'frustrated', 'annoyed', 'upset',
            'negative', 'pessimistic', 'hopeless', 'worried', 'anxious',
            'stressed', 'tired', 'exhausted', 'lonely', 'isolated'
        ]
        
        words = text.split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)

# Example usage and testing
def test_sentiment_analyzer():
    """Test the sentiment analyzer with sample data"""
    analyzer = SentimentAnalyzer()
    
    # Test text sentiment
    test_texts = [
        "I feel great today! Everything is going well.",
        "I'm feeling really down and depressed.",
        "Today was okay, nothing special happened.",
        "I'm so excited about my new job!"
    ]
    
    print("Text Sentiment Analysis:")
    for text in test_texts:
        score = analyzer.calculate_text_sentiment(text)
        print(f"Text: '{text}'")
        print(f"Sentiment Score: {score:.3f}")
        print("-" * 50)
    
    # Test behavioral sentiment
    activities = {
        'sleep_hours': 8,
        'activity_level': 'high',
        'social_interaction': 'high',
        'work_stress': 'low'
    }
    
    behavior_score = analyzer.calculate_behavioral_sentiment(activities)
    print(f"Behavioral Sentiment Score: {behavior_score:.3f}")
    
    # Test survey sentiment
    survey = {
        'mood_today': 'good',
        'energy_level': 'high',
        'stress_level': 'low',
        'sleep_quality': 'good',
        'social_satisfaction': 'satisfied'
    }
    
    survey_score = analyzer.calculate_survey_sentiment(survey)
    print(f"Survey Sentiment Score: {survey_score:.3f}")
    
    # Test combined sentiment
    combined_score = analyzer.calculate_combined_sentiment(
        text_input="I'm feeling optimistic about the future",
        activities_data=activities,
        survey_responses=survey
    )
    print(f"Combined Sentiment Score: {combined_score:.3f}")

if __name__ == "__main__":
    test_sentiment_analyzer()



