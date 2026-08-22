import os
import sys
import io
import cv2
import numpy as np
from PIL import Image
from rembg import remove, new_session

def crop_tight_headshot(img_pil: Image.Image) -> Image.Image:
    """
    Crops image tightly around the head, face, and top shoulders.
    Uses OpenCV face detection if available, or relative proportion crop.
    """
    img_np = np.array(img_pil.convert("RGB"))
    height, width, _ = img_np.shape
    
    # Try OpenCV Haar Cascade frontal face detection
    face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    if os.path.exists(face_cascade_path):
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        face_cascade = cv2.CascadeClassifier(face_cascade_path)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
        
        if len(faces) > 0:
            # Pick largest face
            faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
            fx, fy, fw, fh = faces[0]
            print(f"Face detected at x={fx}, y={fy}, w={fw}, h={fh}")
            
            # Pad around face (more room on top for hair and bottom for neck/collar)
            pad_top = int(fh * 0.7)
            pad_bottom = int(fh * 1.1)
            pad_side = int(fw * 0.7)
            
            x1 = max(0, fx - pad_side)
            y1 = max(0, fy - pad_top)
            x2 = min(width, fx + fw + pad_side)
            y2 = min(height, fy + fh + pad_bottom)
            
            return img_pil.crop((x1, y1, x2, y2))

    # Fallback tight crop for head/shoulders: top 4% to 58% of height, 15% to 85% of width
    print("Using relative headshot crop bounds...")
    x1 = int(width * 0.12)
    y1 = int(height * 0.04)
    x2 = int(width * 0.88)
    y2 = int(height * 0.58)
    return img_pil.crop((x1, y1, x2, y2))

def prep_photo(input_path: str, output_path: str = None) -> str:
    """
    Preprocesses portrait photo:
    1. Crops tightly around head/face/shoulders
    2. Removes background with rembg
    3. Applies OpenCV CLAHE contrast enhancement
    4. Composites onto solid white background
    """
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    if not output_path:
        output_path = os.path.join(repo_root, "source-prepped.png")
        
    if not os.path.isabs(input_path):
        input_path = os.path.abspath(input_path)
        
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input image not found: {input_path}")
        
    print(f"Loading input photo from: {input_path}")
    raw_pil = Image.open(input_path)
    
    # Crop tight headshot
    cropped_pil = crop_tight_headshot(raw_pil)
    
    img_byte_arr = io.BytesIO()
    cropped_pil.save(img_byte_arr, format='PNG')
    input_bytes = img_byte_arr.getvalue()
    
    print("Removing background with rembg...")
    try:
        session = new_session("u2netp")
        output_bytes = remove(input_bytes, session=session)
    except Exception as err:
        print(f"u2netp session warning ({err}), falling back...")
        output_bytes = remove(input_bytes)
        
    img_rgba = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
    img_np = np.array(img_rgba)
    
    rgb = img_np[:, :, :3]
    alpha = img_np[:, :, 3] / 255.0  # 0..1
    
    # CLAHE contrast enhancement on L-channel
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)
    
    enhanced_lab = cv2.merge((cl, a_channel, b_channel))
    enhanced_rgb = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
    
    # Composite onto pure white background
    white_bg = np.ones_like(enhanced_rgb, dtype=np.uint8) * 255
    composite = (enhanced_rgb * alpha[:, :, np.newaxis] + white_bg * (1.0 - alpha[:, :, np.newaxis])).astype(np.uint8)
    
    result_pil = Image.fromarray(composite)
    result_pil.save(output_path, "PNG")
    print(f"Prepped photo saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(repo_root, "input-photo.png")
    if not os.path.exists(src):
        src = os.path.join(repo_root, "input.jpg")
    prep_photo(src)
