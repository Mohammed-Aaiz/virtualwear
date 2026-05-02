import cv2
import numpy as np
from rembg import remove
from PIL import Image
import os


def remove_background(image_path: str) -> np.ndarray:
    with open(image_path, "rb") as f:
        input_bytes = f.read()
    output_bytes = remove(input_bytes)
    from io import BytesIO
    img = Image.open(BytesIO(output_bytes)).convert("RGBA")
    return np.array(img)


def detect_pose_landmarks(image_bgr: np.ndarray):
    try:
        import mediapipe as mp
        mp_pose = mp.solutions.pose
        with mp_pose.Pose(static_image_mode=True, model_complexity=1) as pose:
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)
        return results.pose_landmarks
    except Exception as e:
        print(f"MediaPipe failed: {e}. Using fallback.")
        return None


def get_key_points_from_landmarks(landmarks, image_shape):
    h, w = image_shape[:2]
    import mediapipe as mp
    mp_pose = mp.solutions.pose.PoseLandmark

    def get_point(lid):
        lm = landmarks.landmark[lid]
        return (int(lm.x * w), int(lm.y * h))

    return {
        "left_shoulder":  get_point(mp_pose.LEFT_SHOULDER),
        "right_shoulder": get_point(mp_pose.RIGHT_SHOULDER),
        "left_hip":       get_point(mp_pose.LEFT_HIP),
        "right_hip":      get_point(mp_pose.RIGHT_HIP),
    }


def get_key_points_fallback(image_rgba: np.ndarray) -> dict:
    h, w = image_rgba.shape[:2]
    alpha = image_rgba[:, :, 3]
    rows = np.any(alpha > 10, axis=1)
    cols = np.any(alpha > 10, axis=0)

    if not rows.any() or not cols.any():
        top, bottom = int(h * 0.15), int(h * 0.75)
        left, right = int(w * 0.25), int(w * 0.75)
    else:
        top    = np.argmax(rows)
        bottom = h - np.argmax(rows[::-1])
        left   = np.argmax(cols)
        right  = w - np.argmax(cols[::-1])

    body_h = bottom - top
    body_w = right - left
    cx = (left + right) // 2

    return {
        "left_shoulder":  (cx - int(body_w * 0.42), top + int(body_h * 0.20)),
        "right_shoulder": (cx + int(body_w * 0.42), top + int(body_h * 0.20)),
        "left_hip":       (cx - int(body_w * 0.30), top + int(body_h * 0.55)),
        "right_hip":      (cx + int(body_w * 0.30), top + int(body_h * 0.55)),
    }


def warp_garment_onto_body(person_rgba, garment_rgba, keypoints):
    ls = keypoints["left_shoulder"]
    rs = keypoints["right_shoulder"]
    lh = keypoints["left_hip"]
    rh = keypoints["right_hip"]

    shoulder_px    = abs(ls[0] - rs[0])
    shoulder_width = int(shoulder_px * 2.4)
    torso_height   = int(abs(((ls[1]+rs[1])//2) - ((lh[1]+rh[1])//2)) * 2.3)

    if shoulder_width < 30:
        shoulder_width = int(person_rgba.shape[1] * 0.62)
    if torso_height < 30:
        torso_height = int(person_rgba.shape[0] * 0.62)

    garment_pil     = Image.fromarray(garment_rgba).convert("RGBA")
    garment_resized = garment_pil.resize((shoulder_width, torso_height), Image.LANCZOS)

    body_cx = (ls[0] + rs[0]) // 2
    top_x   = body_cx - shoulder_width // 2
    top_y   = min(ls[1], rs[1]) - int(torso_height * 0.07)

    result = Image.fromarray(person_rgba).convert("RGBA")
    result.paste(garment_resized, (top_x, top_y), garment_resized)
    return np.array(result)


def run_tryon(person_image_path, garment_image_path, output_path="outputs/tryon_result.png"):
    print("Step 1: Removing backgrounds...")
    person_rgba  = remove_background(person_image_path)
    garment_rgba = remove_background(garment_image_path)

    print("Step 2: Detecting body pose...")
    person_bgr = cv2.cvtColor(person_rgba[:, :, :3], cv2.COLOR_RGB2BGR)
    landmarks  = detect_pose_landmarks(person_bgr)

    print("Step 3: Extracting keypoints...")
    if landmarks is not None:
        keypoints = get_key_points_from_landmarks(landmarks, person_rgba.shape)
        print("  Using MediaPipe landmarks")
    else:
        keypoints = get_key_points_fallback(person_rgba)
        print("  Using silhouette fallback")

    print("Step 4: Warping garment...")
    result_rgba = warp_garment_onto_body(person_rgba, garment_rgba, keypoints)

    print("Step 5: Saving...")
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    result_pil = Image.fromarray(result_rgba).convert("RGBA")
    bg = Image.new("RGBA", result_pil.size, (255, 255, 255, 255))
    bg.paste(result_pil, mask=result_pil.split()[3])
    bg.convert("RGB").save(output_path)
    print(f"Done! Saved to: {output_path}")
    return output_path