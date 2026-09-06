from pathlib import Path
import joblib
import numpy as np

TYPE_MAP = {
    "PAYMENT": 0,
    "TRANSFER": 1,
    "CASH_OUT": 2,
    "DEBIT": 3,
    "CASH_IN": 4,
}

_model = None

def load_model(model_path):
    global _model

    if _model is None:
        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Model not found at {path}. Run scripts/train_model.py first."
            )
        _model = joblib.load(path)

    return _model

def build_features(transaction):
    old_balance = transaction["old_balance"]
    new_balance = transaction["new_balance"]
    amount = transaction["amount"]

    balance_drop = max(old_balance - new_balance, 0.0)
    amount_to_balance = amount / max(old_balance, 1.0)

    return np.array([[
        amount,
        old_balance,
        new_balance,
        balance_drop,
        amount_to_balance,
        TYPE_MAP[transaction["transaction_type"]],
        transaction["hour"],
    ]], dtype=float)

def predict_risk(transaction, model_path):
    model = load_model(model_path)
    features = build_features(transaction)
    return float(model.predict_proba(features)[0][1])
