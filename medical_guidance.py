from datetime import datetime
from flask import jsonify, request
import logging

class MedicalGuidance:
    """Class to handle medical disclaimers and professional guidance"""
    
    # Crisis hotlines by country
    CRISIS_HOTLINES = {
        'US': {
            'number': '988',
            'name': 'Suicide & Crisis Lifeline',
            'website': 'https://988lifeline.org/',
            'text': 'Text HOME to 741741'
        },
        'UK': {
            'number': '116 123',
            'name': 'Samaritans',
            'website': 'https://www.samaritans.org/',
            'text': 'Text SHOUT to 85258'
        },
        'CA': {
            'number': '1-833-456-4566',
            'name': 'Crisis Services Canada',
            'website': 'https://www.crisisservicescanada.ca/',
            'text': 'Text 45645'
        },
        'AU': {
            'number': '13 11 14',
            'name': 'Lifeline Australia',
            'website': 'https://www.lifeline.org.au/',
            'text': 'Text 0477 13 11 14'
        },
        'IN': {
            'number': '9152987821',
            'name': 'KIRAN Mental Health Helpline',
            'website': 'https://www.nimhans.ac.in/',
            'text': 'Text 9152987821'
        }
    }
    
    # Professional resources
    PROFESSIONAL_RESOURCES = {
        'psychologists': {
            'description': 'Licensed psychologists who specialize in mental health assessment and therapy',
            'when_to_see': 'For ongoing therapy, psychological testing, and treatment planning',
            'how_to_find': 'Check with your insurance provider or use Psychology Today\'s therapist finder'
        },
        'psychiatrists': {
            'description': 'Medical doctors who specialize in mental health and can prescribe medication',
            'when_to_see': 'For medication evaluation, severe mental health conditions, or when therapy alone isn\'t sufficient',
            'how_to_find': 'Ask your primary care doctor for a referral or check with your insurance provider'
        },
        'therapists': {
            'description': 'Licensed mental health professionals providing talk therapy',
            'when_to_see': 'For ongoing support, coping strategies, and emotional processing',
            'how_to_find': 'Use online directories like Psychology Today or ask for recommendations from friends/family'
        },
        'counselors': {
            'description': 'Mental health counselors providing support and guidance',
            'when_to_see': 'For general mental health support, life transitions, and stress management',
            'how_to_find': 'Check with community mental health centers or employee assistance programs'
        }
    }
    
    # Self-care recommendations by mental health status
    SELF_CARE_RECOMMENDATIONS = {
        'Low': {
            'immediate': [
                'Reach out to a trusted friend or family member',
                'Contact a mental health professional immediately',
                'Consider calling a crisis hotline',
                'Remove yourself from any harmful situations'
            ],
            'daily': [
                'Maintain a regular sleep schedule',
                'Eat regular, nutritious meals',
                'Get some sunlight and fresh air',
                'Practice deep breathing exercises',
                'Limit alcohol and caffeine intake'
            ],
            'weekly': [
                'Schedule an appointment with a mental health professional',
                'Engage in gentle physical activity',
                'Connect with supportive people',
                'Practice mindfulness or meditation',
                'Consider joining a support group'
            ]
        },
        'Moderate': {
            'immediate': [
                'Practice stress-reduction techniques',
                'Take breaks when feeling overwhelmed',
                'Talk to someone you trust about how you\'re feeling'
            ],
            'daily': [
                'Maintain regular sleep and meal schedules',
                'Engage in moderate physical activity',
                'Practice relaxation techniques',
                'Limit screen time before bed',
                'Stay hydrated'
            ],
            'weekly': [
                'Consider scheduling a mental health check-in',
                'Engage in enjoyable activities',
                'Connect with friends or family',
                'Practice self-compassion',
                'Monitor your stress levels'
            ]
        },
        'High': {
            'immediate': [
                'Continue your current healthy habits',
                'Share your positive strategies with others',
                'Consider volunteering or helping others'
            ],
            'daily': [
                'Maintain your healthy routines',
                'Stay physically active',
                'Practice gratitude',
                'Get adequate sleep',
                'Eat a balanced diet'
            ],
            'weekly': [
                'Continue regular mental health maintenance',
                'Engage in meaningful activities',
                'Nurture your relationships',
                'Set and work toward personal goals',
                'Consider mentoring others'
            ]
        }
    }
    
    @staticmethod
    def get_crisis_resources(country_code='US'):
        """Get crisis resources for a specific country"""
        return MedicalGuidance.CRISIS_HOTLINES.get(country_code, MedicalGuidance.CRISIS_HOTLINES['US'])
    
    @staticmethod
    def get_professional_guidance(profession_type='psychologists'):
        """Get information about professional mental health resources"""
        return MedicalGuidance.PROFESSIONAL_RESOURCES.get(profession_type, {})
    
    @staticmethod
    def get_self_care_recommendations(status):
        """Get self-care recommendations based on mental health status"""
        return MedicalGuidance.SELF_CARE_RECOMMENDATIONS.get(status, {})
    
    @staticmethod
    def create_enhanced_disclaimer(prediction, confidence, probabilities):
        """Create enhanced medical disclaimer based on prediction"""
        disclaimers = []
        
        # Base disclaimer
        base_disclaimer = (
            "⚠️ IMPORTANT MEDICAL DISCLAIMER: This prediction is for informational purposes only "
            "and should not replace professional medical advice, diagnosis, or treatment. "
            "Mental health assessment requires evaluation by qualified healthcare professionals."
        )
        disclaimers.append(base_disclaimer)
        
        # Confidence-based disclaimer
        if confidence < 0.7:
            disclaimers.append(
                f"⚠️ LOW CONFIDENCE WARNING: This prediction has low confidence ({confidence:.1%}). "
                "Please consult a mental health professional for an accurate assessment."
            )
        
        # Status-specific disclaimers
        if prediction == "Low":
            disclaimers.append(
                "🚨 CRISIS ALERT: If you're experiencing thoughts of self-harm or suicide, "
                "please seek immediate help from emergency services or a crisis hotline."
            )
        elif prediction == "Moderate":
            disclaimers.append(
                "💡 RECOMMENDATION: Consider scheduling a check-in with a mental health professional "
                "to discuss your current mental health status and develop coping strategies."
            )
        elif prediction == "High":
            disclaimers.append(
                "✅ POSITIVE STATUS: While your mental health appears stable, continue maintaining "
                "healthy habits and consider supporting others who may be struggling."
            )
        
        # General guidance
        disclaimers.append(
            "📞 SUPPORT AVAILABLE: Remember that help is always available. "
            "Don't hesitate to reach out to mental health professionals, crisis hotlines, "
            "or trusted friends and family members."
        )
        
        return "\n\n".join(disclaimers)
    
    @staticmethod
    def log_crisis_detection(user_id, prediction_data, ip_address):
        """Log crisis detection for monitoring and intervention"""
        logger = logging.getLogger('crisis_detection')
        
        crisis_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'prediction': prediction_data.get('prediction'),
            'confidence': prediction_data.get('confidence'),
            'probabilities': prediction_data.get('probabilities'),
            'ip_address': ip_address,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'crisis_level': 'HIGH' if prediction_data.get('prediction') == 'Low' else 'MODERATE'
        }
        
        logger.critical(f"CRISIS DETECTED: {crisis_data}")
        
        # In a real application, you might want to:
        # 1. Send alerts to mental health professionals
        # 2. Trigger automated interventions
        # 3. Log to a separate crisis monitoring system
        
        return crisis_data

def create_professional_guidance_response(prediction, confidence, country_code='US'):
    """Create comprehensive professional guidance response"""
    
    # Get crisis resources
    crisis_resources = MedicalGuidance.get_crisis_resources(country_code)
    
    # Get self-care recommendations
    self_care = MedicalGuidance.get_self_care_recommendations(prediction)
    
    # Create enhanced disclaimer
    disclaimer = MedicalGuidance.create_enhanced_disclaimer(prediction, confidence, {})
    
    # Professional guidance based on prediction
    if prediction == "Low":
        professional_guidance = {
            "urgency": "HIGH",
            "recommendation": "Seek immediate professional help",
            "next_steps": [
                "Contact a mental health professional today",
                "Consider calling a crisis hotline",
                "Inform a trusted friend or family member",
                "Remove yourself from harmful situations"
            ],
            "crisis_hotline": crisis_resources,
            "self_care": self_care
        }
    elif prediction == "Moderate":
        professional_guidance = {
            "urgency": "MODERATE",
            "recommendation": "Schedule a mental health check-in",
            "next_steps": [
                "Schedule an appointment with a mental health professional within the week",
                "Practice stress-reduction techniques",
                "Monitor your mental health daily",
                "Maintain healthy routines"
            ],
            "crisis_hotline": crisis_resources,
            "self_care": self_care
        }
    else:  # High
        professional_guidance = {
            "urgency": "LOW",
            "recommendation": "Continue maintaining healthy habits",
            "next_steps": [
                "Continue your current mental health practices",
                "Consider regular mental health check-ins",
                "Support others who may be struggling",
                "Maintain your healthy lifestyle"
            ],
            "crisis_hotline": crisis_resources,
            "self_care": self_care
        }
    
    return {
        "disclaimer": disclaimer,
        "professional_guidance": professional_guidance,
        "timestamp": datetime.utcnow().isoformat()
    }
