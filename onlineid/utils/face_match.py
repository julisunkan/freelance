try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False


def compare_faces(id_image_path: str, selfie_path: str) -> dict:
    if not FACE_RECOGNITION_AVAILABLE:
        return {'match': None, 'confidence': None, 'error': 'face_recognition not available'}

    try:
        id_img = face_recognition.load_image_file(id_image_path)
        selfie_img = face_recognition.load_image_file(selfie_path)

        id_encs = face_recognition.face_encodings(id_img)
        selfie_encs = face_recognition.face_encodings(selfie_img)

        if not id_encs:
            return {'match': None, 'confidence': None, 'error': 'No face found in ID image'}
        if not selfie_encs:
            return {'match': None, 'confidence': None, 'error': 'No face found in selfie'}

        distance = face_recognition.face_distance([id_encs[0]], selfie_encs[0])[0]
        match = bool(distance < 0.6)
        confidence = round((1 - float(distance)) * 100, 1)
        return {'match': match, 'confidence': confidence, 'error': None}

    except Exception as e:
        return {'match': None, 'confidence': None, 'error': str(e)}
