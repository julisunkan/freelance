def compute_risk(structured_data: dict, image_analysis: dict, is_duplicate: bool, face_match_ok: bool = True) -> str:
    score = 0

    missing = sum(1 for v in structured_data.values() if not v)
    score += missing * 20

    quality = image_analysis.get('quality_score', 100)
    if quality < 40:
        score += 40
    elif quality < 70:
        score += 20

    if is_duplicate:
        score += 50

    if not face_match_ok:
        score += 30

    if score >= 70:
        return 'HIGH'
    elif score >= 30:
        return 'MEDIUM'
    return 'LOW'
