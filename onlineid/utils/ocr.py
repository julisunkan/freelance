import re
import subprocess

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


def extract_text(image_path: str) -> str:
    if not TESSERACT_AVAILABLE:
        return ''
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, config='--psm 6')
        return clean_text(text)
    except Exception:
        return ''


def clean_text(text: str) -> str:
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return '\n'.join(lines)


def extract_structured_fields(text: str) -> dict:
    data = {
        'full_name': '',
        'date_of_birth': '',
        'id_number': '',
        'expiry_date': '',
    }

    name_match = re.search(
        r'(?:Name|NAME)[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})', text)
    if name_match:
        data['full_name'] = name_match.group(1).strip()

    dob_match = re.search(
        r'(?:DOB|Date of Birth|Birth Date|BIRTH)[:\s]*([\d]{1,2}[\/\-\.][\d]{1,2}[\/\-\.][\d]{2,4})', text, re.IGNORECASE)
    if dob_match:
        data['date_of_birth'] = dob_match.group(1).strip()

    id_match = re.search(
        r'(?:ID|No\.|Number|DL|Passport)[:\s#]*([A-Z0-9]{6,15})', text, re.IGNORECASE)
    if id_match:
        data['id_number'] = id_match.group(1).strip()

    exp_match = re.search(
        r'(?:Exp|Expiry|Expires|EXP)[:\s]*([\d]{1,2}[\/\-\.][\d]{1,2}[\/\-\.][\d]{2,4})', text, re.IGNORECASE)
    if exp_match:
        data['expiry_date'] = exp_match.group(1).strip()

    return data
