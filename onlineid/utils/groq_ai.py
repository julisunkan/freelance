import json
import re

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

MODEL = 'llama3-70b-8192'


def _call_groq(api_key: str, prompt: str) -> str:
    if not GROQ_AVAILABLE or not api_key:
        return ''
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.2,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()


def _extract_json(text: str) -> dict:
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {}


def ai_extract_and_fix(ocr_text: str, api_key: str) -> dict:
    if not api_key:
        return {}

    prompt = f"""You are an ID document parser. Given the raw OCR text below extracted from an identity document, return ONLY a valid JSON object with these fields:
{{
  "name": "Full name on the document",
  "dob": "Date of birth in original format",
  "id_number": "ID or document number",
  "expiry_date": "Expiry date if present",
  "notes": "Any observations or corrections made"
}}

Raw OCR Text:
{ocr_text}

Return ONLY the JSON object, nothing else."""

    raw = _call_groq(api_key, prompt)
    return _extract_json(raw)


def ai_risk_analysis(ocr_text: str, structured_data: dict, api_key: str) -> dict:
    if not api_key:
        return {}

    prompt = f"""You are an ID document fraud analyst. Analyze the following OCR text and extracted data from an identity document and return ONLY a valid JSON object:
{{
  "risk_level": "LOW or MEDIUM or HIGH",
  "reasons": ["reason 1", "reason 2"],
  "inconsistencies": ["inconsistency 1"]
}}

OCR Text:
{ocr_text}

Extracted Fields:
{json.dumps(structured_data, indent=2)}

Look for: missing fields, inconsistent dates, suspicious patterns, formatting anomalies.
Return ONLY the JSON object, nothing else."""

    raw = _call_groq(api_key, prompt)
    return _extract_json(raw)
