import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-70b-8192"


def _call_groq(messages, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2048,
    }
    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data['choices'][0]['message']['content'], None
    except requests.exceptions.HTTPError:
        if resp.status_code == 401:
            return None, "Invalid API key. Please check your Groq API key in the Admin Panel."
        return None, f"API error {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return None, str(e)


def generate_proposal_content(data, api_key):
    client = data.get('client_name', 'the client')
    title = data.get('project_title', 'the project')
    description = data.get('description', '')
    price = data.get('price', '')
    timeline = data.get('timeline', '')

    prompt = f"""You are an expert freelance proposal writer. Write a compelling, professional, and persuasive proposal in HTML format.

Project details:
- Client: {client}
- Project: {title}
- Description: {description}
- Budget: ${price}
- Timeline: {timeline}

Write a complete proposal with these sections:
1. A warm, personalized introduction addressing the client by name
2. Clear understanding of the client's problem/need
3. Your proposed approach and solution (use <ul><li> bullet points)
4. Why you are the best fit (relevant experience)
5. Deliverables (numbered list with <ol><li>)
6. Investment section clearly stating ${price}
7. A strong, confident call-to-action closing

Use proper HTML: <h1>, <h2>, <p>, <ul>, <li>, <ol>, <strong>, <em>.
Be professional, persuasive, and confident. Around 400-600 words.
Return ONLY the HTML content, no markdown, no explanations."""

    messages = [
        {"role": "system", "content": "You are a professional freelance proposal writer who creates compelling, winning proposals that convert clients."},
        {"role": "user", "content": prompt}
    ]

    content, error = _call_groq(messages, api_key)
    if error:
        return {'error': error}
    return {'content': content}


def improve_proposal_content(content, api_key):
    prompt = f"""You are an expert copywriter specializing in freelance proposals. Improve the following proposal to make it:
- More persuasive and emotionally compelling
- More professional and polished in language
- Stronger, more confident call-to-action
- Better structured with clear sections
- More client-focused (focus on their benefits, not your features)

Return ONLY the improved HTML content. Keep all HTML structure but improve the text. No explanations.

Original proposal:
{content}"""

    messages = [
        {"role": "system", "content": "You are a professional copywriter who transforms average freelance proposals into winning, client-converting masterpieces."},
        {"role": "user", "content": prompt}
    ]

    improved, error = _call_groq(messages, api_key)
    if error:
        return {'error': error}
    return {'content': improved}
