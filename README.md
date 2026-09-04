# Digital Twin Physiological Simulator

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Digital Twin Physiological Simulator** is an analytical and computational platform implementing cardiovascular & renal hemodynamic simulation with multi-agent consensus evaluation.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds.
- **Risk & Urgency Classification**: Multi-tier categorization with automated clinical/operational action recommendations.
- **Validation & Guardrails**: Rigorous input bounds checking and anomaly detection.
- **Multi-Agent Consensus**: Three specialized workers (InvariantQC, SafetyEscalation, ProtocolConformance) evaluate each task.
- **Zero-PHI Outbound Interceptor**: Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
- **Tamper-Evident HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs for every evaluation.

---

## 💻 CLI Quickstart & Usage

### Installation
```bash
pip install -e .
```

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2
```

### 2. Batch Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 3. Supervisory Chat
```bash
python cli.py chat "What is the system status?"
```

### 4. Verify Audit Trail
```bash
python cli.py verify-audit
```

### 5. Launch API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
| Parameter | Description | Default |
|:----------|:------------|:--------|
| `--task-id` | Unique task identifier | TASK-2026-001 |
| `--target` | Target entity identifier | KEY-TARGET-01 |
| `--primary` | Primary measurement value | 28.5 |
| `--secondary` | Secondary kinetic/confidence score | 14.2 |
| `--critical` | Flag for emergency escalation | False |
| `--status` | Status/phenotype descriptor | DISCORDANT |

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task identifier | Required |
| `target_identifier` | Target entity identifier | Required |
| `primary_metric` | Primary measurement value | Required |
| `secondary_metric` | Secondary kinetic/confidence score | Optional (default: 0.0) |
| `is_critical_flag` | Emergency escalation trigger | Optional (default: false) |
| `status_descriptor` | Status/phenotype descriptor | Optional (default: NOMINAL) |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Secure Key Management:** Audit signing key sourced from `AUDIT_SECRET_KEY` environment variable; ephemeral key generated with warning if unset.
* **Input Validation:** NaN and Inf values are rejected at model validation layer.
* **FastAPI REST API:** Exposes OpenAPI 3.1 REST endpoints.

### Environment Variables
| Variable | Description | Required |
|:---------|:------------|:---------|
| `AUDIT_SECRET_KEY` | Secret key for HMAC-SHA256 audit signing | No (warning if unset) |
| `MODEL_PROVIDER` | LLM provider selection | No (default: mock) |

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Run with coverage:

```bash
pytest -v --cov=agents --cov=physiotwin_simulator
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t digital-twin-physiological-simulator .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key digital-twin-physiological-simulator
```

Or using Docker Compose:

```bash
AUDIT_SECRET_KEY=your-secret-key docker-compose up -d
```

---

## 📁 Project Structure

```
digital-twin-physiological-simulator/
├── agents/                      # Core agent modules
│   ├── __init__.py
│   ├── api.py                   # FastAPI REST endpoints
│   ├── base.py                  # Security, PHI guard, audit trail
│   ├── learning.py              # Bayesian calibration engine
│   ├── llm_factory.py           # LLM client factory
│   ├── metrics.py               # Prometheus metrics collector
│   ├── models.py                # Pydantic data models
│   ├── streamer.py              # WebSocket telemetry streamer
│   ├── supervisor.py            # Multi-agent orchestrator
│   └── workers.py               # Specialized worker agents
├── physiotwin_simulator/        # PhysioTwin simulation engine
│   ├── __init__.py
│   ├── agents.py                # PhysioTwin coordinator & sub-agents
│   ├── cli.py                   # PhysioTwin CLI
│   ├── engine.py                # Core algorithmic engine
│   ├── models.py                # Data models
│   └── server.py                # FastAPI server factory
├── tests/                       # Test suite
│   ├── test_digital_twin_physiological_simulator.py
│   ├── test_edge_cases.py
│   ├── test_enrichment.py
│   └── test_physiotwin_simulator.py
├── web/
│   └── index.html               # Operations console UI
├── cli.py                       # Main CLI entry point
├── simulator.py                 # High-throughput simulation runner
├── enrichment.py                # Enrichment feature suite
├── physiotwin_simulator_app.py  # PhysioTwin CLI entry point
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
