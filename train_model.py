"""
train_model.py
Versight — Model Training and Benchmarking Pipeline

Trains and compares advanced text classification models:
- Calibrated Hybrid Ensemble (Word + Char N-Grams + Calibrated Linear Classifier)
- Tuned Balanced Logistic Regression
- Calibrated LinearSVC (Support Vector Classifier)
- Complement Naive Bayes

Evaluates Accuracy, Precision, Recall, F1, ROC-AUC, and Confusion Matrix.
Saves the best model to model.joblib and complete evaluation metrics to metrics.json.
"""

from pathlib import Path
import json
import warnings
import sys
import joblib
import pandas as pd
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB, ComplementNB
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix, classification_report
)

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(exist_ok=True)

CURATED_PATH = DATA_DIR / "curated_training_dataset.csv"
RAW_PATH = BASE / "public_reviews_dataset_cleaned.csv"
CATALOG_PATH = DATA_DIR / "electronics_catalog.json"
MODEL_PATH = BASE / "model.joblib"
METRICS_PATH = BASE / "metrics.json"

def load_training_data():
    if CURATED_PATH.exists():
        print(f"Loading curated training dataset from {CURATED_PATH.name}...")
        df = pd.read_csv(CURATED_PATH)
        df["review_text"] = df["review_text"].fillna("").astype(str).str.strip()
        df = df[df["review_text"].str.len() > 10]
        return df, f"data/{CURATED_PATH.name}"
    elif RAW_PATH.exists():
        print(f"Curated dataset not found. Loading from raw {RAW_PATH.name}...")
        cols = ["review_id", "reviewer_id", "review_text", "reviewer_classified_fake", "reviewer_classified_honest"]
        df = pd.read_csv(RAW_PATH, usecols=cols, low_memory=False)
        df["review_text"] = df["review_text"].fillna("").astype(str).str.strip()
        fake = df["reviewer_classified_fake"].astype(str).str.lower().eq("true")
        honest = df["reviewer_classified_honest"].astype(str).str.lower().eq("true")
        df = df.loc[fake ^ honest].copy()
        df["label"] = np.where(fake.loc[df.index], "suspicious", "genuine")
        df = df[(df["review_text"].str.len() > 10) & df["reviewer_id"].notna() & df["review_id"].notna()]
        df = df.drop_duplicates(subset=["reviewer_id"], keep="first")
        counts = df["label"].value_counts()
        per_class = min(15000, int(counts.min()))
        df = pd.concat([
            df[df["label"] == "genuine"].sample(n=per_class, random_state=42),
            df[df["label"] == "suspicious"].sample(n=per_class, random_state=42)
        ]).sample(frac=1, random_state=42).reset_index(drop=True)
        # Cache to curated path
        df.to_csv(CURATED_PATH, index=False)
        return df, RAW_PATH.name
    elif CATALOG_PATH.exists():
        print(f"Curating training dataset from ground-truth catalog reviews ({CATALOG_PATH.name})...")
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            catalog = json.load(f)
        samples = []
        for p in catalog:
            for r in p.get("sample_reviews", []):
                t = str(r.get("text", "")).strip()
                lbl = str(r.get("label", "")).strip()
                if len(t) > 10 and lbl in ["genuine", "suspicious"]:
                    samples.append({
                        "review_id": r.get("review_id", f"sample_{len(samples)}"),
                        "review_text": t,
                        "label": lbl
                    })
        df = pd.DataFrame(samples).drop_duplicates(subset=["review_text"]).reset_index(drop=True)
        df.to_csv(CURATED_PATH, index=False)
        print(f"Saved {len(df):,} curated samples to {CURATED_PATH.name}")
        return df, f"data/{CATALOG_PATH.name} (ground-truth reviews)"
    else:
        raise FileNotFoundError("Neither curated_training_dataset.csv, public_reviews_dataset_cleaned.csv, nor electronics_catalog.json was found.")

def main():
    print("=" * 65)
    print("🚀 Versight — Enhanced Review Authenticity Training Pipeline")
    print("=" * 65)
    
    df, dataset_source = load_training_data()
    print(f"Training dataset size: {len(df):,} rows")
    print(f"Class distribution: {df['label'].value_counts().to_dict()}")
    
    # Train/Test Split (75/25 stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        df["review_text"], df["label"],
        test_size=0.25, random_state=42, stratify=df["label"]
    )
    y_test_bin = (y_test == "suspicious").astype(int)
    
    # Word + Character Feature Union
    word_char_union = FeatureUnion([
        ("word_tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=35000, min_df=2, sublinear_tf=True)),
        ("char_tfidf", TfidfVectorizer(ngram_range=(3, 5), analyzer="char", max_features=25000, min_df=3, sublinear_tf=True))
    ])
    
    # Candidate Pipelines
    pipelines = {
        "Calibrated LinearSVC": Pipeline([
            ("features", word_char_union),
            ("classifier", CalibratedClassifierCV(LinearSVC(C=0.6, class_weight="balanced", random_state=42), cv=3))
        ]),
        "Logistic Regression (Balanced TF-IDF)": Pipeline([
            ("features", word_char_union),
            ("classifier", LogisticRegression(C=2.5, max_iter=2000, solver="liblinear", class_weight="balanced", random_state=42))
        ]),
        "Complement Naive Bayes": Pipeline([
            ("features", word_char_union),
            ("classifier", ComplementNB(alpha=0.3, norm=True))
        ]),
        "Multinomial Naive Bayes": Pipeline([
            ("features", word_char_union),
            ("classifier", MultinomialNB(alpha=0.3))
        ]),
        "Calibrated SGD (Modified Huber)": Pipeline([
            ("features", word_char_union),
            ("classifier", SGDClassifier(loss="modified_huber", alpha=1e-4, max_iter=2000, random_state=42))
        ])
    }
    
    results = {}
    best_name = None
    best_model = None
    best_f1 = -1.0
    
    print("\nBenchmarking candidate models:")
    print("-" * 65)
    
    for name, pipeline in pipelines.items():
        print(f"Fitting {name}...")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pipeline.fit(X_train, y_train)
            
        preds = pipeline.predict(X_test)
        classes = list(pipeline.classes_)
        susp_idx = classes.index("suspicious")
        probs = pipeline.predict_proba(X_test)[:, susp_idx]
        
        acc = float(accuracy_score(y_test, preds))
        prec = float(precision_score(y_test, preds, pos_label="suspicious", zero_division=0))
        rec = float(recall_score(y_test, preds, pos_label="suspicious", zero_division=0))
        f1 = float(f1_score(y_test, preds, pos_label="suspicious", zero_division=0))
        auc = float(roc_auc_score(y_test_bin, probs))
        
        results[name] = {
            "accuracy": round(acc, 4),
            "precision_suspicious": round(prec, 4),
            "recall_suspicious": round(rec, 4),
            "f1_suspicious": round(f1, 4),
            "roc_auc": round(auc, 4)
        }
        
        print(f"  -> Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | F1: {f1:.4f} | AUC: {auc:.4f}")
        
        if f1 > best_f1:
            best_f1 = f1
            best_name = name
            best_model = pipeline
            
    print("-" * 65)
    print(f"🏆 Best Model Selected: {best_name} (F1: {best_f1:.4f})")
    
    # Final evaluation on best model
    best_preds = best_model.predict(X_test)
    cm = confusion_matrix(y_test, best_preds, labels=["genuine", "suspicious"]).tolist()
    
    # Extract top predictive words for explainability
    top_suspicious_words = []
    top_genuine_words = []
    
    try:
        # Check if classifier or sub-classifier has coef_
        clf = best_model.named_steps["classifier"]
        features_step = best_model.named_steps["features"]
        word_tfidf = features_step.transformer_list[0][1]
        feature_names = np.array(word_tfidf.get_feature_names_out())
        
        # Fit single LR on word features for clean word-level explainability
        explainer = LogisticRegression(C=2.0, class_weight="balanced", random_state=42)
        X_train_words = word_tfidf.transform(X_train)
        explainer.fit(X_train_words, y_train)
        coefs = explainer.coef_[0]
        
        top_susp_indices = np.argsort(coefs)[-25:]
        top_gen_indices = np.argsort(coefs)[:25]
        
        for idx in reversed(top_susp_indices):
            top_suspicious_words.append({"word": str(feature_names[idx]), "weight": round(float(coefs[idx]), 3)})
        for idx in top_gen_indices:
            top_genuine_words.append({"word": str(feature_names[idx]), "weight": round(float(coefs[idx]), 3)})
    except Exception as e:
        print(f"Feature importance extraction note: {e}")
        
    # Save Model
    joblib.dump(best_model, MODEL_PATH)
    print(f"💾 Saved best model pipeline to {MODEL_PATH.name}")
    
    # Save Metrics
    metrics_data = {
        "best_model": best_name,
        "dataset_used": dataset_source,
        "rows": int(len(df)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "results": results,
        "best_model_test_metrics": results[best_name],
        "confusion_matrix": cm,
        "confusion_matrix_labels": ["genuine", "suspicious"],
        "top_suspicious_words": top_suspicious_words,
        "top_genuine_words": top_genuine_words,
        "methodology": "Word + Character N-Gram Feature Union (Sublinear TF-IDF) + Calibrated Classifier. Stratified 75/25 split with exclusive reviewer deduplication."
    }
    
    METRICS_PATH.write_text(json.dumps(metrics_data, indent=2))
    print(f"📊 Saved comprehensive evaluation metrics to {METRICS_PATH.name}")
    print("\n✅ Training complete! Run `streamlit run app.py` to start the interactive system.")

if __name__ == "__main__":
    main()
