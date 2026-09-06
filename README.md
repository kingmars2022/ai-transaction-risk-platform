# AI Transaction Risk Platform

AI Transaction Risk Platform is a portfolio backend project that simulates how a payment or banking system can score transaction risk.

The user submits a transaction from the browser, the Flask API validates the request, a machine-learning model returns a risk score, PostgreSQL stores the result, and the dashboard displays prediction metrics. The same transaction can also be submitted as an asynchronous job through RabbitMQ and processed by a Python worker.

## What This Project Does

This project is not just a static dashboard. It provides an end-to-end workflow:

```text
Browser transaction form
  |
  v
Flask REST API
  |
  +--> synchronous prediction --> ML model --> PostgreSQL
  |
  +--> asynchronous job --> RabbitMQ --> Python worker --> ML model --> PostgreSQL
  |
  v
Dashboard metrics and recent prediction table
```

Example transaction input:

```json
{
  "amount": 1500.0,
  "old_balance": 1600.0,
  "new_balance": 100.0,
  "transaction_type": "CASH_OUT",
  "hour": 1
}
```

Example output:

```json
{
  "prediction_id": 1,
  "risk_score": 0.513,
  "is_high_risk": false
}
```

## Main Features

- Browser-based transaction input form
- Synchronous risk scoring endpoint
- Asynchronous job endpoint using RabbitMQ
- Python worker for queued prediction jobs
- PostgreSQL persistence for prediction results and job status
- Machine-learning risk scoring with scikit-learn
- Dashboard for prediction count, high-risk count, average risk, risk distribution, job status, and recent predictions
- OpenAPI JSON documentation endpoint
- Docker Compose setup for API, worker, PostgreSQL, and RabbitMQ
- Unit tests for validation and API behavior
- GitHub Actions workflow for automated test execution
- Ansible deployment example

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Python, Flask |
| Machine learning | scikit-learn, joblib, NumPy |
| Database | PostgreSQL |
| Async processing | RabbitMQ, Python worker |
| Frontend dashboard | HTML, CSS, JavaScript |
| Containers | Docker, Docker Compose |
| Testing | unittest |
| CI | GitHub Actions |

## Project Structure

```text
.
├── app/
│   ├── routes.py          # Flask routes for prediction, jobs, metrics, dashboard, OpenAPI
│   ├── models.py          # SQLAlchemy models for predictions and inference jobs
│   ├── schemas.py         # Transaction request validation
│   ├── ml.py              # Model loading and prediction logic
│   ├── queue.py           # RabbitMQ publishing
│   ├── openapi.py         # OpenAPI JSON specification
│   ├── templates/         # Browser dashboard HTML
│   └── static/            # Dashboard CSS and JavaScript
├── worker/
│   └── worker.py          # RabbitMQ consumer and async prediction processor
├── scripts/
│   ├── train_model.py     # Synthetic model training
│   └── wait_for_services.py
├── tests/
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.worker
└── README.md
```

## Requirements

- Docker Desktop
- Docker Compose

Make sure Docker Desktop is running before starting the project. If Docker is not running, you may see:

```text
Cannot connect to the Docker daemon
```

Open Docker Desktop, wait until it is fully started, and then run the commands below.

## Run The Project

From the project root:

```bash
cd /Users/siguangzhao/Documents/GitHub/my-projects/ai/ai-transaction-risk-platform
docker compose up --build
```

Keep this terminal open while using the application.

Open the dashboard:

```text
http://localhost:5001
```

RabbitMQ management UI:

```text
http://localhost:15672
```

RabbitMQ login:

```text
guest / guest
```

## How To Use The Dashboard

1. Open `http://localhost:5001`.
2. Enter transaction values in the form.
3. Click `Run Prediction` for synchronous scoring.
4. Review the risk score and high-risk decision in `Prediction Output`.
5. Click `Queue Async Job` to submit the transaction through RabbitMQ.
6. Watch the metrics, job status, risk distribution, and recent predictions update.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Browser dashboard |
| `GET` | `/health` | API and database health check |
| `POST` | `/api/v1/predict` | Run synchronous transaction risk scoring |
| `POST` | `/api/v1/jobs` | Queue asynchronous prediction job |
| `GET` | `/api/v1/jobs/<job_id>` | Read async job status and result |
| `GET` | `/api/v1/predictions` | List recent persisted predictions |
| `GET` | `/api/v1/metrics` | Dashboard metrics |
| `GET` | `/api/v1/openapi.json` | OpenAPI documentation |

## Test With curl

Health check:

```bash
curl http://localhost:5001/health
```

Synchronous prediction:

```bash
curl -X POST http://localhost:5001/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 950.0,
    "old_balance": 1200.0,
    "new_balance": 250.0,
    "transaction_type": "TRANSFER",
    "hour": 2
  }'
```

Asynchronous prediction:

```bash
curl -X POST http://localhost:5001/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1500.0,
    "old_balance": 1600.0,
    "new_balance": 100.0,
    "transaction_type": "CASH_OUT",
    "hour": 1
  }'
```

Query an async job:

```bash
curl http://localhost:5001/api/v1/jobs/YOUR_JOB_ID
```

OpenAPI:

```bash
curl http://localhost:5001/api/v1/openapi.json
```

## Stop And Reset

Stop the containers:

```bash
docker compose down
```

Stop and clear the database volume:

```bash
docker compose down -v
```

## Run Tests Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
python -m unittest discover -s tests
```

If dependencies are not installed, API tests may be skipped locally. The GitHub Actions workflow installs dependencies and runs the test suite in CI.

## Troubleshooting

### Docker daemon is not running

Start Docker Desktop, wait for it to finish loading, and rerun:

```bash
docker compose up --build
```

### Dashboard does not show the latest changes

Rebuild the containers:

```bash
docker compose down
docker compose up --build
```

Then hard refresh the browser with `Cmd + Shift + R`.

### Port 5001 is already in use

Stop the process using port `5001`, or change the host port in `docker-compose.yml`.

## Resume Bullets

**AI Transaction Risk Platform** - Python, Flask, PostgreSQL, RabbitMQ, scikit-learn, Docker, GitHub Actions

- Built a Flask REST API for transaction risk scoring and persisted prediction results in PostgreSQL.
- Implemented RabbitMQ-based asynchronous inference workflows with a Python worker for queued transaction processing.
- Added a browser-based transaction input workflow, monitoring dashboard, OpenAPI documentation, and unit tests covering request validation and core API behavior.
- Containerized the API, worker, PostgreSQL, and RabbitMQ services with Docker Compose and configured a GitHub Actions test workflow.
