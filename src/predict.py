import sys
from pathlib import Path
import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from preprocessing import add_features

MODEL_PATH = PROJECT_ROOT / "models" / "credit_scoring_model.pkl"
_cached_model = None


def get_model():
    """Load model lazily to prevent import-time side-effects."""
    global _cached_model
    if _cached_model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")
        _cached_model = joblib.load(MODEL_PATH)
    return _cached_model


def predict(applicant: dict, threshold: float = 0.5):
    """Predict creditworthiness for an applicant dictionary."""
    model = get_model()
    df = add_features(pd.DataFrame([applicant]))
    proba_good = float(model.predict_proba(df)[0][1])
    label = "Good credit" if proba_good >= threshold else "Bad credit"
    return label, proba_good


if __name__ == "__main__":
    sample = {
        "checking_status": "A11",
        "duration_months": 24,
        "credit_history": "A32",
        "purpose": "A43",
        "credit_amount": 3000,
        "savings": "A61",
        "employment_since": "A73",
        "installment_rate": 3,
        "personal_status": "A93",
        "other_debtors": "A101",
        "residence_since": 2,
        "property": "A121",
        "age": 35,
        "other_installments": "A143",
        "housing": "A152",
        "existing_credits": 1,
        "job": "A173",
        "dependents": 1,
        "telephone": "A192",
        "foreign_worker": "A201",
    }
    label, proba = predict(sample)
    print(f"Prediction: {label}")
    print(f"Probability of good credit: {proba:.2%}")