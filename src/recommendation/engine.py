import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def load_products(csv_path: str) -> pd.DataFrame:
    """Load product dataset from CSV."""
    return pd.read_csv(csv_path)


def recommend(user_profile: dict, df: pd.DataFrame, top_n: int = 10):
    """
    Content-based recommendation engine.

    Args:
        user_profile: dict with keys:
            - community (str)
            - preferred_categories (list)
            - price_range (tuple)
            - past_purchases (list of tags)
        df: product DataFrame
        top_n: number of recommendations

    Returns:
        top_products (DataFrame), explanations (list of str)
    """

    # Step 1 — Filter by community
    filtered = df[df["community"] == user_profile["community"]].copy()
    if filtered.empty:
        return pd.DataFrame(), []

    # Step 2 — Filter by price range
    min_p, max_p = user_profile["price_range"]
    filtered = filtered[(filtered["price"] >= min_p) & (filtered["price"] <= max_p)]
    if filtered.empty:
        return pd.DataFrame(), []

    # Step 3 — TF-IDF content similarity
    user_text = " ".join(user_profile["past_purchases"]) + " " + " ".join(user_profile["preferred_categories"])
    filtered["combined"] = filtered["tags"] + " " + filtered["category"]

    vectorizer = TfidfVectorizer()
    all_texts = list(filtered["combined"]) + [user_text]
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    user_vec = tfidf_matrix[-1]
    product_vecs = tfidf_matrix[:-1]
    similarity = cosine_similarity(user_vec, product_vecs).flatten()
    filtered["relevance_score"] = similarity

    # Step 4 — Combined score: 50% relevance + 50% normalized rating
    filtered["final_score"] = (
        0.5 * filtered["relevance_score"] +
        0.5 * (filtered["rating"] / 5.0)
    )

    # Step 5 — Category boost for preferred categories
    filtered["final_score"] = filtered.apply(
        lambda r: r["final_score"] * 1.2 if r["category"] in user_profile["preferred_categories"] else r["final_score"],
        axis=1
    )

    # Step 6 — Sort and get top N
    top = filtered.sort_values("final_score", ascending=False).head(top_n).reset_index(drop=True)

    # Step 7 — Generate explanations
    explanations = []
    for _, row in top.iterrows():
        reasons = []
        if row["category"] in user_profile["preferred_categories"]:
            reasons.append(f"matches your preferred category '{row['category']}'")
        if row["rating"] >= 4.7:
            reasons.append(f"highly rated at {row['rating']}/5")
        if row["price"] <= 500:
            reasons.append("budget friendly")
        tags = row["tags"].split()
        matched = [t for t in tags if t in user_profile["past_purchases"]]
        if matched:
            reasons.append(f"similar to past purchases ({', '.join(matched)})")
        explanations.append(
            "Recommended because it " + (", ".join(reasons) if reasons else "fits your community profile")
        )

    return top, explanations


def print_recommendations(top_products: pd.DataFrame, explanations: list, user_profile: dict):
    """Pretty print recommendations."""
    print("=" * 70)
    print(f"TOP RECOMMENDATIONS FOR {user_profile['community'].upper()} USER")
    print("=" * 70)
    for i, (_, row) in enumerate(top_products.iterrows()):
        print(f"\n#{i+1}  {row['name']}")
        print(f"     Category : {row['category']}")
        print(f"     Price    : ₹{row['price']}")
        print(f"     Rating   : {row['rating']}/5")
        print(f"     Score    : {round(row['final_score'], 3)}")
        print(f"     Why      : {explanations[i]}")
    print("\n" + "=" * 70)
