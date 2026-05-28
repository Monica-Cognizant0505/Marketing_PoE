"""
ai_analyzer.py  —  Azure OpenAI GPT-4o analysis of the Content Syndication PDF.
Focuses on extracting the URL and syndication summary from the text.
"""

import json
import re
import base64
from pathlib import Path
from openai import AzureOpenAI


def _encode_image(path: str) -> tuple[str, str]:
    ext = Path(path).suffix.lower().lstrip(".")
    media_map = {"jpg":"image/jpeg","jpeg":"image/jpeg",
                 "png":"image/png","webp":"image/webp","gif":"image/gif"}
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode(), media_map.get(ext, "image/png")


def analyze_with_azure(
    extraction: dict,
    keywords: list,
    azure_endpoint: str,
    azure_api_key: str,
    azure_deployment: str,
    azure_api_version: str,
) -> dict:

    client = AzureOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=azure_api_key,
        api_version=azure_api_version,
    )

    full_text = extraction.get("full_text", "")

    content = [
        {
            "type": "text",
            "text": (
                "You are analysing a Content Syndication Proof of Execution PDF.\n\n"
                "Page 1: URL + screenshot of landing page.\n"
                "Page 2: Results table — company names + job titles of leads.\n\n"
                f"Extracted text:\n{full_text[:8000]}\n\n"
                "Return ONLY valid JSON (no markdown fences):\n"
                "{\n"
                '  "urls": ["full URL from page 1"],\n'
                '  "syndication_title": "Content Syndication: Results",\n'
                '  "syndication_results": ["bullet summary 1", "bullet summary 2"],\n'
                '  "syndication_metrics": {"Total Leads": "N"},\n'
                '  "linkedin_title": "LinkedIn Adverts",\n'
                '  "linkedin_results": [],\n'
                '  "linkedin_metrics": {}\n'
                "}"
            )
        }
    ]

    # Attach first image for context (page 1 screenshot)
    for img_path in extraction.get("images", [])[:2]:
        try:
            b64, mt = _encode_image(img_path)
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mt};base64,{b64}", "detail": "low"}
            })
        except Exception:
            continue

    try:
        response = client.chat.completions.create(
            model=azure_deployment,
            messages=[{"role": "user", "content": content}],
            max_tokens=800,
            temperature=0.1,
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"\s*```$",     "", raw)
        analysis = json.loads(raw)
    except Exception:
        analysis = {
            "urls": [],
            "syndication_title": "Content Syndication: Results",
            "syndication_results": [],
            "syndication_metrics": {},
            "linkedin_title": "LinkedIn Adverts",
            "linkedin_results": [],
            "linkedin_metrics": {},
        }

    # Always prefer URL grabbed directly from PDF text
    if extraction.get("slide3_url"):
        analysis["urls"] = [extraction["slide3_url"]]

    analysis["slide3_image_path"] = extraction.get("slide3_screenshot")
    analysis["slide5_image_path"] = (extraction.get("advert_images") or [None])[0]
    analysis["_image_paths"]      = extraction.get("images", [])

    return analysis
