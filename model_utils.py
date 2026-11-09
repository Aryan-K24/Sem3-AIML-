"""
model_utils.py
Core utilities for Versight:
- Hybrid ML + Linguistic forensic scoring
- Deceptive keyword & behavioral cue extraction
- Rating inflation calculation (Displayed vs Authentic)
- Star distribution shift analysis and trust grading
- Integrated aspect-based failure diagnostics & pros/cons extraction
"""

import re
import numpy as np
import pandas as pd

# High-frequency deceptive buzzwords found in incentivized and fake review rings
SUSPICIOUS_TRIGGER_WORDS = [
    "must buy", "best ever", "five stars", "100% recommended", "100% perfect",
    "flawless", "unbelievable", "perfect in every way", "buy immediately",
    "greatest product", "no competition", "amazing seller", "buy now",
    "top quality", "worth every penny", "everyone should buy", "buy it today",
    "works like a charm", "blown away", "exceeded expectations", "miracle",
    "game changer", "highly highly recommend", "perfect perfect", "amazing amazing"
]

GENUINE_EXPERIENCE_WORDS = [
    "months", "month", "returned", "broke", "disappointed", "complaint", "battery lasted",
    "battery life", "battery backup", "after a week", "customer service", "replacement",
    "pros and cons", "honest review", "daily use", "daily usage", "daily work", "office work",
    "durability", "wear and tear", "setup", "sound quality", "cable length", "noise cancellation",
    "build quality", "disconnects", "pairing was easy", "viewing angles", "multitasking",
    "for the price", "value for money", "verified purchase", "normal use", "lightweight",
    "slim", "fast charging", "everyday use"
]

def analyze_review_text(text, rating=None, model=None):
    """
    Analyzes an individual review combining:
    1. Base TF-IDF classifier probability
    2. Structural & behavioral linguistic signals (excessive caps, exclamation marks, buzzwords)
    """
    text_clean = str(text).strip()
    lower_text = text_clean.lower()
    
    # Base ML model probability
    prob = 0.40
    if model is not None:
        try:
            classes = list(model.classes_)
            suspicious_idx = classes.index("suspicious")
            prob = float(model.predict_proba([text_clean])[0][suspicious_idx])
        except Exception:
            prob = 0.40
            
    # Linguistic & behavioral feature extraction
    char_len = len(text_clean)
    words = text_clean.split()
    word_count = len(words)
    excl_count = text_clean.count("!")
    caps_count = sum(1 for c in text_clean if c.isupper())
    caps_ratio = (caps_count / max(char_len, 1)) * 100
    
    triggers_found = [w for w in SUSPICIOUS_TRIGGER_WORDS if w in lower_text]
    genuine_markers = [w for w in GENUINE_EXPERIENCE_WORDS if w in lower_text]
    
    # Flags & Hybrid adjustment
    flags = []
    bonus = 0.0
    
    if len(triggers_found) >= 2:
        bonus += 0.35
        flags.append(f"Clustered promotional buzzwords ({len(triggers_found)} detected: {', '.join(triggers_found[:3])})")
    elif len(triggers_found) == 1:
        bonus += 0.20
        flags.append(f"Promotional keyword trigger: '{triggers_found[0]}'")
        
    if excl_count >= 3:
        bonus += 0.15
        flags.append(f"Excessive exclamation marks ({excl_count} detected)")
        
    if caps_ratio > 25 and word_count > 3:
        bonus += 0.15
        flags.append(f"High uppercase shouting ratio ({caps_ratio:.1f}%)")
        
    if word_count < 8 and rating == 5 and len(triggers_found) > 0:
        bonus += 0.15
        flags.append("Extreme 5-star rating with brief generic praise")
        
    # Genuine attenuation: if realistic usage words are present and no deceptive triggers found
    if len(triggers_found) == 0:
        if len(genuine_markers) >= 2:
            bonus -= 0.32
        elif len(genuine_markers) == 1:
            bonus -= 0.22
        elif word_count >= 12 and excl_count <= 1 and caps_ratio < 10:
            # Descriptive natural review without promo triggers
            bonus -= 0.15
    else:
        if len(genuine_markers) >= 2:
            bonus -= 0.10
        elif len(genuine_markers) == 1:
            bonus -= 0.05
        
    final_prob = min(0.99, max(0.01, round(prob + bonus, 4)))
    label = "suspicious" if final_prob >= 0.50 else "genuine"
    
    return {
        "text": text_clean,
        "rating": rating,
        "suspicious_probability": final_prob,
        "authenticity_score": round(1.0 - final_prob, 4),
        "predicted_label": label,
        "char_len": char_len,
        "word_count": word_count,
        "exclamation_count": excl_count,
        "caps_ratio_pct": round(caps_ratio, 1),
        "triggers_found": triggers_found,
        "genuine_markers": genuine_markers,
        "flags": flags
    }


def compute_rating_inflation(reviews_df, rating_col="rating", text_col="review_text", model=None, target_displayed_rating=None):
    """
    Given a DataFrame of reviews for a product:
    - Calculates Displayed / Original Rating (or uses target_displayed_rating if provided)
    - Predicts suspicious probability for each review using hybrid ML + linguistic signals
    - Filters out suspicious reviews to obtain Authentic / Adjusted Rating
    - Computes exact Rating Inflation: (Displayed - Authentic)
    - Extracts why the product fails and genuine pros & cons
    - Returns comprehensive forensic diagnostics
    """
    df = reviews_df.copy()
    df[rating_col] = pd.to_numeric(df[rating_col], errors="coerce")
    df = df.dropna(subset=[rating_col])
    df = df[df[rating_col].between(1, 5)]
    
    total_reviews = len(df)
    if total_reviews == 0:
        return {
            "total_reviews": 0,
            "displayed_rating": 0.0,
            "authentic_rating": 0.0,
            "inflation_delta": 0.0,
            "inflation_pct": 0.0,
            "fake_pct": 0.0,
            "trust_grade": "N/A",
            "verdict": "No valid reviews",
            "aspect_analysis": {}
        }
        
    if target_displayed_rating is not None and float(target_displayed_rating) > 0:
        displayed_rating = round(float(target_displayed_rating), 2)
    else:
        displayed_rating = float(df[rating_col].mean())
    
    # Score each review
    probs = []
    is_suspicious_list = []
    triggers_list = []
    flags_list = []
    auth_scores = []
    
    for _, row in df.iterrows():
        t = str(row[text_col]) if text_col in df.columns else ""
        r = float(row[rating_col])
        res = analyze_review_text(t, rating=r, model=model)
        probs.append(res["suspicious_probability"])
        is_suspicious_list.append(res["predicted_label"] == "suspicious")
        triggers_list.append(res.get("triggers_found", []))
        flags_list.append(res.get("flags", []))
        auth_scores.append(res.get("authenticity_score", 0.5))
        
    df["suspicious_prob"] = probs
    df["is_suspicious"] = is_suspicious_list
    df["triggers"] = triggers_list
    df["flags"] = flags_list
    df["authenticity_score"] = auth_scores
    
    suspicious_count = int(df["is_suspicious"].sum())
    genuine_count = total_reviews - suspicious_count
    fake_pct = round(100.0 * suspicious_count / total_reviews, 1)
    
    genuine_df = df[~df["is_suspicious"]]
    
    # 1. Raw genuine mean from verified organic reviews
    if len(genuine_df) > 0:
        raw_genuine_mean = float(genuine_df[rating_col].mean())
    else:
        raw_genuine_mean = max(1.0, displayed_rating - 1.2)
        
    # 2. Fundamental Law of Rating Inflation Auditing:
    # When promotional/suspicious reviews are detected (fake_pct > 0),
    # the genuine customer rating CANNOT exceed the advertised store rating.
    # The genuine rating is strictly bounded: authentic_rating <= displayed_rating.
    if fake_pct > 0:
        inflation_penalty = round(max(0.18, (fake_pct / 100.0) * 0.85), 2)
        if raw_genuine_mean >= displayed_rating:
            # If remaining genuine reviews in the sample are all 5-stars,
            # calculate authentic rating by deflating the advertised rating:
            authentic_rating = round(displayed_rating - inflation_penalty, 2)
        else:
            # If genuine mean is already lower than advertised, blend with penalty
            authentic_rating = min(round(displayed_rating - 0.15, 2), round(raw_genuine_mean, 2))
    else:
        # Zero fake reviews: authentic rating equals displayed rating or raw mean
        authentic_rating = min(displayed_rating, round(raw_genuine_mean, 2))
        
    # Strictly enforce bounds: 1.0 <= authentic_rating <= displayed_rating <= 5.0
    authentic_rating = max(1.0, min(displayed_rating, round(authentic_rating, 2)))
    
    # Inflation Delta is strictly non-negative: Displayed - Authentic
    inflation_delta = max(0.0, round(displayed_rating - authentic_rating, 2))
    inflation_pct = round((inflation_delta / displayed_rating) * 100.0, 1) if displayed_rating > 0 else 0.0
    
    # Weighted Bayesian estimate
    weights = 1.0 - df["suspicious_prob"].clip(0.01, 0.99)
    weighted_rating = float((df[rating_col] * weights).sum() / weights.sum())
    weighted_rating = min(displayed_rating, round(weighted_rating, 2))
    
    # Trust Grade & Verdict (Always consistent with non-negative delta)
    if inflation_delta <= 0.15 and fake_pct <= 15:
        grade = "Grade A"
        verdict = "High Trust — Rating is authentic and organic"
        color = "#10B981"
    elif inflation_delta <= 0.40 and fake_pct <= 30:
        grade = "Grade B"
        verdict = f"Good Trust — Minor review noise; safe to purchase (+{inflation_delta:.2f}★ delta)"
        color = "#3B82F6"
    elif inflation_delta <= 0.75 and fake_pct <= 55:
        grade = "Grade C"
        verdict = f"Moderate Inflation — Advertised rating inflated by +{inflation_delta:.2f}★"
        color = "#F59E0B"
    elif inflation_delta <= 1.10:
        grade = "Grade D"
        verdict = f"Significant Inflation — Advertised rating distorted by +{inflation_delta:.2f}★"
        color = "#EF4444"
    else:
        grade = "Grade F"
        verdict = f"Severe Manipulation — Artificial rating boost (+{inflation_delta:.2f}★)"
        color = "#7F1D1D"
        
    # Star distribution
    star_dist_all = df[rating_col].value_counts().to_dict()
    star_dist_all = {int(s): int(star_dist_all.get(s, 0)) for s in range(1, 6)}
    
    star_dist_gen = genuine_df[rating_col].value_counts().to_dict() if len(genuine_df) > 0 else {}
    star_dist_gen = {int(s): int(star_dist_gen.get(s, 0)) for s in range(1, 6)}

    # Aspect-based Failure Mode Diagnostics and Pros/Cons
    try:
        from aspect_analyzer import extract_aspect_sentiment_and_failures
        aspect_data = extract_aspect_sentiment_and_failures(df)
    except Exception:
        aspect_data = {}
    
    return {
        "total_reviews": total_reviews,
        "displayed_rating": round(displayed_rating, 2),
        "authentic_rating": round(authentic_rating, 2),
        "weighted_rating": round(weighted_rating, 2),
        "inflation_delta": inflation_delta,
        "inflation_pct": inflation_pct,
        "fake_count": suspicious_count,
        "genuine_count": genuine_count,
        "fake_pct": fake_pct,
        "trust_grade": grade,
        "verdict": verdict,
        "color": color,
        "star_distribution_all": star_dist_all,
        "star_distribution_genuine": star_dist_gen,
        "classified_df": df,
        "aspect_analysis": aspect_data
    }
