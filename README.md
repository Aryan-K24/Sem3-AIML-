# 🛡️ Versight — Electronics Review Authenticity, Failure Diagnostics & Rating Deflator

**Versight** is an end-to-end artificial intelligence and natural language processing forensic system. It detects deceptive, sponsored, and fake reviews on electronic devices listed on e-commerce marketplaces (Amazon, BestBuy, Flipkart), recalculates the **Actual Authentic Rating**, displays the exact **Rating Inflation Delta** (e.g. Advertised: **4.50★** vs Actual: **3.80★** -> **Inflated by +0.70★**), and conducts deep **Aspect-Based Failure Diagnostics & Root Cause Analysis** directly from real customer reviews.

---

## 🌟 Key Features

1. **🌐 Live E-Commerce URL Auditor & Rating Deflator:**
   - Paste any live Amazon product URL or ASIN (matches 2,990+ real indexed products or dynamically extracts reviews).
   - Enter/calibrate the advertised Amazon store star rating to reveal the **True Authentic Rating** and **Rating Inflation Delta**.
   - 1-Click presets for **iPhone 16 (4.5★ -> 3.8★)**, **Wireless Earbuds (4.5★ -> 3.8★)**, **18W Fast Charger (4.3★ -> 1.8★)**, and **Galaxy Z Fold (4.0★ -> 3.4★)**.

2. **🛠️ Product Failure Root Cause & Aspect-Based Pros/Cons Diagnostic Engine:**
   - **Why a Product Fails:** Automatically diagnoses acute hardware failure modes (Battery & Power, Durability & Build, Wireless Connectivity, Audio/Mic Quality, Comfort & Fit, Software Stability) with incidence rates and severity rankings.
   - **Direct Review Evidence Proof:** Surfaces exact customer quotes paired with actual star ratings supporting every diagnosed failure mode.
   - **Authentic Pros & Cons:** Extracts verified organic praise and honest limitations filtered strictly from genuine customer feedback.
   - **Aspect Health Scorecard:** Quantitative 0-100 breakdown across engineering dimensions.

3. **🔍 Deep-Dive Forensic Report & Storefront Catalog:**
   - 4 Hero metric cards: Advertised Given Rating, Actual Authentic Rating, Rating Inflation Delta, and Forensic Trust Grade (A to F).
   - Interactive **Star Distribution Shift Chart** visualizing the artificial 5-star spike against the organic customer curve.
   - 311 indexed electronic devices across 7 categories with quick drilldown failure diagnostics.

4. **📊 AI Model Studio, Viva Defense & Mathematical Optimization Engine:**
   - Transparent model benchmark comparison (Accuracy, Precision, Recall, F1-Score, ROC-AUC).
   - Test confusion matrix and top predictive linguistic tokens.
   - Interactive **Mathematical Training Engine (Gradient Descent)** demonstrating how multivariable calculus (gradients $\nabla J$ via the Chain Rule) minimizes Binary Cross-Entropy loss to train the classification pipeline.
   - Comprehensive viva examination defense questions and technical answers.

---

## 🚀 Quickstart Guide

### 1. Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. (Optional) Re-run Model Training & Benchmarking
The trained model (`model.joblib`), curated dataset (`data/curated_training_dataset.csv`), and metrics (`metrics.json`) are pre-bundled and work out of the box! To re-train candidate models:
```bash
python train_model.py
```

### 3. Launch the Interactive Web Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📈 Model Performance Benchmark

Models evaluated on held-out test split with Word (1-2) + Character (3-5) Sublinear TF-IDF FeatureUnion:

| Model Architecture | Accuracy | Precision (Suspicious) | Recall (Suspicious) | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Balanced TF-IDF)** 🏆 | **75.82%** | **72.90%** | **75.49%** | **0.7417** | **0.8276** |
| **Calibrated LinearSVC** | **76.55%** | **75.73%** | **72.13%** | **0.7389** | **0.8267** |
| **Multinomial Naive Bayes** | 75.09% | 71.89% | 75.30% | 0.7355 | 0.8207 |
| **Complement Naive Bayes** | 74.82% | 71.48% | 75.30% | 0.7334 | 0.8198 |
| **Calibrated SGD (Modified Huber)** | 74.45% | 72.64% | 71.34% | 0.7198 | 0.7940 |

---

## 📂 Project Structure

```
Versight/
├── app.py                              # Streamlit forensic dashboard & analytics UI
├── aspect_analyzer.py                  # Product failure root-cause & pros/cons extraction engine
├── gradient_descent_optimizer.py       # Calculus CIE-3 optimizer (BGD, SGD, MBGD, Gradient Ascent)
├── train_model.py                      # Multi-model benchmarking and training pipeline
├── prepare_data.py                     # Dataset curation and electronics indexing script
├── model_utils.py                      # Core inference, rating deflator, and forensic utilities
├── scraper.py                          # Amazon URL parser & 2,990+ ASIN review matcher
├── model.joblib                        # Best trained pipeline (Word + Char TF-IDF + Classifier)
├── metrics.json                        # Full evaluation results and confusion matrix
├── requirements.txt                    # Dependencies
├── README.md                           # Quickstart documentation
├── PROJECT_REPORT_AND_VIVA.md          # Full AIML project report and viva Q&A
├── CALCULUS_CIE3_GRADIENT_DESCENT_REPORT.md # Calculus CIE-3 Project Report (10 Marks)
└── data/
    ├── curated_training_dataset.csv    # 4,398 curated balanced training reviews
    ├── electronics_catalog.json        # 311 indexed electronics products
    └── asin_database.json              # 2,993 real Amazon products & 43,300+ reviews
```
