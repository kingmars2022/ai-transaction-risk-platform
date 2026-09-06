from pathlib import Path
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

def make_training_data(n=12000, seed=42):
    rng = np.random.default_rng(seed)

    amount = rng.gamma(shape=2.0, scale=350.0, size=n)
    old_balance = rng.gamma(shape=2.5, scale=600.0, size=n)
    new_balance = np.maximum(
        old_balance - amount * rng.uniform(0.2, 1.1, size=n),
        0.0,
    )

    balance_drop = np.maximum(old_balance - new_balance, 0.0)
    amount_to_balance = amount / np.maximum(old_balance, 1.0)
    transaction_type = rng.integers(0, 5, size=n)
    hour = rng.integers(0, 24, size=n)

    logit = (
        -4.5
        + 0.0012 * amount
        + 0.9 * (amount_to_balance > 0.8)
        + 1.2 * np.isin(transaction_type, [1, 2])
        + 1.0 * np.isin(hour, [0, 1, 2, 3, 4])
        + 0.0006 * balance_drop
    )

    probability = 1.0 / (1.0 + np.exp(-logit))
    y = rng.binomial(1, np.clip(probability, 0.01, 0.99))

    X = np.column_stack([
        amount,
        old_balance,
        new_balance,
        balance_drop,
        amount_to_balance,
        transaction_type,
        hour,
    ])

    return X, y

def main():
    X, y = make_training_data()

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(max_iter=1000)),
    ])

    model.fit(X, y)

    output = Path("model/risk_model.joblib")
    output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output)

    print(f"Saved model to {output}")
    print(f"Training rows: {len(X)}")
    print(f"Positive rate: {y.mean():.3f}")

if __name__ == "__main__":
    main()
