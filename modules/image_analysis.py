"""Epic 2 - Image-based analysis: site safety audit and concrete crack diagnosis."""
from PIL import Image, ImageOps

from .gemini_client import ask_json

SAFETY_PROMPT = """You are a construction site safety inspector. Examine this site photo.
Return ONLY JSON with this exact shape:
{
  "overall_risk": "Low" | "Medium" | "High" | "Critical",
  "summary": "2-3 sentence summary",
  "hazards": [
    {"issue": "...", "severity": "Low|Medium|High|Critical", "location": "where in the image", "recommendation": "..."}
  ],
  "ppe_observations": "helmets, vests, boots, harnesses seen or missing",
  "positive_observations": ["good practices visible"]
}
Only report what is actually visible. If the image is not a construction site, say so in the summary."""

CRACK_PROMPT = """You are a structural engineer's assistant. Examine this photo of a crack in concrete or masonry.
Return ONLY JSON with this exact shape:
{
  "crack_type": "hairline | shrinkage | settlement | structural | thermal | other",
  "severity": "Low" | "Medium" | "High" | "Critical",
  "urgency": "Monitor | Repair soon | Repair immediately | Consult engineer now",
  "likely_causes": ["..."],
  "structural_concern": true or false,
  "recommended_repair": ["step-by-step repair suggestions"],
  "monitoring_advice": "how to monitor if it is growing",
  "confidence_note": "what you cannot judge from a photo alone"
}
Be honest about uncertainty. A photo cannot replace an on-site inspection."""


def prepare_image(file, max_side: int = 1600) -> Image.Image:
    """Open an uploaded file, fix phone-camera rotation, and shrink it for faster API calls."""
    img = Image.open(file)
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.thumbnail((max_side, max_side))
    return img


def audit_site_safety(client, image: Image.Image) -> dict:
    return ask_json(client, SAFETY_PROMPT, image=image)


def diagnose_crack(client, image: Image.Image) -> dict:
    return ask_json(client, CRACK_PROMPT, image=image)
