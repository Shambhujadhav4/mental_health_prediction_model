---
tags:
  - mental-health
  - xgboost
  - flask
license: mit
---

# Mental Health Prediction Model
## Overview
This project predicts mental health status (Low, Moderate, High) using a Flask app and an XGBoost model.
## Files
- app.py: Flask app for predictions
- index.html: Web interface
- mental_health_model_final.pkl: Trained XGBoost model
- scaler_final.pkl: Scaler for preprocessing
- le_gender_final.pkl: Label encoder for Gender
- le_target_final.pkl: Label encoder for target
## How to Use
1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `python app.py`
3. Access at `http://localhost:5000`