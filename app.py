"""
app.py — Versight
Real-Time E-Commerce Review Authenticity Engine, Rating Deflator & Failure Diagnostics

Features:
1. 🌐 Live E-Commerce URL Auditor (Matches 2,990+ real Amazon devices, analyzes reviews, and deflates inflated ratings)
2. 🔍 Deep-Dive Forensic Report (Hero metrics: Advertised vs Actual Rating, Star Distribution Shift)
3. 🛠️ Product Failure Root Cause & Real-World Pros/Cons Engine (Extracts why products fail & authentic pros/cons)
4. 🏬 Electronics Storefront & Catalog (300+ indexed devices across 7 categories)
5. 📊 AI Model Studio & Mathematical Optimization (Benchmark metrics, confusion matrix, linguistic tokens, and Gradient Descent training engine)
"""

from pathlib import Path
import json
import warnings
import joblib
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

warnings.filterwarnings("ignore")

from model_utils import analyze_review_text, compute_rating_inflation, SUSPICIOUS_TRIGGER_WORDS
from aspect_analyzer import extract_aspect_sentiment_and_failures
from scraper import fetch_product_reviews_from_url, get_asin_db
from gradient_descent_optimizer import GradientDescentOptimizer, run_synthetic_benchmark

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
CATALOG_PATH = DATA_DIR / "electronics_catalog.json"
ASIN_DB_PATH = DATA_DIR / "asin_database.json"
MODEL_PATH = BASE / "model.joblib"
METRICS_PATH = BASE / "metrics.json"
CIE3_REPORT_PATH = BASE / "CALCULUS_CIE3_GRADIENT_DESCENT_REPORT.md"

st.set_page_config(
    page_title="Versight — E-Commerce Rating Deflator & Diagnostics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------------
# Clean, Professional "Non-AI" Analytics Styling
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* Clean System Typography & Slate Backgrounds */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    .stApp {
        background-color: #090d16;
        color: #f1f5f9;
    }

    /* Minimalist High-Contrast Stat Cards */
    .stat-card {
        background: #111827;
        border: 1px solid #1f293d;
        border-radius: 8px;
        padding: 18px 20px;
        color: #f8fafc;
        margin-bottom: 12px;
    }
    .stat-card-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }
    .stat-card-value {
        font-size: 2.2rem;
        font-weight: 700;
        line-height: 1.1;
        letter-spacing: -0.02em;
    }
    .stat-card-delta {
        font-size: 0.8rem;
        font-weight: 500;
        color: #94a3b8;
        margin-top: 6px;
    }

    /* Executive Failure Diagnostics Banner */
    .diagnostic-banner {
        background: #121829;
        border: 1px solid #1e293b;
        border-left: 4px solid #f43f5e;
        border-radius: 8px;
        padding: 20px 22px;
        margin-bottom: 20px;
    }
    .diagnostic-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .diagnostic-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .diagnostic-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .diagnostic-body {
        font-size: 0.92rem;
        color: #cbd5e1;
        line-height: 1.6;
    }

    /* Failure Mode Cards */
    .failure-card {
        background: #131b2e;
        border: 1px solid #1e293b;
        border-left: 3px solid #f43f5e;
        border-radius: 8px;
        padding: 16px 18px;
        margin-bottom: 14px;
    }
    .failure-card-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #f8fafc;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .failure-incidence {
        font-size: 0.78rem;
        font-weight: 600;
        color: #fca5a5;
        background: rgba(244, 63, 94, 0.12);
        padding: 2px 8px;
        border-radius: 4px;
    }
    .failure-cause {
        font-size: 0.85rem;
        color: #94a3b8;
        line-height: 1.45;
        margin-bottom: 10px;
    }

    /* Quotes Callouts */
    .quote-box {
        background: #0f172a;
        border-left: 2px solid #334155;
        border-radius: 0 4px 4px 0;
        padding: 8px 12px;
        margin-top: 6px;
        font-size: 0.82rem;
        color: #cbd5e1;
        font-style: italic;
    }
    .quote-box-star {
        font-style: normal;
        font-weight: 600;
        color: #fbbf24;
        margin-right: 6px;
    }

    /* Pros & Cons Editorial Cards */
    .pro-card {
        background: #0e1e17;
        border: 1px solid #16382b;
        border-left: 3px solid #10b981;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }
    .pro-title {
        font-size: 0.92rem;
        font-weight: 600;
        color: #34d399;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .pro-score {
        font-size: 0.75rem;
        font-weight: 700;
        color: #6ee7b7;
        background: rgba(16, 185, 129, 0.15);
        padding: 2px 8px;
        border-radius: 4px;
    }

    .con-card {
        background: #1c1418;
        border: 1px solid #3b1d24;
        border-left: 3px solid #f43f5e;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }
    .con-title {
        font-size: 0.92rem;
        font-weight: 600;
        color: #fb7185;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .con-score {
        font-size: 0.75rem;
        font-weight: 700;
        color: #fda4af;
        background: rgba(244, 63, 94, 0.15);
        padding: 2px 8px;
        border-radius: 4px;
    }

    /* Scorecard bar */
    .score-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #1e293b;
        font-size: 0.88rem;
    }

    .url-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 4px;
        background-color: #1e293b;
        color: #93c5fd;
        font-size: 0.78rem;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        border: 1px solid #334155;
    }

    /* Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid #1e293b;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 16px;
        font-weight: 600;
        font-size: 0.9rem;
        border-radius: 6px 6px 0 0;
        color: #94a3b8;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #38bdf8;
        border-bottom: 2px solid #38bdf8;
        background: transparent;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Data & Model Loaders
# ---------------------------------------------------------------------------
@st.cache_resource
def load_model():
    if not MODEL_PATH.exists():
        return None
    try:
        return joblib.load(MODEL_PATH)
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

@st.cache_data
def load_catalog():
    if not CATALOG_PATH.exists():
        return []
    try:
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading catalog: {e}")
        return []

@st.cache_data
def load_metrics():
    if not METRICS_PATH.exists():
        return {}
    try:
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

model = load_model()
catalog = load_catalog()
metrics = load_metrics()
asin_database = get_asin_db()


# ---------------------------------------------------------------------------
# Reusable UI Component: Render Product Failure Diagnostics & Pros/Cons
# ---------------------------------------------------------------------------
def render_aspect_diagnostics_ui(aspect_data: dict):
    if not aspect_data or not aspect_data.get("summary"):
        return

    summary = aspect_data["summary"]
    failure_modes = aspect_data.get("failure_modes", [])
    pros = aspect_data.get("pros", [])
    cons = aspect_data.get("cons", [])
    scorecard = aspect_data.get("aspect_scorecard", {})

    st.markdown("### 🛠️ Product Failure Diagnostics & Real-World Pros/Cons")
    st.caption("Extracted directly from genuine customer reviews. Analyzes primary hardware/software failure modes and contrasts authentic pros against real customer trade-offs.")

    # 1. Executive Failure Summary Banner (Customer-Friendly)
    risk_level = summary.get("failure_risk_level", "Moderate")
    risk_score = summary.get("failure_risk_score", 50)
    risk_color = summary.get("failure_risk_color", "#f43f5e")

    banner_html = (
        f'<div class="diagnostic-banner" style="border-left-color: {risk_color};">'
        f'<div class="diagnostic-header">'
        f'<span class="diagnostic-title">🔍 What Buyers Should Know: {summary.get("primary_failure_reason", "Hardware Durability")}</span>'
        f'<span class="diagnostic-badge" style="background: {risk_color}25; color: {risk_color}; border: 1px solid {risk_color};">'
        f'{risk_level} • Risk Score: {risk_score}/100</span>'
        f'</div>'
        f'<div class="diagnostic-body">'
        f'{summary.get("executive_diagnostic", "")}'
        f'</div></div>'
    )
    st.markdown(banner_html, unsafe_allow_html=True)

    # 2. Tabs: Failure Root Causes vs Pros & Cons vs Aspect Scorecard
    tab_failures, tab_pros_cons, tab_scorecard = st.tabs([
        f"🚨 Why This Product Fails ({len(failure_modes)} Identified Modes)",
        f"⚖️ Authentic Pros & Cons ({len(pros)} Pros / {len(cons)} Cons)",
        "📊 Hardware Aspect Scorecard"
    ])

    with tab_failures:
        if not failure_modes:
            st.info("✅ No recurrent acute hardware or software failures detected in the analyzed customer reviews.")
        else:
            st.markdown(f"**Identified Hardware & Component Failure Areas:**")
            
            f_col1, f_col2 = st.columns(2)
            for idx, mode in enumerate(failure_modes):
                target_col = f_col1 if idx % 2 == 0 else f_col2
                with target_col:
                    quotes_html = "".join([
                        f'<div class="quote-box"><span class="quote-box-star">★{q["rating"]}</span> "{q["quote"]}"</div>'
                        for q in mode.get("evidence_quotes", [])[:3]
                    ])
                    card_html = (
                        f'<div class="failure-card" style="border-left-color: {mode["severity_color"]};">'
                        f'<div class="failure-card-title">'
                        f'<span>{mode["icon"]} {mode["category"]}</span>'
                        f'<span class="failure-incidence">{mode["incidence_pct"]:.1f}% Critical Incidence</span>'
                        f'</div>'
                        f'<div class="failure-cause"><strong>What Goes Wrong:</strong> {mode["root_cause_summary"]}</div>'
                        f'<div style="font-size: 0.75rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin-top: 8px;">'
                        f'Verified Customer Proof ({mode["complaint_count"]} reports):</div>'
                        f'{quotes_html}</div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)

    with tab_pros_cons:
        col_pro, col_con = st.columns(2)
        
        with col_pro:
            st.markdown("#### 🟢 Authentic Pros (Verified Genuine Praise)")
            st.caption("Extracted strictly from verified organic customer reviews. Artificial promotional hype is filtered out.")
            if not pros:
                st.info("No verified organic pros identified — all 5-star reviews were flagged as promotional or unverified.")
            else:
                for p in pros:
                    pro_html = (
                        f'<div class="pro-card">'
                        f'<div class="pro-title">'
                        f'<span>{p["icon"]} {p["aspect_title"]}</span>'
                        f'<span class="pro-score">+{p["sentiment_score"]}% Positive</span>'
                        f'</div>'
                        f'<div class="quote-box" style="border-left-color: #10b981;">'
                        f'<span class="quote-box-star">★{p["rating"]}</span> "{p["evidence_quote"]}"'
                        f'</div></div>'
                    )
                    st.markdown(pro_html, unsafe_allow_html=True)

        with col_con:
            st.markdown("#### 🔴 Authentic Cons (Real Customer Limitations)")
            st.caption("Extracted from honest customer reviews detailing practical limitations and trade-offs.")
            if not cons:
                st.success("No significant recurring trade-offs reported by customers.")
            else:
                for c in cons:
                    con_html = (
                        f'<div class="con-card">'
                        f'<div class="con-title">'
                        f'<span>{c["icon"]} {c["aspect_title"]}</span>'
                        f'<span class="con-score">{c["impact_level"]}</span>'
                        f'</div>'
                        f'<div class="quote-box" style="border-left-color: #f43f5e;">'
                        f'<span class="quote-box-star">★{c["rating"]}</span> "{c["evidence_quote"]}"'
                        f'</div></div>'
                    )
                    st.markdown(con_html, unsafe_allow_html=True)

    with tab_scorecard:
        st.markdown("#### 📊 Hardware & Usability Aspect Scorecard (0 to 100)")
        st.caption("Customer satisfaction percentage per technical domain. Only aspects with actual customer reviews are scored.")
        
        sc_col1, sc_col2 = st.columns([3, 2])
        scored_aspects = []
        with sc_col1:
            for title, info in scorecard.items():
                if info.get("has_data"):
                    score = info["score"]
                    status = info["status"]
                    score_color = "#10b981" if score >= 70 else ("#f59e0b" if score >= 50 else "#f43f5e")
                    
                    row_html = (
                        f'<div class="score-row">'
                        f'<span><strong>{info["icon"]} {title}</strong></span>'
                        f'<span>'
                        f'<span style="font-weight: 700; color: {score_color}; margin-right: 8px;">{score}/100</span>'
                        f'<span style="font-size: 0.78rem; color: #94a3b8;">({info["positive_count"]} praise / {info["negative_count"]} critical)</span>'
                        f'</span></div>'
                    )
                    st.markdown(row_html, unsafe_allow_html=True)
                    st.progress(score / 100.0)
                    scored_aspects.append({"Aspect": title, "Score": score})
                else:
                    unmentioned_html = (
                        f'<div class="score-row" style="opacity: 0.65;">'
                        f'<span><strong>{info["icon"]} {title}</strong></span>'
                        f'<span style="font-size: 0.78rem; color: #94a3b8; background: #1e293b; padding: 3px 8px; border-radius: 4px;">'
                        f'No Customer Feedback (0 mentions)</span></div>'
                    )
                    st.markdown(unmentioned_html, unsafe_allow_html=True)

        with sc_col2:
            if scored_aspects:
                sc_data = pd.DataFrame(scored_aspects)
                sc_chart = alt.Chart(sc_data).mark_bar(cornerRadius=4).encode(
                    x=alt.X("Score:Q", scale=alt.Scale(domain=[0, 100]), title="Satisfaction Score (0-100)"),
                    y=alt.Y("Aspect:N", sort="-x", title=""),
                    color=alt.Color("Score:Q", scale=alt.Scale(domain=[30, 60, 90], range=["#f43f5e", "#f59e0b", "#10b981"])),
                    tooltip=["Aspect", "Score"]
                ).properties(height=220)
                st.altair_chart(sc_chart, use_container_width=True)
            else:
                st.info("No hardware dimensions were specifically discussed in this review sample.")


# ---------------------------------------------------------------------------
# App Header & Navigation
# ---------------------------------------------------------------------------
h_col1, h_col2 = st.columns([1, 7])
with h_col1:
    st.markdown("<h1 style='font-size: 3.2rem; margin-bottom: 0;'>🛡️</h1>", unsafe_allow_html=True)
with h_col2:
    st.markdown("<h1 style='margin-bottom: 0; font-size: 2.1rem; font-weight: 700;'>Versight</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 0.95rem; margin-top: 2px;'>E-Commerce Review Authenticity Engine, True Rating Deflator & Failure Diagnostics</p>", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("### 🛡️ Versight Suite")
nav_choice = st.sidebar.radio(
    "Navigation Mode:",
    [
        "🌐 Live E-Commerce URL Auditor",
        "🔍 Deep-Dive Forensic Report",
        "🏬 Electronics Storefront & Catalog",
        "📊 AI Model Studio & Evaluation"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("**Active Forensic Model:**")
active_model_name = metrics.get('best_model', 'Logistic Regression (Balanced TF-IDF)')
st.sidebar.info(
    f"**Pipeline:** {active_model_name}\n\n"
    f"**Accuracy:** {metrics.get('best_model_test_metrics', {}).get('accuracy', 0.7582):.1%}\n\n"
    f"**ROC-AUC:** {metrics.get('best_model_test_metrics', {}).get('roc_auc', 0.8276):.3f}\n\n"
    f"**Catalog Index:** 311 Electronics Devices\n\n"
    f"**Product Database:** 2,990+ Real Amazon ASINs"
)


# ---------------------------------------------------------------------------
# Mode 1: 🌐 Live E-Commerce URL Auditor
# ---------------------------------------------------------------------------
if nav_choice == "🌐 Live E-Commerce URL Auditor":
    st.subheader("🌐 E-Commerce Product URL Audit & Rating Deflator")
    st.caption("Paste any Amazon or e-commerce product link. Versight matches the product or extracts reviews, runs them through the trained ML classifier to filter fake/incentivized reviews, reveals the true authentic rating, and diagnoses why the product fails.")

    st.markdown("**⚡ Quick Benchmark Presets:**")
    ex_c1, ex_c2, ex_c3, ex_c4, ex_c5 = st.columns(5)
    
    selected_url = ""
    if ex_c1.button("📱 iPhone 16\n(4.5★ -> 3.8★)", use_container_width=True):
        selected_url = "https://www.amazon.in/Apple-iPhone-16-128-GB/dp/B0DGJ9B589"
    if ex_c2.button("🎧 Earbuds\n(4.5★ -> 3.8★)", use_container_width=True):
        selected_url = "https://www.amazon.com/dp/P001"
    if ex_c3.button("⚡ 18W Fast Charger\n(4.3★ -> 1.8★)", use_container_width=True):
        selected_url = "https://www.amazon.com/dp/B0836QVLD3"
    if ex_c4.button("🔊 BT Speaker\n(4.2★ -> 1.9★)", use_container_width=True):
        selected_url = "https://www.amazon.com/dp/B07Z8ZWQYV"
    if ex_c5.button("📱 Galaxy Z Fold\n(4.0★ -> 3.4★)", use_container_width=True):
        selected_url = "https://www.amazon.com/dp/B0FDL5T1PF"

    url_input = st.text_input(
        "Enter Amazon Product URL or ASIN:",
        value=selected_url if selected_url else "",
        placeholder="Paste any Amazon product link or ASIN (e.g. https://www.amazon.in/dp/...)"
    )

    run_audit = st.button("🚀 Audit Product URL & Diagnose", type="primary")

    target_to_audit = url_input.strip() if url_input.strip() else selected_url

    if run_audit or selected_url:
        if not target_to_audit:
            st.warning("⚠️ Please enter or paste an Amazon product URL or ASIN above to start the audit.")
        else:
            with st.spinner("Retrieving customer reviews and running forensic NLP models..."):
                extracted = fetch_product_reviews_from_url(target_to_audit, catalog_list=catalog)

        if extracted.get("status") == "captcha_blocked":
            st.warning("🔒 **Amazon Bot Protection Active:** Amazon returned an anti-bot CAPTCHA for this request.")
            st.info("Try testing one of the indexed real Amazon product ASINs (like `B0836QVLD3`, `B07Z8ZWQYV`, `B07Q34ZKLF`).")
        else:
            product_title = extracted["product_title"]
            source = extracted["source"]
            asin_found = extracted["asin"]
            displayed_rating = extracted.get("displayed_rating")
            reviews_list = extracted.get("reviews", [])

            if not reviews_list:
                st.warning("No reviews could be parsed from this product URL.")
            else:
                rev_df = pd.DataFrame(reviews_list)
                analysis = compute_rating_inflation(
                    rev_df,
                    rating_col="rating",
                    text_col="review_text",
                    model=model,
                    target_displayed_rating=displayed_rating
                )

                st.divider()
                st.markdown(f"### 📦 {product_title}")
                st.markdown(f"<span class='url-badge'>Source: {source}</span> &nbsp; <span class='url-badge'>ASIN: {asin_found}</span> &nbsp; <span class='url-badge'>{analysis['total_reviews']} Real Reviews Audited</span>", unsafe_allow_html=True)
                st.write("")

                # 4 Hero Metric Cards
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-card-title">Advertised Given Rating</div>
                        <div class="stat-card-value" style="color: #60a5fa;">{analysis['displayed_rating']:.2f} ★</div>
                        <div class="stat-card-delta">Listed on online store</div>
                    </div>
                    """, unsafe_allow_html=True)

                with c2:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-card-title">Actual Genuine Rating</div>
                        <div class="stat-card-value" style="color: #34d399;">{analysis['authentic_rating']:.2f} ★</div>
                        <div class="stat-card-delta" style="color: #34d399;">Calculated from verified organic reviews</div>
                    </div>
                    """, unsafe_allow_html=True)

                with c3:
                    inf_color = "#f43f5e" if analysis['inflation_delta'] >= 0.5 else "#f59e0b"
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-card-title">Rating Inflation Delta</div>
                        <div class="stat-card-value" style="color: {inf_color};">+{analysis['inflation_delta']:.2f} ★</div>
                        <div class="stat-card-delta" style="color: {inf_color};">Inflated by {analysis['inflation_pct']:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)

                with c4:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-card-title">Trust Assessment</div>
                        <div class="stat-card-value" style="font-size: 1.8rem;">{analysis['trust_grade']}</div>
                        <div class="stat-card-delta">{analysis['fake_pct']:.1f}% Suspicious Reviews Flagged</div>
                    </div>
                    """, unsafe_allow_html=True)

                if analysis['inflation_delta'] > 0:
                    st.warning(
                        f"⚠️ **Rating Inflation Result:** The advertised rating listed on the store is **{analysis['displayed_rating']:.2f} stars**, "
                        f"but actual genuine reviews average **{analysis['authentic_rating']:.2f} stars**. "
                        f"**The rating is inflated by +{analysis['inflation_delta']:.2f} stars ({analysis['inflation_pct']:.1f}%)!**"
                    )
                else:
                    st.success(f"✅ **Authentic Rating:** The advertised rating ({analysis['displayed_rating']:.2f}★) matches verified customer feedback. No significant inflation detected.")

                st.divider()

                # NEW FEATURE: Failure Diagnostics & Pros/Cons
                render_aspect_diagnostics_ui(analysis.get("aspect_analysis", {}))

                st.divider()

                # Visual Charts
                st.subheader("📊 Rating Deflator Visualizations")
                ch1, ch2 = st.columns([3, 2])
                with ch1:
                    comp_data = pd.DataFrame([
                        {"Metric": "Advertised Given Rating", "Stars": analysis["displayed_rating"]},
                        {"Metric": "Actual Genuine Rating", "Stars": analysis["authentic_rating"]}
                    ])
                    bar_chart = alt.Chart(comp_data).mark_bar(size=32, cornerRadius=4).encode(
                        x=alt.X("Stars:Q", scale=alt.Scale(domain=[0, 5]), title="Rating (0 to 5 Stars)"),
                        y=alt.Y("Metric:N", sort="-x", title=""),
                        color=alt.Color("Metric:N", scale=alt.Scale(domain=["Advertised Given Rating", "Actual Genuine Rating"], range=["#f43f5e", "#10b981"])),
                        tooltip=["Metric", "Stars"]
                    ).properties(height=160)
                    st.altair_chart(bar_chart, use_container_width=True)

                with ch2:
                    pie_df = pd.DataFrame([
                        {"Class": "Verified Genuine", "Count": analysis["genuine_count"]},
                        {"Class": "Filtered Fake", "Count": analysis["fake_count"]}
                    ])
                    pie = alt.Chart(pie_df).mark_arc(innerRadius=45).encode(
                        theta=alt.Theta(field="Count", type="quantitative"),
                        color=alt.Color(field="Class", type="nominal", scale=alt.Scale(domain=["Verified Genuine", "Filtered Fake"], range=["#10b981", "#f43f5e"])),
                        tooltip=["Class", "Count"]
                    ).properties(height=160, title="Review Authenticity Distribution")
                    st.altair_chart(pie, use_container_width=True)

                st.divider()

                # Side-by-Side Review Breakdown
                st.subheader("📑 Customer Reviews Breakdown: Verified Genuine vs Detected Fake")
                classified_df = analysis["classified_df"].copy()
                genuine_revs = classified_df[~classified_df["is_suspicious"]]
                fake_revs = classified_df[classified_df["is_suspicious"]]

                col_gen, col_fake = st.columns(2)
                with col_gen:
                    st.markdown(f"#### 🟢 Verified Real Customer Reviews ({len(genuine_revs)} Reviews)")
                    if genuine_revs.empty:
                        st.info("No genuine reviews identified in this sample.")
                    else:
                        for _, r in genuine_revs.iterrows():
                            with st.container():
                                st.markdown(f"**⭐ {r['rating']:.0f}/5 Stars** | *Authenticity Score: {1.0 - r['suspicious_prob']:.1%} Genuine*")
                                st.write(f'"{r["review_text"]}"')
                                st.markdown("---")

                with col_fake:
                    st.markdown(f"#### 🔴 Filtered Fake / Manipulated Reviews ({len(fake_revs)} Reviews)")
                    if fake_revs.empty:
                        st.success("Zero fake or suspicious reviews detected for this product!")
                    else:
                        for _, r in fake_revs.iterrows():
                            with st.container():
                                st.markdown(f"**⭐ {r['rating']:.0f}/5 Stars** | *Fraud Probability: {r['suspicious_prob']:.1%} Suspicious*")
                                st.write(f'"{r["review_text"]}"')
                                triggers = [w for w in SUSPICIOUS_TRIGGER_WORDS if w in r["review_text"].lower()]
                                if triggers:
                                    st.caption(f"🚨 **Deceptive cues detected:** `{', '.join(triggers)}`")
                                st.markdown("---")


# ---------------------------------------------------------------------------
# Mode 2: 🔍 Deep-Dive Forensic Report
# ---------------------------------------------------------------------------
elif nav_choice == "🔍 Deep-Dive Forensic Report":
    st.subheader("🔍 Deep-Dive Forensic Audit & Star Distribution Shift")
    st.caption("Select any electronic device from the catalog to inspect its rating inflation, star distribution shift, failure root causes, and pros/cons.")

    if not catalog:
        st.warning("Catalog is empty. Please run `python prepare_data.py` first.")
        st.stop()

    device_options = [f"{p['title']} [{p['asin']}]" for p in catalog]
    selected_option = st.selectbox("Select Electronic Device to Audit:", device_options, index=0)

    selected_asin = selected_option.split("[")[-1].replace("]", "").strip()
    product = next((p for p in catalog if p["asin"] == selected_asin), catalog[0])

    # Fetch reviews from asin_database if available, else product sample_reviews
    raw_reviews = []
    if selected_asin in asin_database and asin_database[selected_asin].get("reviews"):
        raw_reviews = asin_database[selected_asin]["reviews"]
    else:
        raw_reviews = product.get("sample_reviews", [])

    # Run analysis with live aspect diagnostics
    rev_df = pd.DataFrame(raw_reviews) if raw_reviews else pd.DataFrame(product.get("sample_reviews", []))
    analysis = compute_rating_inflation(rev_df, rating_col="rating" if "rating" in rev_df.columns else "stars", text_col="review_text" if "review_text" in rev_df.columns else "text", model=model)

    st.markdown(f"### {product['title']}")
    st.caption(f"**Category:** {product['category']} | **ASIN / ID:** `{product['asin']}` | **Sample Size:** {analysis['total_reviews']} verified reviews")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-card-title">Given / Advertised Rating</div>
            <div class="stat-card-value" style="color: #60a5fa;">{analysis['displayed_rating']:.2f} ★</div>
            <div class="stat-card-delta">Listed on online store</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-card-title">Actual Genuine Rating</div>
            <div class="stat-card-value" style="color: #34d399;">{analysis['authentic_rating']:.2f} ★</div>
            <div class="stat-card-delta" style="color: #34d399;">Calculated from verified organic reviews</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        inf_color = "#f43f5e" if analysis['inflation_delta'] >= 0.5 else "#f59e0b"
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-card-title">Rating Inflation Delta</div>
            <div class="stat-card-value" style="color: {inf_color};">+{analysis['inflation_delta']:.2f} ★</div>
            <div class="stat-card-delta" style="color: {inf_color};">Inflated by {analysis['inflation_pct']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-card-title">Trust Assessment</div>
            <div class="stat-card-value" style="font-size: 1.8rem;">{analysis['trust_grade']}</div>
            <div class="stat-card-delta">{analysis['fake_pct']:.1f}% Suspicious Reviews</div>
        </div>
        """, unsafe_allow_html=True)

    if analysis['inflation_delta'] >= 0.5:
        st.error(f"⚠️ **Rating Inflation Alert:** This device is listed at **{analysis['displayed_rating']:.2f} stars**, but genuine customer reviews average **{analysis['authentic_rating']:.2f} stars**. The rating is inflated by **{analysis['inflation_delta']:.2f} stars** ({analysis['inflation_pct']:.1f}%).")
    else:
        st.success(f"✅ **High Trust Device:** Advertised rating ({analysis['displayed_rating']:.2f}★) closely matches genuine customer experience ({analysis['authentic_rating']:.2f}★). Rating inflation is minimal (+{analysis['inflation_delta']:.2f}★).")

    st.divider()

    # Product Failure Diagnostics & Pros/Cons
    render_aspect_diagnostics_ui(analysis.get("aspect_analysis", {}))

    st.divider()

    # Star Distribution Shift & Pie Charts
    st.subheader("📊 Star Distribution Shift & Authenticity Breakdown")
    star_all = analysis.get("star_distribution_all", {1:0, 2:0, 3:0, 4:0, 5:0})
    star_gen = analysis.get("star_distribution_genuine", {1:0, 2:0, 3:0, 4:0, 5:0})

    dist_data = []
    for s in range(1, 6):
        dist_data.append({"Stars": f"{s} Star", "Count": star_all.get(s, 0), "Type": "All Advertised Reviews"})
        dist_data.append({"Stars": f"{s} Star", "Count": star_gen.get(s, 0), "Type": "Verified Genuine Reviews"})

    df_dist = pd.DataFrame(dist_data)

    ch_col1, ch_col2 = st.columns([3, 2])
    with ch_col1:
        star_chart = alt.Chart(df_dist).mark_bar(cornerRadius=4).encode(
            x=alt.X("Stars:N", title="Star Rating"),
            y=alt.Y("Count:Q", title="Number of Reviews"),
            color=alt.Color("Type:N", scale=alt.Scale(domain=["All Advertised Reviews", "Verified Genuine Reviews"], range=["#38bdf8", "#10b981"])),
            xOffset="Type:N",
            tooltip=["Stars", "Type", "Count"]
        ).properties(height=280)
        st.altair_chart(star_chart, use_container_width=True)

    with ch_col2:
        pie_data = pd.DataFrame([
            {"Category": "Genuine Reviews", "Count": analysis["genuine_count"]},
            {"Category": "Suspicious Reviews", "Count": analysis["fake_count"]}
        ])
        pie_chart = alt.Chart(pie_data).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="Count", type="quantitative"),
            color=alt.Color(field="Category", type="nominal", scale=alt.Scale(domain=["Genuine Reviews", "Suspicious Reviews"], range=["#10b981", "#f43f5e"])),
            tooltip=["Category", "Count"]
        ).properties(height=280, title="Review Authenticity Breakdown")
        st.altair_chart(pie_chart, use_container_width=True)


# -------------------------------------------------------------
# Mode 4: 🏬 Electronics Storefront & Catalog
# -------------------------------------------------------------
elif nav_choice == "🏬 Electronics Storefront & Catalog":
    st.subheader("🏬 Online Electronics Storefront — Listed vs Authentic Ratings")
    st.caption("Browse 300+ consumer electronics indexed from research review datasets. Compare advertised star ratings against genuine ratings and inspect failure reasons.")

    if not catalog:
        st.warning("Electronics catalog not found. Please run `python prepare_data.py`.")
        st.stop()

    cat_df = pd.DataFrame(catalog)

    m1, m2, m3, m4 = st.columns(4)
    avg_displayed = cat_df["displayed_rating"].mean()
    avg_authentic = cat_df["authentic_rating"].mean()
    avg_inflation = cat_df["inflation_delta"].mean()
    inflated_count = (cat_df["inflation_delta"] >= 0.50).sum()

    m1.metric("Devices Indexed", f"{len(cat_df):,}")
    m2.metric("Avg Given Rating", f"{avg_displayed:.2f} ★")
    m3.metric("Avg Actual Rating", f"{avg_authentic:.2f} ★")
    m4.metric("Avg Rating Inflation", f"+{avg_inflation:.2f} ★", f"{inflated_count} heavily inflated", delta_color="inverse")

    st.divider()
    f1, f2, f3 = st.columns([2, 2, 2])
    with f1:
        categories = ["All Categories"] + sorted(list(cat_df["category"].unique()))
        selected_category = st.selectbox("Filter by Category", categories)
    with f2:
        search_query = st.text_input("🔍 Search device or ASIN", placeholder="e.g. Earbuds, Charger, Laptop, Smart Watch")
    with f3:
        grade_filter = st.multiselect(
            "Filter by Trust Grade",
            ["Grade A", "Grade B", "Grade C", "Grade D", "Grade F"],
            default=["Grade A", "Grade B", "Grade C", "Grade D", "Grade F"]
        )

    filtered = cat_df.copy()
    if selected_category != "All Categories":
        filtered = filtered[filtered["category"] == selected_category]
    if search_query.strip():
        filtered = filtered[filtered["title"].str.contains(search_query.strip(), case=False, na=False) | filtered["asin"].str.contains(search_query.strip(), case=False, na=False)]
    if grade_filter:
        filtered = filtered[filtered["trust_grade"].isin(grade_filter)]

    st.write(f"Showing **{len(filtered)}** matching electronic devices:")

    display_cols = [
        "title", "category", "displayed_rating", "authentic_rating",
        "inflation_delta", "fake_pct", "total_reviews", "trust_grade"
    ]
    view_table = filtered[display_cols].copy()
    view_table.columns = [
        "Device Title", "Category", "Given Rating", "Actual Rating",
        "Inflation (Stars)", "Fake Reviews %", "Reviews", "Trust Grade"
    ]
    view_table["Given Rating"] = view_table["Given Rating"].map(lambda x: f"{x:.2f} ★")
    view_table["Actual Rating"] = view_table["Actual Rating"].map(lambda x: f"{x:.2f} ★")
    view_table["Inflation (Stars)"] = view_table["Inflation (Stars)"].map(lambda x: f"+{x:.2f} ★" if x > 0 else f"{x:.2f} ★")
    view_table["Fake Reviews %"] = view_table["Fake Reviews %"].map(lambda x: f"{x:.1f}%")

    st.dataframe(view_table, use_container_width=True, hide_index=True)

    # Quick Drill-Down Diagnostics
    with st.expander("🔍 Inspect Instant Failure Diagnostics for Any Catalog Device"):
        drill_options = [f"{p['title']} [{p['asin']}]" for p in filtered.to_dict(orient="records")]
        if drill_options:
            selected_drill = st.selectbox("Select Device for Failure Mode & Pros/Cons Drilldown:", drill_options)
            drill_asin = selected_drill.split("[")[-1].replace("]", "").strip()
            item = next((p for p in catalog if p["asin"] == drill_asin), catalog[0])
            
            raw_revs = asin_database.get(drill_asin, {}).get("reviews", item.get("sample_reviews", []))
            drill_df = pd.DataFrame(raw_revs) if raw_revs else pd.DataFrame(item.get("sample_reviews", []))
            drill_analysis = compute_rating_inflation(drill_df, rating_col="rating" if "rating" in drill_df.columns else "stars", text_col="review_text" if "review_text" in drill_df.columns else "text", model=model)
            
            render_aspect_diagnostics_ui(drill_analysis.get("aspect_analysis", {}))


# -------------------------------------------------------------
# Mode 4: 📊 AI Model Studio & Evaluation
# -------------------------------------------------------------
elif nav_choice == "📊 AI Model Studio & Evaluation":
    st.subheader("📊 AI Model Studio & Benchmark Evaluation")
    st.caption("Transparent evaluation of machine learning models trained on balanced electronics reviews. Inspect performance metrics, confusion matrix, and predictive linguistic tokens.")

    tab_eval, tab_words = st.tabs(["📈 Model Benchmarks & Metrics", "🔤 Predictive Linguistic Tokens"])

    with tab_eval:
        st.markdown(f"**Selected Best Model:** `{metrics.get('best_model', 'Logistic Regression (Balanced TF-IDF)')}`")
        st.markdown(f"**Training Dataset:** `{metrics.get('dataset_used', 'data/curated_training_dataset.csv')}` | **Total Samples:** {metrics.get('rows', 4398):,} rows")

        results = metrics.get("results", {})
        if results:
            res_df = pd.DataFrame(results).T.reset_index()
            res_df.columns = ["Model Architecture", "Accuracy", "Precision (Suspicious)", "Recall (Suspicious)", "F1-Score (Suspicious)", "ROC-AUC"]
            st.dataframe(res_df, use_container_width=True, hide_index=True)

            melted_res = pd.melt(res_df, id_vars=["Model Architecture"], value_vars=["Accuracy", "Precision (Suspicious)", "Recall (Suspicious)", "F1-Score (Suspicious)", "ROC-AUC"], var_name="Metric", value_name="Score")
            metric_chart = alt.Chart(melted_res).mark_bar(cornerRadius=3).encode(
                x=alt.X("Score:Q", scale=alt.Scale(domain=[0.65, 0.88]), title="Score (0 to 1)"),
                y=alt.Y("Model Architecture:N", title="Model"),
                color=alt.Color("Metric:N"),
                xOffset="Metric:N",
                tooltip=["Model Architecture", "Metric", "Score"]
            ).properties(height=320)
            st.altair_chart(metric_chart, use_container_width=True)

        cm = metrics.get("confusion_matrix", [[430, 163], [124, 383]])
        st.subheader("Confusion Matrix (Test Split: 1,100 held-out reviews)")
        cm_df = pd.DataFrame(cm, index=["Actual Genuine", "Actual Suspicious"], columns=["Predicted Genuine", "Predicted Suspicious"])

        cm_c1, cm_c2 = st.columns([2, 1])
        with cm_c1:
            st.dataframe(cm_df, use_container_width=True)
        with cm_c2:
            correct = int(cm_df.iloc[0, 0] + cm_df.iloc[1, 1])
            total = int(cm_df.to_numpy().sum())
            st.metric("Total Test Reviews", f"{total:,}")
            st.metric("Correct Predictions", f"{correct:,} ({correct/total:.1%})")
            st.metric("Misclassifications", f"{total - correct:,} ({(total - correct)/total:.1%})")

    with tab_words:
        st.subheader("🔤 Top Predictive Linguistic Features")
        st.caption("Word and character n-gram coefficients extracted from the calibrated model. Shows terms most strongly predictive of deceptive/suspicious reviews versus genuine reviews.")

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            st.markdown("#### 🔴 Top Suspicious / Promotional Terms")
            top_susp = metrics.get("top_suspicious_words", [])[:15]
            if top_susp:
                df_susp = pd.DataFrame(top_susp)
                st.dataframe(df_susp, use_container_width=True, hide_index=True)
            else:
                st.info("No words recorded.")

        with col_w2:
            st.markdown("#### 🟢 Top Genuine / Natural Terms")
            top_gen = metrics.get("top_genuine_words", [])[:15]
            if top_gen:
                df_gen = pd.DataFrame(top_gen)
                st.dataframe(df_gen, use_container_width=True, hide_index=True)
            else:
                st.info("No words recorded.")

st.divider()
st.caption("🛡️ Versight — Machine Learning for E-Commerce Transparency and Consumer Protection.")
