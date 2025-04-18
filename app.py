from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import numpy as np
import joblib
import os

app = Flask(__name__)

# Load the model and preprocessing objects
model = joblib.load('mental_health_model_final.pkl')
scaler = joblib.load('scaler_final.pkl')
le_gender = joblib.load('le_gender_final.pkl')
le_target = joblib.load('le_target_final.pkl')

# Print feature importance
columns = ['Sentiment_Score', 'HRV', 'Sleep_Hours', 'Activity', 'Age', 'Gender', 'Work_Study_Hours']
print("Feature Importance:")
for feature, importance in zip(columns, model.feature_importances_):
    print(f"{feature}: {importance:.4f}")

# Serve the HTML file
@app.route('/')
def serve_html():
    return send_from_directory('.', 'index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the input data from the request
        data = request.get_json()
        
        # Convert to DataFrame
        columns = ['Sentiment_Score', 'HRV', 'Sleep_Hours', 'Activity', 'Age', 'Gender', 'Work_Study_Hours']
        new_data = pd.DataFrame([data], columns=columns)
        
        # Validate input
        if new_data['Sleep_Hours'].iloc[0] < 0:
            return jsonify({'error': 'Sleep_Hours cannot be negative'}), 400
        if new_data['Work_Study_Hours'].iloc[0] < 0:
            return jsonify({'error': 'Work_Study_Hours cannot be negative'}), 400
        if new_data['Gender'].iloc[0] not in ['Male', 'Female']:
            return jsonify({'error': 'Gender must be Male or Female'}), 400
        
        # Preprocess the data
        new_data['Gender'] = le_gender.transform(new_data['Gender'])
        new_data_scaled = scaler.transform(new_data)
        
        # Predict
        prediction = model.predict(new_data_scaled)[0]
        probs = model.predict_proba(new_data_scaled)[0]
        health_status = {0: "Low", 1: "Moderate", 2: "High"}
        result = health_status[prediction]
        
        # Include probabilities in the response
        prob_dict = {health_status[i]: float(prob) for i, prob in enumerate(probs)}
        
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

        return jsonify({
            'prediction': result,
            'probabilities': prob_dict,
            'disclaimer': disclaimer,
            'model_accuracy': 'This model has a cross-validation accuracy of 80.8%.',
            'chatbot_message': chatbot_message
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        feedback_data = request.get_json()
        with open('feedback.log', 'a') as f:
            f.write(f"Prediction: {feedback_data['prediction']}, Accurate: {feedback_data['accurate']}\n")
        return jsonify({'message': 'Feedback received'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)