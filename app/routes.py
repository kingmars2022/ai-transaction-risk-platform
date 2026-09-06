from flask import Blueprint, current_app, jsonify, render_template, request
from sqlalchemy import text

from .extensions import db
from .ml import predict_risk
from .models import InferenceJob, Prediction
from .openapi import openapi_spec
from .queue import publish_job
from .schemas import validate_transaction

api = Blueprint("api", __name__)

@api.get("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "ok", "database": "ok"})
    except Exception:
        return jsonify({"status": "degraded", "database": "unavailable"}), 503

@api.get("/")
def dashboard():
    return render_template("dashboard.html")

def save_prediction(transaction, risk_score):
    threshold = current_app.config["HIGH_RISK_THRESHOLD"]

    prediction = Prediction(
        **transaction,
        risk_score=risk_score,
        is_high_risk=risk_score >= threshold,
    )

    db.session.add(prediction)
    db.session.commit()
    return prediction

@api.post("/api/v1/predict")
def predict():
    transaction, error = validate_transaction(request.get_json(silent=True))

    if error:
        return jsonify({"error": error}), 400

    risk_score = predict_risk(transaction, current_app.config["MODEL_PATH"])
    prediction = save_prediction(transaction, risk_score)

    return jsonify({
        "prediction_id": prediction.id,
        "risk_score": round(prediction.risk_score, 6),
        "is_high_risk": prediction.is_high_risk,
    }), 201

@api.post("/api/v1/jobs")
def create_job():
    transaction, error = validate_transaction(request.get_json(silent=True))

    if error:
        return jsonify({"error": error}), 400

    job = InferenceJob(status="queued", request_json=transaction)
    db.session.add(job)
    db.session.commit()

    try:
        publish_job(job.id)
    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)
        db.session.commit()
        return jsonify(job.to_dict()), 503

    return jsonify(job.to_dict()), 202

@api.get("/api/v1/jobs/<job_id>")
def get_job(job_id):
    job = db.session.get(InferenceJob, job_id)

    if job is None:
        return jsonify({"error": "Job not found"}), 404

    return jsonify(job.to_dict())

@api.get("/api/v1/predictions")
def list_predictions():
    rows = Prediction.query.order_by(Prediction.id.desc()).limit(100).all()

    return jsonify({
        "count": len(rows),
        "predictions": [row.to_dict() for row in rows],
    })

@api.get("/api/v1/metrics")
def metrics():
    predictions = Prediction.query.order_by(Prediction.id.desc()).limit(100).all()
    jobs = InferenceJob.query.order_by(InferenceJob.updated_at.desc()).limit(100).all()

    risk_buckets = {
        "low": 0,
        "medium": 0,
        "high": 0,
    }
    for prediction in predictions:
        if prediction.risk_score < 0.35:
            risk_buckets["low"] += 1
        elif prediction.risk_score < current_app.config["HIGH_RISK_THRESHOLD"]:
            risk_buckets["medium"] += 1
        else:
            risk_buckets["high"] += 1

    job_status = {}
    for job in jobs:
        job_status[job.status] = job_status.get(job.status, 0) + 1

    return jsonify({
        "prediction_count": len(predictions),
        "high_risk_count": sum(1 for row in predictions if row.is_high_risk),
        "average_risk_score": round(
            sum(row.risk_score for row in predictions) / len(predictions),
            6,
        ) if predictions else 0.0,
        "risk_buckets": risk_buckets,
        "job_status": job_status,
        "recent_predictions": [row.to_dict() for row in predictions[:10]],
    })

@api.get("/api/v1/openapi.json")
def get_openapi_spec():
    return jsonify(openapi_spec())
