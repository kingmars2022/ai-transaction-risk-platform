ALLOWED_TYPES = {"PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"}

def validate_transaction(payload):
    if not isinstance(payload, dict):
        return None, "JSON object required"

    required = ["amount", "old_balance", "new_balance", "transaction_type", "hour"]
    missing = [field for field in required if field not in payload]
    if missing:
        return None, "Missing fields: " + ", ".join(missing)

    try:
        amount = float(payload["amount"])
        old_balance = float(payload["old_balance"])
        new_balance = float(payload["new_balance"])
        hour = int(payload["hour"])
    except (TypeError, ValueError):
        return None, "amount, old_balance, new_balance, and hour must be numeric"

    transaction_type = str(payload["transaction_type"]).upper().strip()

    if amount < 0 or old_balance < 0 or new_balance < 0:
        return None, "Monetary values must be non-negative"

    if not 0 <= hour <= 23:
        return None, "hour must be between 0 and 23"

    if transaction_type not in ALLOWED_TYPES:
        return None, "transaction_type must be one of: " + ", ".join(sorted(ALLOWED_TYPES))

    return {
        "amount": amount,
        "old_balance": old_balance,
        "new_balance": new_balance,
        "transaction_type": transaction_type,
        "hour": hour,
    }, None
