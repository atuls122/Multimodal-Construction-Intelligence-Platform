# Multimodal Construction Intelligence Platform

A Streamlit app that uses Google Gemini to audit site safety from photos, diagnose concrete cracks,
estimate project budgets, timelines and asset value, and give weather-aware daily guidance.

## Features
- 🦺 **Site Safety Audit** - upload a photo, get risk level, hazards and recommendations
- 🧱 **Crack Diagnosis** - crack type, severity, causes, repair steps, urgency
- 💰 **Budget & Valuation** - line-item cost, category chart, Gantt timeline, depreciation, CSV export
- ⛅ **Weather Guidance** - 3-day forecast (Open-Meteo) turned into go / caution / avoid advice
- 🤖 **AI insights** - cost-saving ideas and budget risks
- 💬 **Assistant & Advisories** - rule-based STOP/HIGH/MEDIUM/INFO actions plus a chat assistant that knows your results

## Project structure
```
app.py                    Streamlit UI (5 tabs)
modules/
  gemini_client.py        Gemini API wrapper
  image_analysis.py       Epic 2: safety + crack analysis
  planning_valuation.py   Epic 3: budget, timeline, asset value
  ai_layer.py             Epic 4: AI budget insights
  assistant.py            Epic 5: advisory engine + chat assistant
  weather_guidance.py     Epic 4: weather + guidance
data/material_rates.csv   Editable quantity norms and rates
docs/                     SRS, workflow, testing, deployment, conclusion
tests/                    Unit tests for the calculation module
```

## Setup (Windows)
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Get a free API key at https://aistudio.google.com, then either paste it in the app sidebar,
or copy `.env.example` to `.env` and put the key there.

## Run
```
streamlit run app.py
```

## Test
```
python tests/test_planning.py
python tests/test_assistant.py
```

## Deploy (free)
Push to GitHub, then on https://share.streamlit.io create an app from the repo, and add
`GEMINI_API_KEY` under *Secrets*.

## Notes and limits
- Costs and quantities are rough rule-of-thumb estimates, not quotations.
- AI output is decision support, not a substitute for a qualified engineer.

## Tech stack
Python, Streamlit, Google Gemini (google-genai), Pandas, Matplotlib, Pillow, Open-Meteo.
