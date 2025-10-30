# 🧠 Mental Health Prediction Model

A web-based application that predicts mental health status (Low, Moderate, High) using machine learning. Built with Flask and powered by an XGBoost model trained on comprehensive health metrics including sentiment analysis, HRV, sleep patterns, and activity levels.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.0-green.svg)
![XGBoost](https://img.shields.io/badge/XGBoost-3.0.0-orange.svg)
![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Model Details](#model-details)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This project provides a user-friendly web interface for mental health assessment using machine learning. The system analyzes multiple health indicators including:

- **Sentiment Score**: Analyzes emotional tone from text input, behavioral patterns, or survey responses
- **Heart Rate Variability (HRV)**: Cardiovascular health indicator
- **Sleep Hours**: Sleep duration tracking
- **Activity Level**: Daily physical activity (steps)
- **Demographic Data**: Age and gender
- **Work/Study Hours**: Time spent on work or study activities

The model predicts one of three mental health states:
- **Low**: Indicates potential mental health concerns requiring attention
- **Moderate**: Balanced mental health status
- **High**: Positive mental health indicators (⚠️ Note: If prediction is HIGH, consult a qualified healthcare professional)

## ✨ Features

- 🎨 **Intuitive Web Interface**: Clean, responsive design with gradient backgrounds
- 📊 **Real-time Predictions**: Instant mental health status predictions with probability scores
- 💬 **Sentiment Analysis**: Multiple methods for calculating sentiment scores:
  - Text sentiment analysis from diary entries or thoughts
  - Behavioral sentiment from daily activities
  - Survey-based sentiment assessment
  - Combined sentiment analysis
- 🔍 **Detailed Results**: View prediction probabilities for all mental health states
- 📱 **Mobile Responsive**: Works seamlessly on desktop, tablet, and mobile devices
- 🧮 **Standalone Sentiment Calculator**: Dedicated page for sentiment score calculations
- 🔒 **Privacy Focused**: All processing is done locally (when deployed properly)

## 🛠 Technology Stack

### Backend
- **Python 3.8+**: Core programming language
- **Flask 3.1.0**: Web framework
- **XGBoost 3.0.0**: Gradient boosting machine learning model
- **scikit-learn 1.5.2**: Data preprocessing and model utilities
- **pandas 2.2.3**: Data manipulation
- **numpy 2.1.3**: Numerical computations
- **joblib 1.4.2**: Model serialization

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling with animations
- **JavaScript**: Client-side interactivity

### Deployment
- **Gunicorn 21.2.0**: WSGI HTTP Server (for production)
- **Docker**: Containerization support

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Shambhujadhav4/mental_health_prediction_model.git
cd mental_health_prediction_model
```

### Step 2: Create a Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements_updated.txt
```

### Step 4: Verify Required Files

Ensure these model files are present in the project directory:
- `mental_health_model_final.pkl`
- `scaler_final.pkl`
- `le_gender_final.pkl`
- `le_target_final.pkl`

## 💻 Usage

### Running Locally

1. **Start the Flask application:**

```bash
python app.py
```

2. **Access the application:**

Open your web browser and navigate to:
```
http://localhost:5000
```
or
```
http://127.0.0.1:5000
```

3. **Using the Application:**

   - **Main Prediction Page (`/`)**: 
     - Fill in the required health metrics
     - Click "🧠 Calculate" to compute sentiment score from text (optional)
     - Click "Predict" to get mental health prediction
   
   - **Sentiment Calculator (`/sentiment` or `/sentiment_calculator`)**:
     - Calculate sentiment scores using different methods:
       - Text analysis
       - Behavioral analysis
       - Survey-based analysis
       - Combined analysis

### Input Parameters

| Parameter | Description | Type | Range/Options |
|-----------|------------|------|---------------|
| Sentiment Score | Emotional tone indicator | Float | 0.0 - 1.0 |
| HRV | Heart Rate Variability | Float | ≥ 0 |
| Sleep Hours | Hours of sleep per day | Float | ≥ 0 |
| Activity | Daily steps | Integer | ≥ 0 |
| Age | User age | Integer | ≥ 0 |
| Gender | Gender identifier | String | Male, Female |
| Work/Study Hours | Hours worked/studied | Float | ≥ 0 |

### Stopping the Server

Press `Ctrl + C` in the terminal where the application is running.

## 📡 API Documentation

### Endpoints

#### 1. Home Page
```
GET /
```
Returns the main prediction interface HTML page.

**Response:** HTML page

---

#### 2. Sentiment Calculator Page
```
GET /sentiment
GET /sentiment_calculator
```
Returns the sentiment calculator interface HTML page.

**Response:** HTML page

---

#### 3. Mental Health Prediction
```
POST /predict
Content-Type: application/json
```

**Request Body:**
```json
{
  "Sentiment_Score": 0.75,
  "HRV": 45.5,
  "Sleep_Hours": 8.0,
  "Activity": 8000,
  "Age": 28,
  "Gender": "Male",
  "Work_Study_Hours": 8.5
}
```

**Response:**
```json
{
  "prediction": "Moderate",
  "probabilities": {
    "Low": 0.0119,
    "Moderate": 0.9854,
    "High": 0.0027
  },
  "timestamp": "2025-01-15T10:30:00.123456"
}
```

**Error Response:**
```json
{
  "error": "Error message description"
}
```
Status Code: 400

---

#### 4. Calculate Sentiment Score
```
POST /calculate_sentiment
Content-Type: application/json
```

**Request Body Options:**

**Text-based:**
```json
{
  "text": "I feel great today! I had a wonderful time with friends."
}
```

**Behavioral-based:**
```json
{
  "activities": {
    "sleep_hours": 8,
    "activity_level": "high",
    "social_interaction": "moderate",
    "work_stress": "low"
  }
}
```

**Survey-based:**
```json
{
  "survey": {
    "mood_today": "good",
    "energy_level": "high",
    "stress_level": "moderate",
    "sleep_quality": "good"
  }
}
```

**Combined (optional fields):**
```json
{
  "text": "I'm feeling optimistic about the future.",
  "activities": {
    "sleep_hours": 7.5,
    "activity_level": "moderate"
  },
  "survey": {
    "mood_today": "excellent"
  }
}
```

**Response:**
```json
{
  "sentiment_score": 0.75,
  "timestamp": "2025-01-15T10:30:00.123456"
}
```

**Error Response:**
```json
{
  "error": "Error message description"
}
```
Status Code: 400

---

## 📁 Project Structure

```
mental_health_prediction_model/
│
├── app.py                          # Main Flask application
├── app_enhanced.py                 # Enhanced version with additional features
├── sentiment_analyzer.py           # Sentiment analysis module
├── models.py                        # Model training and utilities
├── config.py                        # Configuration settings
├── security_privacy.py              # Security and privacy utilities
├── error_handling.py                # Error handling utilities
├── logging_config.py                # Logging configuration
├── medical_guidance.py              # Medical guidance utilities
├── performance_tests.py             # Performance testing scripts
├── test_app.py                      # Application tests
│
├── index.html                       # Main prediction interface
├── sentiment_calculator.html        # Sentiment calculator interface
│
├── mental_health_model_final.pkl    # Trained XGBoost model
├── scaler_final.pkl                 # Data scaler for preprocessing
├── le_gender_final.pkl              # Gender label encoder
├── le_target_final.pkl              # Target label encoder
│
├── mental_health_dataset.csv        # Original dataset
├── mental_health_dataset_improved.csv # Improved dataset
│
├── requirements.txt                 # Original requirements
├── requirements_updated.txt         # Updated requirements (use this)
├── runtime.txt                      # Python runtime version
│
├── Dockerfile                       # Docker configuration
├── docker-compose.yml               # Docker Compose configuration
├── Procfile                         # Process file for deployment
│
├── README.md                        # This file
├── LICENSE                          # License file
├── IMPLEMENTATION_SUMMARY.md        # Implementation details
├── SENTIMENT_INTEGRATION_SUMMARY.md # Sentiment integration guide
├── SENTIMENT_SCORE_GUIDE.md         # Sentiment score guide
│
└── .gitignore                       # Git ignore rules
```

## 🔬 Model Details

### Algorithm
- **XGBoost Classifier**: Gradient boosting decision tree ensemble
- **Preprocessing**: StandardScaler for feature normalization
- **Encoding**: Label encoding for categorical variables

### Features
The model uses 7 input features:
1. Sentiment Score (0-1 scale)
2. Heart Rate Variability (HRV)
3. Sleep Hours
4. Activity (steps per day)
5. Age
6. Gender (encoded)
7. Work/Study Hours

### Performance
The model provides probability distributions across three classes:
- Low Mental Health
- Moderate Mental Health
- High Mental Health

**Note**: Model performance may vary based on input data quality. This is a predictive tool and should not replace professional medical advice.

## 🌐 Deployment

### Using Gunicorn (Production)

```bash
gunicorn app:app --bind 0.0.0.0:5000 --workers 4
```

### Using Docker

1. **Build the image:**
```bash
docker build -t mental-health-app .
```

2. **Run the container:**
```bash
docker run -p 5000:5000 mental-health-app
```

### Using Docker Compose

```bash
docker-compose up -d
```

### Platform-Specific Deployment

#### Heroku
1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Deploy: `git push heroku main`

#### Render
1. Connect GitHub repository
2. Select "Web Service"
3. Build command: `pip install -r requirements_updated.txt`
4. Start command: `gunicorn app:app`
5. Set Python version in `runtime.txt`

#### Railway
1. Connect GitHub repository
2. Railway auto-detects Python
3. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`

## 🔧 Troubleshooting

### Common Issues

**1. ModuleNotFoundError**
```
Solution: Ensure all dependencies are installed:
pip install -r requirements_updated.txt
```

**2. FileNotFoundError for .pkl files**
```
Solution: Verify all required .pkl files are in the project root directory
```

**3. Port already in use**
```
Solution: Change port in app.py:
app.run(debug=True, host='0.0.0.0', port=5001)
```

**4. Version warnings (XGBoost/scikit-learn)**
```
These are warnings, not errors. The model will still work, but consider 
re-saving models with current versions for optimal compatibility.
```

**5. Template not found**
```
Solution: Ensure index.html and sentiment_calculator.html are in the 
project root directory (or adjust template_folder in Flask app)
```

### Getting Help

If you encounter issues:
1. Check that all dependencies are installed correctly
2. Verify all required files are present
3. Review error messages in the terminal
4. Ensure Python version is 3.8 or higher

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines
- Follow PEP 8 style guide
- Add comments for complex logic
- Update documentation for new features
- Write tests for new functionality

## ⚠️ Important Disclaimers

- **Not a Medical Device**: This tool is for informational purposes only
- **No Medical Advice**: Does not provide, replace, or substitute professional medical advice
- **Professional Consultation**: Always consult qualified healthcare professionals for mental health concerns
- **High Risk**: If you or someone you know is in crisis, contact emergency services immediately
- **Data Privacy**: Be mindful of data privacy when deploying this application

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- XGBoost team for the excellent machine learning library
- Flask community for the robust web framework
- Contributors and open-source community

## 📧 Contact & Support

For questions, issues, or contributions:
- **Repository**: [GitHub Issues](https://github.com/Shambhujadhav4/mental_health_prediction_model/issues)
- **Fork**: Feel free to fork and customize for your needs

---

**Made with ❤️ for better mental health awareness**

*Remember: Your mental health matters. If you're struggling, please reach out to qualified professionals or crisis hotlines in your area.*
