# Ticket Prioritisation AI

Revenue-aware support triage for teams that need to spot urgent, high-value,
SLA-sensitive tickets before customers churn.

This repo has been upgraded from a notebook prototype into a deployable product
demo:

- Explainable priority scoring: `Critical`, `High`, `Medium`, `Low`
- Business signals: customer tier, affected users, revenue at risk, SLA window
- Smart routing: security, platform, revenue ops, access, data, or support
- Optional OpenAI enrichment for customer replies and internal notes
- FastAPI endpoint for pilots and integrations
- Streamlit dashboard for live customer demos
- Static GitHub Pages demo in `docs/`
- CI, Docker, tests, and deployment workflow

## Live Demo Options

### Static customer demo

Open `docs/index.html` directly, or deploy with GitHub Pages. Once Pages is
enabled for this repo, the expected URL is:

```text
https://saifmangan.github.io/ticket-prioritisation-system/
```

The static demo runs fully in the browser and is ideal for first sales calls.

### Streamlit demo

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### FastAPI service

```bash
pip install -r requirements.txt
uvicorn api:app --reload
```

Then post a ticket:

```bash
curl -X POST http://127.0.0.1:8000/prioritise \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Production checkout is down",
    "message": "URGENT: customers cannot pay and our checkout is down.",
    "customer": "Northstar Retail",
    "customer_tier": "enterprise",
    "affected_users": 480,
    "revenue_at_risk": 25000,
    "hours_until_sla": 0.5
  }'
```

## Optional AI Briefs

The product works without an API key. To enable LLM-generated summaries,
customer replies, and internal notes:

```bash
cp .env.example .env
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4o-mini"
```

The deterministic local prioritiser still produces a fallback brief when no key
is configured, so demos never fail in front of customers.

## Product Positioning

Sell this as a lightweight triage intelligence layer for B2B support teams:

- Starter: GBP 99/month for shared dashboard triage
- Growth: GBP 399/month for API access, AI briefs, and weekly risk reporting
- Enterprise: custom pricing for SSO, audit exports, private deployment, and SLA rules

Best first customers: SaaS support teams, managed service providers, e-commerce
platforms, fintech support desks, and agencies handling multiple client queues.

## Project Structure

```text
ticket-prioritisation-system/
├── ticket_prioritisation/
│   ├── prioritizer.py      # Deterministic explainable scoring engine
│   ├── ai.py               # Optional OpenAI brief generation
│   └── sample_data.py      # Demo scenarios
├── api.py                  # FastAPI service
├── app.py                  # Streamlit demo
├── docs/index.html         # Static sales/demo page for GitHub Pages
├── tests/                  # Prioritisation regression tests
├── Dockerfile
└── .github/workflows/      # CI and Pages deployment
```

## Development

```bash
pip install -r requirements-dev.txt
pytest
ruff check .
python main.py --ai
```

## Deployment

### GitHub Pages

The `Deploy customer demo` workflow deploys the `docs/` directory when changes
land on `main`. In repository settings, set Pages source to GitHub Actions if it
is not already enabled.

### Docker

```bash
docker build -t ticket-prioritisation-ai .
docker run -p 8000:8000 --env-file .env ticket-prioritisation-ai
```

### Render/Fly/Railway

Use the Dockerfile or run:

```bash
uvicorn api:app --host 0.0.0.0 --port $PORT
```

## Original ML Assets

The older notebook and feature-engineering files are kept for model exploration.
They can be used later to train a supervised classifier from labelled support
data, while the current product path prioritises a reliable demo and explainable
business rules.
