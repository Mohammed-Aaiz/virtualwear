import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel


# Garment categories
GARMENT_CLASSES = [
    "a top or shirt or blouse or kurta",
    "a bottom or pants or trousers or skirt or salwar",
    "a full length dress or abaya or gown or saree",
    "a headwear or hijab or turban or dupatta or scarf",
    "an accessory or jewellery or bag or shoes or watch",
]

CLASS_LABELS = ["Top", "Bottom", "Full Length", "Headwear", "Accessory"]


def load_model():
    """Load CLIP model and processor."""
    print("Loading CLIP model...")
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    print("Model loaded!")
    return model, processor


def classify_garment(image_path: str, model=None, processor=None) -> dict:
    """
    Classify a garment image using CLIP zero-shot classification.

    Args:
        image_path: Path to garment image
        model: CLIP model (loaded once for efficiency)
        processor: CLIP processor

    Returns:
        dict with class_label and confidence_score
    """
    if model is None or processor is None:
        model, processor = load_model()

    image = Image.open(image_path).convert("RGB")

    inputs = processor(
        text=GARMENT_CLASSES,
        images=image,
        return_tensors="pt",
        padding=True
    )

    with torch.no_grad():
        outputs = model(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1).squeeze().tolist()

    best_idx = probs.index(max(probs))
    result = {
        "class_label":       CLASS_LABELS[best_idx],
        "confidence_score":  f"{round(probs[best_idx] * 100, 2)}%",
        "all_scores": {
            CLASS_LABELS[i]: f"{round(p * 100, 2)}%" for i, p in enumerate(probs)
        }
    }
    return result


def print_classification(result: dict):
    print("\n" + "=" * 40)
    print("   GARMENT CLASSIFICATION RESULT")
    print("=" * 40)
    print(f"  Class      : {result['class_label']}")
    print(f"  Confidence : {result['confidence_score']}")
    print("\n  All Scores:")
    for label, score in result["all_scores"].items():
        print(f"    {label:<15}: {score}")
    print("=" * 40)
