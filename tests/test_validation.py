import unittest
import importlib.util
from pathlib import Path

schema_path = Path(__file__).parents[1] / "app" / "schemas.py"
spec = importlib.util.spec_from_file_location("schemas", schema_path)
schemas = importlib.util.module_from_spec(spec)
spec.loader.exec_module(schemas)

class ValidationTests(unittest.TestCase):
    def test_valid_transaction(self):
        payload = {
            "amount": 100.0,
            "old_balance": 500.0,
            "new_balance": 400.0,
            "transaction_type": "TRANSFER",
            "hour": 12,
        }

        result, error = schemas.validate_transaction(payload)
        self.assertIsNone(error)
        self.assertEqual(result["transaction_type"], "TRANSFER")

    def test_invalid_hour(self):
        payload = {
            "amount": 100.0,
            "old_balance": 500.0,
            "new_balance": 400.0,
            "transaction_type": "TRANSFER",
            "hour": 30,
        }

        result, error = schemas.validate_transaction(payload)
        self.assertIsNone(result)
        self.assertIn("hour", error)

    def test_missing_fields(self):
        result, error = schemas.validate_transaction({"amount": 100.0})

        self.assertIsNone(result)
        self.assertIn("Missing fields", error)

    def test_rejects_unknown_transaction_type(self):
        payload = {
            "amount": 100.0,
            "old_balance": 500.0,
            "new_balance": 400.0,
            "transaction_type": "WIRE",
            "hour": 12,
        }

        result, error = schemas.validate_transaction(payload)
        self.assertIsNone(result)
        self.assertIn("transaction_type", error)

if __name__ == "__main__":
    unittest.main()
