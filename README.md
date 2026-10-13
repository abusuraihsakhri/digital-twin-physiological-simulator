# Digital Twin Physiological Simulator

A research-oriented **rule-based parameter evaluation** repository with a standalone browser explorer, two Python command-line evaluators, and a FastAPI audit endpoint.

**Scope:** The current code compares numeric inputs against fixed thresholds and checks status keywords. Despite historical class names, it does **not** implement an eight-compartment cardiovascular/renal ODE, ventricular elastance solver, patient-specific digital twin, or medically validated decision support. Thresholds are synthetic demonstrations, not physiological reference ranges. **Do not use for clinical decisions or provide patient information.**

## Browser application

The browser app is in [`web/`](web/). It reproduces the `agents/workers.py` rules locally: primary value > 25, secondary value > 12, a synthetic critical flag, and anomaly tokens in a descriptor. It displays the resulting classification, explains triggered checks, and exports a JSON report.

The browser application runs without Python, Pyodide, a backend, external packages, or API calls. It keeps results in the current tab and does not persist input data or transmit it to the server. JSON export saves a local file; it is **not an HMAC-signed audit record**.

For local development, serve the repository directory using:

```bash
python -m http.server 8001
```

Then open `http://localhost:8001/`. A simple `file://` page may block ES-module imports; use an HTTP static server or GitHub Pages. Recent Chromium, Firefox, and Safari browsers support the required JavaScript modules.

## Python usage

Requires Python 3.9+ (CI verifies 3.10–3.12).

```bash
python -m pip install -e '.[api]'
digital-twin-physiological-simulator audit --task-id DEMO-01 --target SYNTHETIC-01 --primary 28.5 --secondary 14.2
digital-twin-physiological-simulator batch -i sample.csv -o results.csv
digital-twin-physiological-simulator verify-audit
digital-twin-physiological-simulator serve --host 127.0.0.1 --port 8000
```

The installed command calls the `agents` evaluator, which uses primary > 25 and secondary > 12. The separate `python -m physiotwin_simulator.cli` command runs the legacy `physiotwin_simulator` evaluator, which uses primary > 25 and secondary > 10. These are different demonstration rule sets, **not** alternate ODE solvers.

Batch CSV columns are `task_id`, `target_identifier`, `primary_metric`, `secondary_metric`, `status_descriptor`, and `is_critical_flag`. Boolean strings `true/false`, `yes/no`, and `1/0` are recognized; invalid values fail with an error.

With the API installed, inspect `http://127.0.0.1:8000/docs`, `GET /health`, `GET /metrics`, `POST /api/audit`, `POST /api/chat`, and `GET /api/audit/logs`. The browser application deliberately does not call this backend. The chat endpoint is a **mock text responder**, not a connected LLM.

`python simulator.py 1000` performs synthetic *task throughput* testing, not longitudinal physiological simulation.

## Security and limitations

The Python audit component uses an in-memory HMAC-SHA256 chain and verifies both chain linkage and message signatures. Set `AUDIT_SECRET_KEY` to a strong, confidential value to use a consistent signing key; otherwise an ephemeral key is generated. Audit entries are not persisted, and the chain alone cannot prove that records were not truncated or deleted. It must **not** be described as a durable compliance-grade record.

The identifier guard uses regular expressions to detect some sensitive identifiers. It is **not** a complete de-identification system, privacy certification, or a guarantee of zero protected health information. The API has no authentication or deployment-grade access controls; run it only in a trusted local/test environment with synthetic data.

Optional container execution:

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
```

Compose binds port 8000 to localhost by default. Do not publish the service to the Internet without adding appropriate authentication, access controls, and deployment security.

## Testing

```bash
python -m pip install -e '.[api,test]'
python -m pytest -q
node --check web/app.mjs
node --test web/rules.test.mjs
python -m pip check
```

GitHub Actions runs package installation, Python tests, and browser-rule tests on Python 3.10–3.12. The browser uses JavaScript rather than WebAssembly Python because its current calculations are simple deterministic rules.

## Structure and license

`agents/` contains the primary Pydantic-based audit workers, audit-chain logic, and API. `physiotwin_simulator/` contains the separate legacy evaluator. `web/` contains the static interface and rule tests; `enrichment.py` contains experimental illustrative feature classes. See [MIT License](LICENSE).
