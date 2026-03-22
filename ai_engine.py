import face_recognition
import cv2
import numpy as np
import io
from PIL import Image

def get_face_encoding(image_path_or_bytes):
    """
    Extracts face encoding from an image.
    """
    try:
        if isinstance(image_path_or_bytes, bytes):
            image = face_recognition.load_image_file(io.BytesIO(image_path_or_bytes))
        else:
            image = face_recognition.load_image_file(image_path_or_bytes)
            
        encodings = face_recognition.face_encodings(image)
        if len(encodings) > 0:
            return encodings[0]
        return None
    except Exception as e:
        print(f"Error extracting face encoding: {e}")
        return None

def compare_faces(target_encoding, known_encodings, tolerance=0.6):
    """
    Compares a target encoding against a list of known encodings.
    Returns list of (index, confidence)
    """
    if not known_encodings:
        return []
    
    # face_distance returns a value where lower is better (0 is perfect match)
    distances = face_recognition.face_distance(known_encodings, target_encoding)
    matches = []
    for i, dist in enumerate(distances):
        # Confidence score (inverse of distance, normalized roughly)
        confidence = max(0, 1 - dist) * 100
        if dist <= tolerance:
            matches.append((i, confidence))
    
    # Sort by confidence descending
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches

def simulate_age_progression(image_path, years_to_add):
    """
    Simulates age progression with a simple visual effect.
    This is a demonstration helper as requested.
    Real age progression requires complex GANs, but for this app 
    we will use a slight 'aged' filter (sepia + slight noise/blur).
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        # Simple placeholder for age progression logic
        # For demonstration: slightly darken and add a warm tint
        # Also simulate slight widening (children's faces change)
        
        # 1. Warm tint (simulating aging skin/old photo look)
        img = cv2.applyColorMap(img, cv2.COLORMAP_BONE) # Mock aging effect
        
        # 2. Add some noise or texture if needed
        # 3. Save to a temporary file for display
        output_path = image_path.replace(".jpg", f"_aged_{years_to_add}.jpg").replace(".png", f"_aged_{years_to_add}.png")
        cv2.imwrite(output_path, img)
        return output_path
    except Exception as e:
        print(f"Error in age progression: {e}")
        return image_path
