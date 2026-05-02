import cv2
import numpy as np
import mediapipe as mp
from PIL import Image


def estimate_measurements(image_path: str, height_cm: float) -> dict:
    """
    Estimate body measurements from a full body photo.

    Args:
        image_path: Path to full body photo
        height_cm: Real height of the person in cm (reference for scaling)

    Returns:
        dict with shoulder_width, torso_length, hip_width, recommended_size
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image from {image_path}")

    h, w = image.shape[:2]
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Detect pose
    mp_pose = mp.solutions.pose
    with mp_pose.Pose(static_image_mode=True, model_complexity=2) as pose:
        results = pose.process(image_rgb)

    if not results.pose_landmarks:
        raise ValueError("No pose detected. Please use a clear, full-body photo.")

    landmarks = results.pose_landmarks.landmark
    mp_lm = mp_pose.PoseLandmark

    def px(landmark_id):
        lm = landmarks[landmark_id]
        return np.array([lm.x * w, lm.y * h])

    # Key landmarks
    left_shoulder  = px(mp_lm.LEFT_SHOULDER)
    right_shoulder = px(mp_lm.RIGHT_SHOULDER)
    left_hip       = px(mp_lm.LEFT_HIP)
    right_hip      = px(mp_lm.RIGHT_HIP)
    nose           = px(mp_lm.NOSE)
    left_ankle     = px(mp_lm.LEFT_ANKLE)
    right_ankle    = px(mp_lm.RIGHT_ANKLE)

    # Pixel distances
    shoulder_px = np.linalg.norm(left_shoulder - right_shoulder)
    hip_px      = np.linalg.norm(left_hip - right_hip)
    torso_px    = np.linalg.norm(
        ((left_shoulder + right_shoulder) / 2) - ((left_hip + right_hip) / 2)
    )

    # Full body height in pixels (nose to ankle average)
    ankle_mid   = (left_ankle + right_ankle) / 2
    body_px     = np.linalg.norm(nose - ankle_mid)

    # Scale factor: real cm per pixel
    scale = height_cm / body_px if body_px > 0 else 1.0

    # Convert to cm
    shoulder_cm = round(shoulder_px * scale, 1)
    hip_cm      = round(hip_px * scale, 1)
    torso_cm    = round(torso_px * scale, 1)

    # Size recommendation based on shoulder width
    def recommend_size(shoulder_cm):
        if shoulder_cm < 38:
            return "S"
        elif shoulder_cm < 42:
            return "M"
        elif shoulder_cm < 46:
            return "L"
        else:
            return "XL"

    size = recommend_size(shoulder_cm)

    result = {
        "shoulder_width":    f"{shoulder_cm} cm",
        "torso_length":      f"{torso_cm} cm",
        "hip_width":         f"{hip_cm} cm",
        "recommended_size":  size
    }

    return result


def print_measurements(measurements: dict):
    """Pretty print measurements."""
    print("\n" + "=" * 40)
    print("   BODY MEASUREMENT RESULTS")
    print("=" * 40)
    for key, val in measurements.items():
        label = key.replace("_", " ").title()
        print(f"  {label:<22}: {val}")
    print("=" * 40)
