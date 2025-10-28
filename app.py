
from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
from sentiment_analyzer import SentimentAnalyzer
import logging
from datetime import datetime

app = Flask(__name__)

# Load the model and preprocessing objects
model = joblib.load('mental_health_model_final.pkl')
scaler = joblib.load('scaler_final.pkl')
le_gender = joblib.load('le_gender_final.pkl')
le_target = joblib.load('le_target_final.pkl')

# Initialize sentiment analyzer
sentiment_analyzer = SentimentAnalyzer()

# Feature columns
feature_columns = ['Sentiment_Score', 'HRV', 'Sleep_Hours', 'Activity', 'Age', 'Gender', 'Work_Study_Hours']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        # Prepare input data
        input_data = np.array([
            data['Sentiment_Score'],
            data['HRV'],
            data['Sleep_Hours'],
            data['Activity'],
            data['Age'],
            le_gender.transform([data['Gender']])[0],
            data['Work_Study_Hours']
        ]).reshape(1, -1)

        # Scale the input
        input_scaled = scaler.transform(input_data)

        # Make prediction
        prediction = model.predict(input_scaled)[0]
        probabilities = model.predict_proba(input_scaled)[0]

        # Convert prediction back to original label
        prediction_label = le_target.inverse_transform([prediction])[0]

        # Create response
        response = {
            'prediction': prediction_label,
            'probabilities': {
                le_target.classes_[i]: float(prob) 
                for i, prob in enumerate(probabilities)
            },
            'timestamp': datetime.now().isoformat()
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/calculate_sentiment', methods=['POST'])
def calculate_sentiment():
    try:
        data = request.get_json()

        if 'text' in data:
            score = sentiment_analyzer.calculate_text_sentiment(data['text'])
        elif 'activities' in data:
            score = sentiment_analyzer.calculate_behavioral_sentiment(data['activities'])
        elif 'survey' in data:
            score = sentiment_analyzer.calculate_survey_sentiment(data['survey'])
        else:
            score = sentiment_analyzer.calculate_combined_sentiment(
                text_input=data.get('text'),
                activities_data=data.get('activities'),
                survey_responses=data.get('survey')
            )

        return jsonify({
            'sentiment_score': round(score, 3),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
