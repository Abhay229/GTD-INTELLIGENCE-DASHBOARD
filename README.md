# 🛡 AI-Based Military Intelligence Dashboard + Agentic AI Analyst

A Streamlit application for exploring, visualizing, and forecasting incidents
in the **Global Terrorism Database (GTD)** — combined with an **LLM agent**
that can autonomously call the app's own ML models and data-query functions
to answer open-ended analytical questions.

Runs entirely on your laptop. LLM inference uses **free models via
[OpenRouter](https://openrouter.ai)** — no paid API key required.

---

## Why this project

Most dashboards like this stop at charts and a couple of `scikit-learn`
models. This one adds a genuine **agentic AI layer** on top:

- The dashboard pages (map, country analysis, forecasting, classifiers,
  explorer) are the **tools**.
- An LLM **decides which tools to call, in what order, with what
  arguments** — based on a natural-language question — instead of a human
  clicking through tabs.
- Every tool call and its result is logged to a visible **reasoning trace**
  in the UI, for basic observability into the agent's decisions.

## Features

| Page | What it does |
|---|---|
| 🏠 Home | Overview KPIs + attacks-over-time chart |
| 🌍 Global Threat Map | Geo-plot of incidents, filterable by year |
| 🌎 Country Analysis | Deep dive on one country (trends, groups, weapons, map, table) |
| 🤖 Attack Prediction | Random Forest classifier predicting attack type from incident features |
| 🚨 Threat Level | Random Forest classifier predicting LOW/MEDIUM/HIGH threat level |
| 📈 Forecasting | Linear Regression forecast of future attack counts per country |
| 🧠 AI Intelligence Report | Auto-generated executive summary — LLM-written when configured, templated fallback otherwise |
| 📊 Data Explorer | Multi-filter EDA tool with charts, missing-value report, CSV export |
| ⚙ Settings | Dashboard configuration (UI only) + shows current agent/model config |
| 🕵 **AI Analyst Agent** | **Chat with an agent that calls the tools above on your behalf, with a visible reasoning trace** |

## Architecture

```
User question (chat)
      │
      ▼
agent/agent_core.py  ── tool-calling loop (hand-rolled, not a framework)
      │
      ├──> tools/agent_tools.py
      │       ├─ query_country_stats()   → country summary stats
      │       ├─ forecast_attacks()      → LinearRegression forecast
      │       ├─ predict_threat_level()  → RandomForest classifier
      │       └─ query_data()            → filtered aggregate lookups
      │
      ▼
agent/llm_client.py  ── OpenRouter API (OpenAI-compatible), free-tier model
      │
      ▼
Final answer + reasoning trace rendered in Streamlit
```

Every "tool" the agent can call is just a plain, testable Python function —
the same logic used elsewhere in the dashboard, refactored so it isn't
locked inside a Streamlit page.

## Setup

### 1. Clone and install

```bash
git clone https://github.com/<your-username>/gtd-intelligence-dashboard.git
cd gtd-intelligence-dashboard
pip install -r requirements.txt
```

### 2. Get the dataset

The raw GTD CSV isn't included in this repo (licensed research dataset —
see `data/README.md` for how to obtain it). Place it at:

```
data/globalterrorism.csv
```

### 3. Train the attack-type model (one-time)

```bash
python train_attack_model.py
```

This writes `models/attack_prediction_model.pkl` and its encoders, used by
the Attack Prediction page. (The Threat Level model and the agent's
`predict_threat_level` tool train themselves automatically and are cached
in-process — no separate script needed.)

### 4. Add a free OpenRouter API key (for the GenAI pages)

```bash
cp .env.example .env
```

- Sign up at https://openrouter.ai (no credit card required)
- Create an API key
- Paste it into `.env` as `OPENROUTER_API_KEY=...`

Without a key, everything still runs — the AI Intelligence Report falls
back to a templated summary, and the AI Analyst Agent page shows a
configuration warning instead of chatting.

> **Free-tier note:** OpenRouter's free models are rate-limited (roughly
> 20 requests/min, 200/day at the time of writing) and the specific list
> of free models rotates. Check https://openrouter.ai/models filtered to
> `Price: Free` and update `OPENROUTER_MODEL` in `.env` if the default
> stops working. This is a deliberate constraint of the project, not a bug
> — it's called out here because production systems need the same
> awareness of rate limits and model availability.

### 5. Run the app

```bash
streamlit run app.py
```

## Tech stack

- **UI:** Streamlit (multi-page app)
- **Data / viz:** pandas, Plotly
- **ML:** scikit-learn (RandomForestClassifier, LinearRegression)
- **LLM inference:** OpenRouter (OpenAI-compatible API), free-tier models
  (e.g. `qwen/qwen3-coder:free`)
- **Agent loop:** hand-rolled tool-calling loop (no LangChain/LangGraph —
  written from scratch so the mechanics are transparent)

## Known limitations / next steps

- Free OpenRouter models have rate limits — not intended for production
  traffic.
- No persistent storage for the agent's conversation (resets per session).
- `9_⚙_Settings.py` is a UI mockup; most toggles aren't wired to actual
  behavior yet.
- Possible extensions: RAG over per-country summaries with a local vector
  store (Chroma + `sentence-transformers`), a second "critic" agent that
  reviews the analyst agent's output, deployment to Streamlit Community
  Cloud.

## Dataset credit

Global Terrorism Database (GTD), National Consortium for the Study of
Terrorism and Responses to Terrorism (START), University of Maryland.
https://www.start.umd.edu/gtd/
