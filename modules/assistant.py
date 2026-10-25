"""Epic 5 - Assistant and Advisory Engine.

1. advisory_rules(): a transparent, rule-based engine that turns the app's results
   (safety audit, crack diagnosis, weather, budget) into a prioritised action list.
2. chat_answer(): a Gemini chat assistant that answers questions using those results as context.
"""
from .gemini_client import ask_text

PRIORITY_ORDER = {"STOP": 0, "HIGH": 1, "MEDIUM": 2, "INFO": 3}


def advisory_rules(safety: dict | None = None, crack: dict | None = None,
                   forecast: list[dict] | None = None, budget: dict | None = None) -> list[dict]:
    """Return a sorted list of {priority, source, message} advisories."""
    out = []

    def add(priority, source, message):
        out.append({"priority": priority, "source": source, "message": message})

    if safety and "_raw" not in safety:
        risk = safety.get("overall_risk")
        if risk == "Critical":
            add("STOP", "Safety audit", "Critical risk seen on site. Stop affected work until hazards are fixed.")
        elif risk == "High":
            add("HIGH", "Safety audit", "High risk on site. Fix the high-severity hazards before continuing.")
        for h in safety.get("hazards", []):
            if h.get("severity") in ("High", "Critical"):
                add("HIGH", "Safety audit", f"{h.get('issue', 'Hazard')}: {h.get('recommendation', '')}")

    if crack and "_raw" not in crack:
        if crack.get("structural_concern"):
            add("STOP", "Crack diagnosis", "Possible structural crack. Keep load off the area and call a structural engineer.")
        elif crack.get("severity") in ("High", "Critical"):
            add("HIGH", "Crack diagnosis", f"Serious crack ({crack.get('urgency', 'repair soon')}). Get it inspected.")
        elif crack.get("severity") == "Medium":
            add("MEDIUM", "Crack diagnosis", "Medium crack. Mark its ends with a date and re-check weekly.")

    for day in forecast or []:
        d = day["date"]
        if day["rain_mm"] >= 10:
            add("HIGH", "Weather", f"{d}: heavy rain ({day['rain_mm']} mm). Avoid concrete pouring; cover cement and steel.")
        elif day["rain_mm"] >= 2:
            add("MEDIUM", "Weather", f"{d}: light rain expected. Protect fresh concrete and plaster.")
        if day["wind_kmh"] >= 40:
            add("HIGH", "Weather", f"{d}: strong wind ({day['wind_kmh']} km/h). Pause crane and work at height.")
        if day["temp_max_c"] >= 38:
            add("MEDIUM", "Weather", f"{d}: very hot ({day['temp_max_c']} C). Schedule heavy work early; provide water and shade; cure concrete longer.")

    if budget:
        pct = budget.get("contingency_pct")
        if pct is not None and pct < 8:
            add("MEDIUM", "Budget", f"Contingency is only {pct}%. Consider 8-15% for unexpected costs.")
        add("INFO", "Budget", "Compare these estimates with at least three local supplier quotes before ordering.")

    if not out:
        add("INFO", "General", "No advisories yet. Run the safety audit, crack diagnosis, budget or weather tabs first.")
    return sorted(out, key=lambda a: PRIORITY_ORDER[a["priority"]])


def build_context(safety=None, crack=None, forecast=None, budget_summary=None) -> str:
    parts = []
    if safety:
        parts.append(f"Latest safety audit: {safety}")
    if crack:
        parts.append(f"Latest crack diagnosis: {crack}")
    if forecast:
        parts.append(f"Weather forecast: {forecast}")
    if budget_summary:
        parts.append(f"Budget summary: {budget_summary}")
    return "\n".join(parts) if parts else "No analysis has been run yet."


def chat_answer(client, question: str, history: list[dict], context: str) -> str:
    """history = [{"role": "user"|"assistant", "content": str}, ...]"""
    convo = "\n".join(f"{m['role'].title()}: {m['content']}" for m in history[-8:])
    prompt = f"""You are a helpful construction site assistant for engineers, contractors and students.
Use the project context below when it is relevant. Be concise and practical.
For anything about structural safety, say when a qualified engineer must confirm.
If you do not know, say so instead of guessing.

PROJECT CONTEXT:
{context}

CONVERSATION SO FAR:
{convo}

User: {question}
Assistant:"""
    return ask_text(client, prompt)
