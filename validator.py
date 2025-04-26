import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import IsolationForest
import joblib
from config import CONFIDENCE_THRESHOLDS

class CommandValidator:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 3))
        self.model = IsolationForest(contamination=0.1)
        self.bad_patterns = open("data/b4d.txt").read().splitlines()

    def train(self, good_commands):
        texts = good_commands + self.bad_patterns
        X = self.vectorizer.fit_transform(texts)
        labels = np.array([1]*len(good_commands) + [-1]*len(self.bad_patterns))
        self.model.fit(X, labels)
        joblib.dump((self.vectorizer, self.model), "data/model/validator.joblib")

    def validate(self, command):
        X = self.vectorizer.transform([command] + self.bad_patterns)
        similarity = cosine_similarity(X)[0][1:]
        anomaly_score = self.model.decision_function(X[0:1])[0]
        confidence = (1 - (anomaly_score + 1)/2) * 100
        
        return {
            "decision": "block" if confidence > CONFIDENCE_THRESHOLDS["block"] 
                     else "warn" if confidence > CONFIDENCE_THRESHOLDS["warn"] 
                     else "allow",
            "confidence": confidence,
            "closest_match": self.bad_patterns[np.argmax(similarity)]
        }