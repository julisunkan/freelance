import requests

GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'


def enhance_nda(base_html, data, template, api_key, model='llama-3.3-70b-versatile', tone='formal'):
    if not api_key:
        return None

    tone_desc = {
        'formal': 'highly formal and traditional legal language',
        'strict': 'strict and strongly-worded protective language',
        'startup': 'clear, modern, and startup-friendly language without excessive legalese',
        'legal-heavy': 'comprehensive, dense legal language with maximum protection',
    }.get(tone, 'professional and formal legal language')

    system_msg = (
        'You are a legal document assistant specializing in Non-Disclosure Agreements. '
        'Improve NDA clarity, structure, professionalism, and legal strength. '
        'Do NOT provide legal advice. Return only the improved HTML content of the NDA document, '
        'preserving the exact same HTML structure and class names. Do not add markdown or explanations.'
    )

    user_msg = (
        f'Improve this NDA using {tone_desc}:\n\n'
        f'Template: {template.get("name", "Standard NDA")}\n'
        f'Party A: {data.get("party_a")}\n'
        f'Party B: {data.get("party_b")}\n'
        f'Purpose: {data.get("purpose")}\n'
        f'Jurisdiction: {data.get("jurisdiction")}\n'
        f'Duration: {data.get("duration")}\n\n'
        f'Current NDA HTML:\n{base_html}\n\n'
        f'Return the complete improved HTML only, keeping all class names and structure intact.'
    )

    try:
        resp = requests.post(
            GROQ_API_URL,
            headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            json={
                'model': model,
                'messages': [
                    {'role': 'system', 'content': system_msg},
                    {'role': 'user', 'content': user_msg},
                ],
                'temperature': 0.3,
                'max_tokens': 4096,
            },
            timeout=45,
        )
        resp.raise_for_status()
        content = resp.json()['choices'][0]['message']['content']
        content = content.strip()
        if content.startswith('```'):
            lines = content.split('\n')
            lines = [l for l in lines if not l.strip().startswith('```')]
            content = '\n'.join(lines).strip()
        return content if content else None
    except Exception:
        return None
