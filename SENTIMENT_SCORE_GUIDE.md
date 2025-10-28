# 🧠 Sentiment Score Calculation Guide

## 📊 **What is Sentiment Score?**

The sentiment score is a numerical representation of emotional state, ranging from **0.0 (very negative)** to **1.0 (very positive)**, used as a key feature in your mental health prediction model.

## 🔢 **Calculation Methods**

### **1. Text-Based Sentiment Analysis**

**Method:** Analyze written text (diary entries, thoughts, messages)

**Tools Used:**
- **TextBlob:** Simple, fast sentiment analysis
- **VADER:** Advanced sentiment analysis for social media text
- **Custom Keywords:** Domain-specific positive/negative word lists

**Example:**
```python
from sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()

# Analyze text
text = "I feel great today! Everything is going well."
score = analyzer.calculate_text_sentiment(text)
print(f"Sentiment Score: {score:.3f}")  # Output: 0.919
```

**Score Interpretation:**
- **0.0 - 0.3:** Negative sentiment (Low mental health)
- **0.3 - 0.7:** Neutral sentiment (Moderate mental health)  
- **0.7 - 1.0:** Positive sentiment (High mental health)

### **2. Behavioral Sentiment Analysis**

**Method:** Calculate sentiment based on daily activities and behaviors

**Factors Considered:**
- **Sleep Quality:** 7-9 hours = +0.1, <6 or >10 hours = -0.1
- **Activity Level:** High = +0.1, Low = -0.1, Moderate = 0.0
- **Social Interaction:** High = +0.15, Low = -0.15, Moderate = 0.0
- **Work Stress:** Low = +0.1, High = -0.15, Moderate = 0.0

**Example:**
```python
activities = {
    'sleep_hours': 8,
    'activity_level': 'high',
    'social_interaction': 'high',
    'work_stress': 'low'
}

score = analyzer.calculate_behavioral_sentiment(activities)
print(f"Behavioral Sentiment: {score:.3f}")  # Output: 0.950
```

### **3. Survey-Based Sentiment Analysis**

**Method:** Calculate sentiment from structured mental health survey responses

**Survey Questions:**
- **Mood Today:** Very Poor (0.0) → Excellent (1.0)
- **Energy Level:** Very Low (0.0) → Very High (1.0)
- **Stress Level:** Very High (0.0) → Very Low (1.0)
- **Sleep Quality:** Very Poor (0.0) → Excellent (1.0)
- **Social Satisfaction:** Very Dissatisfied (0.0) → Very Satisfied (1.0)

**Example:**
```python
survey = {
    'mood_today': 'good',
    'energy_level': 'high',
    'stress_level': 'low',
    'sleep_quality': 'good',
    'social_satisfaction': 'satisfied'
}

score = analyzer.calculate_survey_sentiment(survey)
print(f"Survey Sentiment: {score:.3f}")  # Output: 0.750
```

### **4. Combined Sentiment Analysis**

**Method:** Weighted combination of all available data sources

**Weights:**
- **Text Analysis:** 40% weight
- **Behavioral Data:** 30% weight
- **Survey Responses:** 30% weight

**Example:**
```python
combined_score = analyzer.calculate_combined_sentiment(
    text_input="I'm feeling optimistic about the future",
    activities_data=activities,
    survey_responses=survey
)
print(f"Combined Sentiment: {combined_score:.3f}")  # Output: 0.805
```

## 🛠️ **Practical Implementation**

### **For Your Mental Health App:**

1. **Add Sentiment Analysis Endpoint:**
```python
@app.route('/calculate_sentiment', methods=['POST'])
def calculate_sentiment():
    data = request.get_json()
    
    analyzer = SentimentAnalyzer()
    
    # Calculate sentiment based on available data
    if 'text' in data:
        score = analyzer.calculate_text_sentiment(data['text'])
    elif 'activities' in data:
        score = analyzer.calculate_behavioral_sentiment(data['activities'])
    elif 'survey' in data:
        score = analyzer.calculate_survey_sentiment(data['survey'])
    else:
        score = analyzer.calculate_combined_sentiment(
            text_input=data.get('text'),
            activities_data=data.get('activities'),
            survey_responses=data.get('survey')
        )
    
    return jsonify({
        'sentiment_score': score,
        'interpretation': get_sentiment_interpretation(score)
    })
```

2. **Integration with Prediction Model:**
```python
# In your prediction endpoint
def predict():
    # ... existing code ...
    
    # Calculate sentiment score if not provided
    if 'Sentiment_Score' not in data or data['Sentiment_Score'] is None:
        analyzer = SentimentAnalyzer()
        sentiment_score = analyzer.calculate_combined_sentiment(
            text_input=data.get('user_text'),
            activities_data=data.get('activities'),
            survey_responses=data.get('survey')
        )
        data['Sentiment_Score'] = sentiment_score
    
    # ... rest of prediction code ...
```

## 📱 **User Interface Options**

### **1. Text Input Method:**
- Simple textarea for diary entries
- Real-time sentiment analysis
- Visual feedback with color coding

### **2. Survey Method:**
- Structured questions with dropdowns
- Quick assessment (2-3 minutes)
- Consistent scoring across users

### **3. Behavioral Tracking:**
- Daily activity logging
- Automatic sentiment calculation
- Trend analysis over time

### **4. Combined Method:**
- Multiple input options
- Weighted scoring
- Most comprehensive assessment

## 🎯 **Best Practices**

### **1. Data Collection:**
- **Encourage regular input:** Daily or weekly sentiment tracking
- **Multiple methods:** Offer text, survey, and behavioral options
- **Context awareness:** Consider time of day, recent events
- **Privacy protection:** Ensure user data is secure

### **2. Score Interpretation:**
- **Provide context:** Explain what the score means
- **Show trends:** Display sentiment over time
- **Offer guidance:** Suggest actions based on sentiment
- **Professional disclaimer:** Always recommend professional help for low scores

### **3. Model Integration:**
- **Feature importance:** Sentiment score is the 2nd most important feature (19.98%)
- **Validation:** Ensure scores are between 0 and 1
- **Missing data:** Use behavioral/survey data when text is unavailable
- **Real-time updates:** Recalculate when new data is available

## 🔧 **Quick Start**

1. **Install Dependencies:**
```bash
pip install textblob nltk
```

2. **Use the Sentiment Calculator:**
Open `sentiment_calculator.html` in your browser for an interactive tool.

3. **Test the Analyzer:**
```bash
python sentiment_analyzer.py
```

4. **Integrate with Your App:**
Add the sentiment analysis to your mental health prediction model.

## 📊 **Example Results**

| Input Method | Sample Input | Sentiment Score | Interpretation |
|--------------|--------------|-----------------|----------------|
| Text | "I feel great today!" | 0.919 | Very Positive |
| Text | "I'm feeling down" | 0.209 | Negative |
| Behavioral | Good sleep + High activity | 0.950 | Very Positive |
| Survey | Good mood + Low stress | 0.750 | Positive |
| Combined | All positive inputs | 0.805 | Very Positive |

## 🚨 **Important Notes**

- **Not a substitute for professional help:** Always recommend professional mental health support
- **Privacy considerations:** Ensure user data is handled securely
- **Cultural sensitivity:** Consider cultural differences in expression
- **Regular updates:** Sentiment can change quickly, encourage regular input
- **Crisis detection:** Low sentiment scores should trigger professional guidance

Your sentiment score calculation system is now ready to provide accurate emotional state assessment for your mental health prediction model! 🎉



