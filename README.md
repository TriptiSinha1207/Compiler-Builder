# Config-Driven App Compiler

This repository implements a deterministic multi-stage generation pipeline for converting open-ended user instructions into a strict, validated application configuration and a runnable runtime.
Deployed link: http://compiler-builder-461674.netlify.app/

## What it includes

- `pipeline/intent.py` — intent extraction from natural language into a structured intermediate form
- `pipeline/design.py` — architecture generation for UI, API, database, auth, and business logic
- `pipeline/validator.py` — schema enforcement, cross-layer checks, and targeted repair
- `pipeline/runtime.py` — runtime engine that instantiates a working Flask app from config and simulates execution
- `pipeline/evaluator.py` — evaluation framework with 20 prompt cases, metrics, and success tracking

## How to use

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Generate a config from a prompt:

   ```bash
   python app.py generate --prompt "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics." --output app_config.json
   ```

3. Simulate the generated config:

   ```bash
   python app.py simulate --config app_config.json
   ```

4. Run the generated app runtime:

   ```bash
   python app.py run --config app_config.json --port 5000
   ```

5. Open the generated website in a browser:

   - `http://127.0.0.1:5000/` for the landing page
   - `http://127.0.0.1:5000/app` for the generated UI pages


5. Evaluate the dataset:

   ```bash
   python app.py evaluate
   ```

## Design guarantees

- Strict JSON contract via Pydantic models
- Cross-layer consistency between UI, API, DB, and auth
- Validation + repair engine for missing fields and mismatches
- Deterministic behavior through rule-based generation
- Execution awareness via runtime simulation and Flask app instantiation

## Dataset

- `data/dataset.json` includes 10 real product prompts and 10 edge cases for vagueness, conflict, and incompleteness.

## Cost vs Quality

- The system uses deterministic rule-based conversion instead of expensive model calls to keep latency low.
- Validation and repair are prioritized over raw coverage, ensuring generated configs are directly usable before execution.
- The runtime is intentionally minimal to avoid large dependency and operational cost while still producing a working Flask application.
