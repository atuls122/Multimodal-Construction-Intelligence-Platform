"""Epic 4 - AI intelligence layer: explains budgets and suggests savings / risks."""
from .gemini_client import ask_text


def budget_insights(client, summary: dict, line_items_csv: str, quality: str, area: float, floors: int) -> str:
    prompt = f"""You are a construction cost consultant. A user estimated a building budget.

Inputs: {area} sqft per floor, {floors} floor(s), quality grade: {quality}.
Summary: {summary}

Line items (CSV):
{line_items_csv}

Give:
1. A plain-language explanation of where the money goes (3-4 sentences).
2. Five specific cost-saving suggestions that do NOT compromise structural safety.
3. Three budget risks to watch (price swings, delays, scope creep) with a mitigation each.
Note that figures are rough estimates and local quotes should be used before real decisions."""
    return ask_text(client, prompt)
