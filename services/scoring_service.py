import re


def score_proposal(proposal):
    content = proposal.get('content', '') or ''
    description = proposal.get('description', '') or ''
    raw = content + ' ' + description
    text = re.sub(r'<[^>]+>', ' ', raw).lower()

    score = 0
    feedback = []

    # ── Clarity (0–25) ─────────────────────────────────────────────
    words = len(text.split())
    if words >= 300:
        clarity = 25
    elif words >= 150:
        clarity = 15
        feedback.append("Expand your proposal — aim for at least 300 words to clearly communicate your value.")
    elif words >= 50:
        clarity = 8
        feedback.append("Your proposal is too brief. Add details about your approach, experience, and process.")
    else:
        clarity = 0
        feedback.append("Your proposal needs substantial content. Describe your solution, approach, and value clearly.")

    # ── Structure (0–25) ───────────────────────────────────────────
    headings = len(re.findall(r'<h[1-6]', content))
    lists = len(re.findall(r'<li', content))

    if headings >= 3 and lists >= 3:
        structure = 25
    elif headings >= 2 or lists >= 3:
        structure = 16
        feedback.append("Add more section headings (e.g., 'My Approach', 'Deliverables') to improve readability.")
    elif headings >= 1 or lists >= 1:
        structure = 8
        feedback.append("Use headings and bullet points to organize your proposal into clear, scannable sections.")
    else:
        structure = 0
        feedback.append("Add headings and bullet lists — clients skim proposals, so structure is critical.")

    # ── Pricing presence (0–25) ────────────────────────────────────
    price = proposal.get('price')
    has_price_text = bool(re.search(r'\$|price|cost|invest|fee|rate|budget|payment', text))

    if price and has_price_text:
        pricing = 25
    elif price:
        pricing = 15
        feedback.append("Mention your price in the proposal body with context (e.g., 'Total investment: $X').")
    elif has_price_text:
        pricing = 10
        feedback.append("Set a specific price in the proposal metadata for a complete picture.")
    else:
        pricing = 0
        feedback.append("Always include a clear pricing section — undefined pricing loses clients.")

    # ── Call-to-action (0–25) ──────────────────────────────────────
    cta_patterns = [
        r'contact', r'reach out', r'schedule', r'call', r'meet',
        r'get started', r'next step', r'let\'?s', r'ready to',
        r'questions', r'happy to', r'looking forward', r'excited to', r'reply',
    ]
    cta_hits = sum(1 for p in cta_patterns if re.search(p, text))

    if cta_hits >= 3:
        cta = 25
    elif cta_hits >= 1:
        cta = 12
        feedback.append("Strengthen your call-to-action — make it easy and inviting for the client to respond.")
    else:
        cta = 0
        feedback.append("Add a clear call-to-action at the end (e.g., 'Let's schedule a quick call this week!').")

    score = min(clarity + structure + pricing + cta, 100)

    if score >= 85:
        grade, summary = 'Excellent', 'Outstanding proposal! This is highly competitive.'
    elif score >= 70:
        grade, summary = 'Good', 'Strong proposal with a few areas to polish.'
    elif score >= 50:
        grade, summary = 'Fair', 'Decent start — apply the feedback below to significantly improve it.'
    else:
        grade, summary = 'Needs Work', 'This proposal needs significant improvement before sending to a client.'

    return {
        'score': score,
        'grade': grade,
        'summary': summary,
        'feedback': feedback,
        'breakdown': {
            'clarity': clarity,
            'structure': structure,
            'pricing': pricing,
            'cta': cta,
        }
    }
