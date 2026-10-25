"""Multimodal Construction Intelligence Platform - Streamlit app.

Run with:  streamlit run app.py
"""
import os
from datetime import date

import streamlit as st
from dotenv import load_dotenv

from modules import ai_layer, assistant, image_analysis, planning_valuation as pv, weather_guidance as wg
from modules.gemini_client import get_client

load_dotenv()
st.set_page_config(page_title="Construction Intelligence Platform", page_icon="🏗️", layout="wide")

SEVERITY_ICON = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}


# ---------- helpers ----------
def get_gemini():
    """Return a Gemini client or show a friendly message and return None."""
    try:
        return get_client(st.session_state.get("api_key") or os.getenv("GEMINI_API_KEY"))
    except ValueError as e:
        st.warning(str(e))
        return None


def show_json_fallback(result: dict) -> bool:
    """If the model did not return valid JSON, show raw text. Returns True if fallback was used."""
    if "_raw" in result:
        st.warning("The AI reply was not in the expected format. Showing the raw reply:")
        st.write(result["_raw"])
        return True
    return False


def upload_image(label: str, key: str):
    file = st.file_uploader(label, type=["jpg", "jpeg", "png", "webp"], key=key)
    if file is None:
        return None
    img = image_analysis.prepare_image(file)
    st.image(img, caption="Uploaded image", use_container_width=True)
    return img


# ---------- sidebar ----------
with st.sidebar:
    st.title("🏗️ Settings")
    st.text_input("Gemini API key", type="password", key="api_key",
                  help="Free key from aistudio.google.com. Or put it in a .env file.")
    st.caption("Your key stays in this session and is never saved to disk by the app.")
    st.divider()
    st.caption("AI results are decision-support only. Always get a qualified engineer to confirm "
               "safety, structural and cost decisions.")

st.title("Multimodal Construction Intelligence Platform")
st.write("Audit site safety from photos, diagnose cracks, estimate budgets and timelines, "
         "and get weather-aware guidance for your site team.")

tab_safety, tab_crack, tab_budget, tab_weather, tab_assistant = st.tabs(
    ["🦺 Site Safety Audit", "🧱 Crack Diagnosis", "💰 Budget & Valuation", "⛅ Weather Guidance",
     "💬 Assistant & Advisories"]
)

# ---------- Tab 1: safety ----------
with tab_safety:
    st.subheader("Site safety audit from a photo")
    img = upload_image("Upload a construction site photo", "safety_img")
    if img is not None and st.button("Run safety audit", type="primary"):
        client = get_gemini()
        if client:
            with st.spinner("Inspecting the photo..."):
                try:
                    result = image_analysis.audit_site_safety(client, img)
                except Exception as e:
                    st.error(f"Gemini request failed: {e}")
                    result = None
            if result and not show_json_fallback(result):
                st.session_state["last_safety"] = result
                risk = result.get("overall_risk", "Unknown")
                st.metric("Overall risk", f"{SEVERITY_ICON.get(risk, '⚪')} {risk}")
                st.write(result.get("summary", ""))
                st.markdown("#### Hazards found")
                hazards = result.get("hazards", [])
                if not hazards:
                    st.success("No hazards reported.")
                for h in hazards:
                    sev = h.get("severity", "Unknown")
                    with st.expander(f"{SEVERITY_ICON.get(sev, '⚪')} {h.get('issue', 'Hazard')} ({sev})"):
                        st.write(f"**Where:** {h.get('location', '-')}")
                        st.write(f"**Recommendation:** {h.get('recommendation', '-')}")
                st.markdown("#### PPE observations")
                st.write(result.get("ppe_observations", "-"))
                good = result.get("positive_observations", [])
                if good:
                    st.markdown("#### Good practices seen")
                    for g in good:
                        st.write(f"- {g}")

# ---------- Tab 2: cracks ----------
with tab_crack:
    st.subheader("Concrete / masonry crack diagnosis")
    img = upload_image("Upload a close-up photo of the crack", "crack_img")
    if img is not None and st.button("Diagnose crack", type="primary"):
        client = get_gemini()
        if client:
            with st.spinner("Analysing the crack..."):
                try:
                    result = image_analysis.diagnose_crack(client, img)
                except Exception as e:
                    st.error(f"Gemini request failed: {e}")
                    result = None
            if result and not show_json_fallback(result):
                st.session_state["last_crack"] = result
                sev = result.get("severity", "Unknown")
                c1, c2, c3 = st.columns(3)
                c1.metric("Severity", f"{SEVERITY_ICON.get(sev, '⚪')} {sev}")
                c2.metric("Crack type", str(result.get("crack_type", "-")).title())
                c3.metric("Urgency", result.get("urgency", "-"))
                if result.get("structural_concern"):
                    st.error("Possible structural concern - consult a structural engineer.")
                st.markdown("#### Likely causes")
                for c in result.get("likely_causes", []):
                    st.write(f"- {c}")
                st.markdown("#### Recommended repair")
                for i, step in enumerate(result.get("recommended_repair", []), 1):
                    st.write(f"{i}. {step}")
                st.markdown("#### Monitoring")
                st.write(result.get("monitoring_advice", "-"))
                st.info(result.get("confidence_note", "A photo cannot replace an on-site inspection."))

# ---------- Tab 3: budget ----------
with tab_budget:
    st.subheader("Budget, timeline and asset value")
    col1, col2, col3, col4 = st.columns(4)
    area = col1.number_input("Built-up area per floor (sqft)", 100.0, 100000.0, 1000.0, 50.0)
    floors = col2.number_input("Floors", 1, 20, 2)
    quality = col3.selectbox("Quality grade", list(pv.QUALITY_MULTIPLIER), index=1)
    contingency = col4.slider("Contingency %", 0, 25, 10)
    start = st.date_input("Planned start date", date.today())

    if st.button("Estimate", type="primary"):
        try:
            rates = pv.load_rates()
            items, summary = pv.estimate_budget(rates, area, int(floors), quality, float(contingency))
            timeline = pv.build_timeline(start, area, int(floors))
            st.session_state["budget"] = {
                "items": items, "summary": summary, "timeline": timeline,
                "area": area, "floors": int(floors), "quality": quality,
                "contingency_pct": contingency,
            }
        except Exception as e:
            st.error(f"Could not calculate: {e}")

    data = st.session_state.get("budget")
    if data:
        s = data["summary"]
        m1, m2, m3 = st.columns(3)
        m1.metric("Estimated total", pv.inr(s["grand_total"]))
        m2.metric("Cost per sqft", pv.inr(s["cost_per_sqft"]))
        m3.metric("Duration", f"{pv.estimate_duration_days(data['area'], data['floors'])} days")

        st.markdown("#### Cost by category")
        st.bar_chart(s["by_category"])

        st.markdown("#### Line items")
        st.dataframe(
            data["items"][["item", "category", "unit", "quantity", "adj_rate_inr", "cost_inr"]],
            use_container_width=True, hide_index=True,
        )
        st.download_button("Download line items (CSV)", data["items"].to_csv(index=False),
                           "budget_estimate.csv", "text/csv")

        st.markdown("#### Timeline")
        st.pyplot(pv.plot_gantt(data["timeline"]))

        st.markdown("#### Asset value (after completion)")
        a1, a2 = st.columns(2)
        age = a1.number_input("Building age (years)", 0.0, 100.0, 5.0, 1.0)
        life = a2.number_input("Useful life (years)", 10.0, 150.0, 60.0, 5.0)
        av = pv.asset_value(s["grand_total"], age, life)
        v1, v2 = st.columns(2)
        v1.metric("Current building value", pv.inr(av["current_value"]))
        v2.metric("Yearly depreciation", pv.inr(av["yearly_depreciation"]))
        st.caption("Straight-line depreciation, land value not included.")

        st.markdown("#### 🤖 AI insights")
        if st.button("Get cost-saving suggestions and risks"):
            client = get_gemini()
            if client:
                with st.spinner("Thinking..."):
                    try:
                        csv_text = data["items"][["item", "quantity", "adj_rate_inr", "cost_inr"]].to_csv(index=False)
                        st.markdown(ai_layer.budget_insights(
                            client, s, csv_text, data["quality"], data["area"], data["floors"]))
                    except Exception as e:
                        st.error(f"Gemini request failed: {e}")

# ---------- Tab 4: weather ----------
with tab_weather:
    st.subheader("Weather-aware daily guidance")
    city = st.text_input("Site city", "Indore")
    activities = st.text_area("Planned work for the next days", "Slab concrete pouring and brick masonry")
    if st.button("Get guidance", type="primary"):
        client = get_gemini()
        if client:
            try:
                place = wg.geocode(city)
                if place is None:
                    st.error("City not found. Try another spelling.")
                else:
                    forecast = wg.get_forecast(place["lat"], place["lon"], days=3)
                    st.session_state["last_forecast"] = forecast
                    st.markdown(f"**Forecast for {place['name']}**")
                    st.dataframe(forecast, use_container_width=True, hide_index=True)
                    with st.spinner("Preparing guidance..."):
                        st.markdown(wg.daily_guidance(client, place["name"], forecast, activities))
            except Exception as e:
                st.error(f"Something went wrong: {e}")

# ---------- Tab 5: assistant + advisory engine ----------
with tab_assistant:
    st.subheader("Advisory engine")
    st.caption("Rule-based advisories built from whatever you have run in the other tabs.")
    budget_state = st.session_state.get("budget")
    advisories = assistant.advisory_rules(
        safety=st.session_state.get("last_safety"),
        crack=st.session_state.get("last_crack"),
        forecast=st.session_state.get("last_forecast"),
        budget={"contingency_pct": budget_state["contingency_pct"]} if budget_state else None,
    )
    icons = {"STOP": "🛑", "HIGH": "🔴", "MEDIUM": "🟡", "INFO": "ℹ️"}
    for a in advisories:
        st.write(f"{icons[a['priority']]} **{a['priority']}** ({a['source']}): {a['message']}")

    st.divider()
    st.subheader("Ask the construction assistant")
    st.session_state.setdefault("chat", [])
    for m in st.session_state["chat"]:
        with st.chat_message(m["role"]):
            st.write(m["content"])

    question = st.chat_input("Ask about safety, cracks, materials, costs, scheduling...")
    if question:
        client = get_gemini()
        if client:
            with st.chat_message("user"):
                st.write(question)
            context = assistant.build_context(
                st.session_state.get("last_safety"), st.session_state.get("last_crack"),
                st.session_state.get("last_forecast"),
                budget_state["summary"] if budget_state else None,
            )
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        reply = assistant.chat_answer(client, question, st.session_state["chat"], context)
                    except Exception as e:
                        reply = f"Sorry, the request failed: {e}"
                st.write(reply)
            st.session_state["chat"] += [{"role": "user", "content": question},
                                         {"role": "assistant", "content": reply}]
    if st.session_state["chat"] and st.button("Clear chat"):
        st.session_state["chat"] = []
        st.rerun()
