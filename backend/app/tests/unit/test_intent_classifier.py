import pytest
from app.services.ai.assistant.intent_classifier import IntentClassifier

def test_intent_classifier_health_check():
    classifier = IntentClassifier()
    result = classifier.classify("Why is my EC2 unhealthy?")
    assert result["intent"] == "HEALTH_CHECK"
    assert result["confidence"] > 0.8

def test_intent_classifier_cost_analysis():
    classifier = IntentClassifier()
    result = classifier.classify("What is my AWS bill?")
    assert result["intent"] == "COST_ANALYSIS"


def test_intent_classifier_security():
    classifier = IntentClassifier()
    result = classifier.classify("Can you audit the security of my S3 bucket?")
    assert result["intent"] == "SECURITY"
    assert result["confidence"] > 0.8

