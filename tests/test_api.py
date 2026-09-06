import unittest
from unittest.mock import patch

try:
    from app import create_app
    from app.extensions import db
    from app.models import InferenceJob, Prediction
except ModuleNotFoundError as exc:
    create_app = None
    db = None
    InferenceJob = None
    Prediction = None
    MISSING_DEPENDENCY = exc.name
else:
    MISSING_DEPENDENCY = None


VALID_TRANSACTION = {
    "amount": 950.0,
    "old_balance": 1200.0,
    "new_balance": 250.0,
    "transaction_type": "TRANSFER",
    "hour": 2,
}


class ApiTests(unittest.TestCase):
    def setUp(self):
        if MISSING_DEPENDENCY:
            self.skipTest(f"Missing dependency: {MISSING_DEPENDENCY}")

        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "HIGH_RISK_THRESHOLD": 0.65,
        })
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_health_returns_ok_when_database_is_available(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["database"], "ok")

    def test_dashboard_page_loads(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AI Transaction Risk Platform", response.data)

    @patch("app.routes.predict_risk", return_value=0.87)
    def test_predict_persists_prediction(self, mock_predict):
        response = self.client.post("/api/v1/predict", json=VALID_TRANSACTION)
        data = response.get_json()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["risk_score"], 0.87)
        self.assertTrue(data["is_high_risk"])
        self.assertEqual(data["prediction_id"], 1)
        mock_predict.assert_called_once()

        list_response = self.client.get("/api/v1/predictions")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.get_json()["count"], 1)

    def test_predict_rejects_invalid_payload(self):
        response = self.client.post("/api/v1/predict", json={"amount": 100})

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    @patch("app.routes.publish_job")
    def test_create_job_queues_valid_transaction(self, mock_publish):
        response = self.client.post("/api/v1/jobs", json=VALID_TRANSACTION)
        data = response.get_json()

        self.assertEqual(response.status_code, 202)
        self.assertEqual(data["status"], "queued")
        self.assertIn("job_id", data)
        mock_publish.assert_called_once_with(data["job_id"])

    def test_get_missing_job_returns_404(self):
        response = self.client.get("/api/v1/jobs/missing-job")

        self.assertEqual(response.status_code, 404)

    def test_openapi_spec_documents_core_endpoints(self):
        response = self.client.get("/api/v1/openapi.json")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["info"]["title"], "AI Transaction Risk Platform API")
        self.assertIn("/", data["paths"])
        self.assertIn("/api/v1/predict", data["paths"])
        self.assertIn("/api/v1/jobs", data["paths"])
        self.assertIn("/api/v1/metrics", data["paths"])

    def test_metrics_returns_prediction_and_job_summary(self):
        with self.app.app_context():
            prediction = Prediction(
                amount=1000.0,
                old_balance=1200.0,
                new_balance=200.0,
                transaction_type="TRANSFER",
                hour=1,
                risk_score=0.91,
                is_high_risk=True,
            )
            job = InferenceJob(status="completed", request_json=VALID_TRANSACTION)
            db.session.add_all([prediction, job])
            db.session.commit()

        response = self.client.get("/api/v1/metrics")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["prediction_count"], 1)
        self.assertEqual(data["high_risk_count"], 1)
        self.assertEqual(data["risk_buckets"]["high"], 1)
        self.assertEqual(data["job_status"]["completed"], 1)


if __name__ == "__main__":
    unittest.main()
