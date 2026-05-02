"""
main.py — Optional CLI runner for all tasks
Usage:
    python main.py --task tryon --person data/person.jpg --garment data/garment.jpg
    python main.py --task measure --image data/person.jpg --height 170
    python main.py --task recommend --community Muslim
    python main.py --task classify --image data/garment.jpg
"""

import argparse
import sys
import os

sys.path.append(os.path.dirname(__file__))


def run_tryon(args):
    from src.tryon.pipeline import run_tryon
    print(f"\nRunning Virtual Try-On...")
    output = run_tryon(args.person, args.garment, "outputs/tryon_result.png")
    print(f"Result saved to: {output}")


def run_measure(args):
    from src.measurement.estimator import estimate_measurements, print_measurements
    print(f"\nEstimating body measurements...")
    result = estimate_measurements(args.image, args.height)
    print_measurements(result)


def run_recommend(args):
    from src.recommendation.engine import load_products, recommend, print_recommendations
    print(f"\nGenerating recommendations for {args.community} user...")
    df = load_products("data/products.csv")
    user_profile = {
        "community": args.community,
        "preferred_categories": ["Ethnic Wear", "Religious", "Beauty"],
        "price_range": (0, 1500),
        "past_purchases": ["ethnic", "prayer", "festive"]
    }
    top, explanations = recommend(user_profile, df)
    print_recommendations(top, explanations, user_profile)


def run_classify(args):
    from src.tryon.classifier import load_model, classify_garment, print_classification
    print(f"\nClassifying garment...")
    model, processor = load_model()
    result = classify_garment(args.image, model, processor)
    print_classification(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Virtual Try-On Assessment CLI")
    parser.add_argument("--task", choices=["tryon", "measure", "recommend", "classify"], required=True)
    parser.add_argument("--person",   help="Path to person image (for tryon)")
    parser.add_argument("--garment",  help="Path to garment image (for tryon/classify)")
    parser.add_argument("--image",    help="Path to image (for measure/classify)")
    parser.add_argument("--height",   type=float, default=170, help="Person height in cm")
    parser.add_argument("--community", default="Muslim", help="User community")

    args = parser.parse_args()

    if args.task == "tryon":     run_tryon(args)
    elif args.task == "measure": run_measure(args)
    elif args.task == "recommend": run_recommend(args)
    elif args.task == "classify": run_classify(args)
