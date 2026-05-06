try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


def analyze_image(image_path: str) -> dict:
    result = {
        'blur_score': 0.0,
        'resolution_ok': True,
        'noise_level': 0.0,
        'quality_score': 100,
        'issues': [],
    }

    if not CV2_AVAILABLE:
        return result

    try:
        img = cv2.imread(image_path)
        if img is None:
            result['issues'].append('Could not read image')
            result['quality_score'] = 0
            return result

        h, w = img.shape[:2]
        if w < 400 or h < 250:
            result['resolution_ok'] = False
            result['issues'].append(f'Low resolution ({w}x{h})')

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        result['blur_score'] = round(float(blur_score), 2)
        if blur_score < 50:
            result['issues'].append(f'Image is blurry (score: {blur_score:.1f})')

        noise_level = float(np.std(gray))
        result['noise_level'] = round(noise_level, 2)
        if noise_level > 80:
            result['issues'].append(f'High noise level ({noise_level:.1f})')

        penalty = len(result['issues']) * 25
        if not result['resolution_ok']:
            penalty += 10
        result['quality_score'] = max(0, 100 - penalty)

    except Exception as e:
        result['issues'].append(f'Analysis error: {str(e)}')

    return result
