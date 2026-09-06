def openapi_spec():
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "AI Transaction Risk Platform API",
            "version": "1.0.0",
            "description": "REST API for synchronous and asynchronous transaction risk scoring.",
        },
        "paths": {
            "/": {
                "get": {
                    "summary": "Render prediction monitoring dashboard",
                    "responses": {"200": {"description": "Dashboard HTML returned"}},
                }
            },
            "/health": {
                "get": {
                    "summary": "Check API and database health",
                    "responses": {
                        "200": {"description": "API and database are available"},
                        "503": {"description": "Database is unavailable"},
                    },
                }
            },
            "/api/v1/predict": {
                "post": {
                    "summary": "Run synchronous transaction risk scoring",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/TransactionRequest"}
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Prediction created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PredictionResponse"}
                                }
                            },
                        },
                        "400": {"description": "Invalid transaction payload"},
                    },
                }
            },
            "/api/v1/jobs": {
                "post": {
                    "summary": "Create an asynchronous risk scoring job",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/TransactionRequest"}
                            }
                        },
                    },
                    "responses": {
                        "202": {"description": "Job queued"},
                        "400": {"description": "Invalid transaction payload"},
                        "503": {"description": "Queue unavailable"},
                    },
                }
            },
            "/api/v1/jobs/{job_id}": {
                "get": {
                    "summary": "Get asynchronous job status",
                    "parameters": [
                        {
                            "name": "job_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {"description": "Job status returned"},
                        "404": {"description": "Job not found"},
                    },
                }
            },
            "/api/v1/predictions": {
                "get": {
                    "summary": "List recent predictions",
                    "responses": {"200": {"description": "Recent predictions returned"}},
                }
            },
            "/api/v1/metrics": {
                "get": {
                    "summary": "Return dashboard metrics",
                    "responses": {"200": {"description": "Aggregated risk metrics returned"}},
                }
            },
            "/api/v1/openapi.json": {
                "get": {
                    "summary": "Return OpenAPI documentation",
                    "responses": {"200": {"description": "OpenAPI specification returned"}},
                }
            },
        },
        "components": {
            "schemas": {
                "TransactionRequest": {
                    "type": "object",
                    "required": [
                        "amount",
                        "old_balance",
                        "new_balance",
                        "transaction_type",
                        "hour",
                    ],
                    "properties": {
                        "amount": {"type": "number", "minimum": 0},
                        "old_balance": {"type": "number", "minimum": 0},
                        "new_balance": {"type": "number", "minimum": 0},
                        "transaction_type": {
                            "type": "string",
                            "enum": ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"],
                        },
                        "hour": {"type": "integer", "minimum": 0, "maximum": 23},
                    },
                },
                "PredictionResponse": {
                    "type": "object",
                    "properties": {
                        "prediction_id": {"type": "integer"},
                        "risk_score": {"type": "number"},
                        "is_high_risk": {"type": "boolean"},
                    },
                },
            }
        },
    }
