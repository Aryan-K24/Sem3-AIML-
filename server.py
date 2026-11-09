"""
server.py
Versight — Standalone High-Performance Web Application
Flask backend serving the forensic AI review auditor, aspect failure analyzer, and catalog.
"""

import os
import re
import json
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory
import pandas as pd
import joblib

from model_utils import compute_rating_inflation, analyze_review_text
from aspect_analyzer import extract_aspect_sentiment_and_failures
from scraper import fetch_product_reviews_from_url, extract_asin_from_url, extract_title_from_url, clean_product_title

app = Flask(__name__, template_folder="templates", static_folder="static")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_PATH = BASE_DIR / "model.joblib"
METRICS_PATH = BASE_DIR / "metrics.json"
CATALOG_PATH = DATA_DIR / "electronics_catalog.json"

# Load AI Model and Data
model = None
if MODEL_PATH.exists():
    try:
        model = joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"Error loading model: {e}")

catalog = []
if CATALOG_PATH.exists():
    try:
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            catalog = json.load(f)
    except Exception as e:
        print(f"Error loading catalog: {e}")

metrics = {}
if METRICS_PATH.exists():
    try:
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            metrics = json.load(f)
    except Exception as e:
        print(f"Error loading metrics: {e}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/audit-url", methods=["POST"])
def api_audit_url():
    data = request.get_json() or {}
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "Please enter a valid Amazon product URL or ASIN."}), 400

    try:
        extracted = fetch_product_reviews_from_url(url, catalog_list=catalog)
        reviews_list = extracted.get("reviews", [])
        if not reviews_list:
            return jsonify({"error": "No reviews could be parsed from this product URL."}), 404

        df = pd.DataFrame(reviews_list)
        displayed_rating = extracted.get("displayed_rating")

        audit = compute_rating_inflation(
            df,
            rating_col="rating",
            text_col="review_text",
            model=model,
            target_displayed_rating=displayed_rating
        )

        classified_records = audit["classified_df"].to_dict(orient="records")
        for r in classified_records:
            if "review_text" in r:
                r["review_text"] = str(r["review_text"])

        return jsonify({
            "status": "success",
            "product_title": extracted.get("product_title", "Amazon Product"),
            "asin": extracted.get("asin", "N/A"),
            "source": extracted.get("source", "Live Amazon Storefront"),
            "displayed_rating": audit["displayed_rating"],
            "authentic_rating": audit["authentic_rating"],
            "inflation_delta": audit["inflation_delta"],
            "inflation_pct": audit["inflation_pct"],
            "fake_pct": audit["fake_pct"],
            "trust_grade": audit["trust_grade"],
            "verdict": audit["verdict"],
            "total_reviews": audit["total_reviews"],
            "star_distribution_all": audit.get("star_distribution_all", {}),
            "star_distribution_genuine": audit.get("star_distribution_genuine", {}),
            "aspect_analysis": audit.get("aspect_analysis", {}),
            "reviews": classified_records
        })
    except Exception as e:
        return jsonify({"error": f"Audit error: {str(e)}"}), 500


@app.route("/api/audit-paste", methods=["POST"])
def api_audit_paste():
    data = request.get_json() or {}
    raw_text = data.get("text", "").strip()
    product_title = data.get("title", "").strip() or "Direct Customer Paste"
    target_rating = data.get("store_rating")

    if not raw_text:
        return jsonify({"error": "Please paste at least one customer review."}), 400

    chunks = [c.strip() for c in re.split(r"\n\s*\n", raw_text) if c.strip()]
    parsed_revs = []
    for chunk in chunks:
        match_star = re.match(r"^([1-5](?:\.[0-9])?)\s*(?:stars?|★)?\s*\|\s*(.+)$", chunk, re.IGNORECASE | re.DOTALL)
        if match_star:
            star = float(match_star.group(1))
            body = match_star.group(2).strip()
        else:
            star = 5.0
            body = chunk
        if len(body) > 3:
            parsed_revs.append({"rating": star, "review_text": body})

    if not parsed_revs:
        return jsonify({"error": "Could not parse valid reviews from the input."}), 400

    try:
        df = pd.DataFrame(parsed_revs)
        disp_r = float(target_rating) if target_rating is not None and float(target_rating) > 0 else None

        audit = compute_rating_inflation(
            df,
            rating_col="rating",
            text_col="review_text",
            model=model,
            target_displayed_rating=disp_r
        )

        classified_records = audit["classified_df"].to_dict(orient="records")
        for r in classified_records:
            if "review_text" in r:
                r["review_text"] = str(r["review_text"])

        return jsonify({
            "status": "success",
            "product_title": product_title,
            "asin": "DIRECT-PASTE",
            "source": f"Direct Customer Paste ({len(parsed_revs)} Reviews)",
            "displayed_rating": audit["displayed_rating"],
            "authentic_rating": audit["authentic_rating"],
            "inflation_delta": audit["inflation_delta"],
            "inflation_pct": audit["inflation_pct"],
            "fake_pct": audit["fake_pct"],
            "trust_grade": audit["trust_grade"],
            "verdict": audit["verdict"],
            "total_reviews": audit["total_reviews"],
            "star_distribution_all": audit.get("star_distribution_all", {}),
            "star_distribution_genuine": audit.get("star_distribution_genuine", {}),
            "aspect_analysis": audit.get("aspect_analysis", {}),
            "reviews": classified_records
        })
    except Exception as e:
        return jsonify({"error": f"Paste audit error: {str(e)}"}), 500


@app.route("/api/catalog", methods=["GET"])
def api_catalog():
    category = request.args.get("category", "").strip().lower()
    query = request.args.get("q", "").strip().lower()

    filtered = catalog
    if category and category != "all":
        filtered = [p for p in filtered if p.get("category", "").lower() == category]
    if query:
        filtered = [p for p in filtered if query in p.get("title", "").lower() or query in p.get("asin", "").lower()]

    return jsonify({"count": len(filtered), "products": filtered[:60]})


@app.route("/api/catalog/<asin>", methods=["GET"])
def api_catalog_item(asin):
    asin_clean = asin.strip().upper()
    item = next((p for p in catalog if p.get("asin", "").upper() == asin_clean), None)
    if not item:
        return jsonify({"error": f"Product with ASIN {asin} not found in catalog."}), 404

    sample_revs = item.get("sample_reviews", [])
    revs = [{"rating": float(r.get("stars", 5)), "review_text": r.get("text", "")} for r in sample_revs]
    df = pd.DataFrame(revs) if revs else pd.DataFrame([{"rating": 5.0, "review_text": "Good"}])

    audit = compute_rating_inflation(
        df,
        rating_col="rating",
        text_col="review_text",
        model=model,
        target_displayed_rating=item.get("displayed_rating", 4.5)
    )

    return jsonify({
        "status": "success",
        "product_title": item.get("title", "Catalog Product"),
        "asin": item.get("asin"),
        "source": "Verified Electronics Benchmark Catalog",
        "category": item.get("category", "Electronics"),
        "displayed_rating": audit["displayed_rating"],
        "authentic_rating": audit["authentic_rating"],
        "inflation_delta": audit["inflation_delta"],
        "inflation_pct": audit["inflation_pct"],
        "fake_pct": audit["fake_pct"],
        "trust_grade": audit["trust_grade"],
        "verdict": audit["verdict"],
        "total_reviews": audit["total_reviews"],
        "star_distribution_all": audit.get("star_distribution_all", {}),
        "star_distribution_genuine": audit.get("star_distribution_genuine", {}),
        "aspect_analysis": audit.get("aspect_analysis", {}),
        "reviews": audit["classified_df"].to_dict(orient="records")
    })


@app.route("/api/metrics", methods=["GET"])
def api_metrics():
    return jsonify(metrics)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n==================================================")
    print(f">> Versight AI Standalone Server Running!")
    print(f">> Local URL: http://127.0.0.1:{port}")
    print(f"==================================================\n")
    app.run(host="127.0.0.1", port=port, debug=False)
