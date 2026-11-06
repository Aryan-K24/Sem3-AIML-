# RV UNIVERSITY

School of Computer Science and Engineering

Bengaluru, Karnataka, India

# CS2227 AI AND ML

PROJECT REPORT

TrustRate AI: E-Commerce Review Authenticity Engine, True Rating Deflator & Aspect-Based Failure Diagnostics

Submitted by:

Aryan Kulkarni  (1RUA25CSE0085)

Aryan Kumar Jha  (1RUA25CSE0086)

Ashifraj Gaddi  (1RUA25CSE0088)

Ata Us Faizaan  (1RUA25CSE0094)

Bachelor of Technology in Computer Science & Engineering (Section B)

Under the guidance of:

Dr. Sarasvathi

Faculty Guide, School of Computer Science and Engineering

Academic Year: 2025–2026

# RV UNIVERSITY, BENGALURU

School of Computer Science and Engineering

# CERTIFICATE

Certified that the CS2227 AI AND ML project work titled "TrustRate AI: E-Commerce Review Authenticity Engine, True Rating Deflator & Aspect-Based Failure Diagnostics" is carried out by Aryan Kulkarni (1RUA25CSE0085), Aryan Kumar Jha (1RUA25CSE0086), Ashifraj Gaddi (1RUA25CSE0088), and Ata Us Faizaan (1RUA25CSE0094), who are bonafide students of the School of Computer Science and Engineering, RV University, Bengaluru, during the academic year 2025–26. It is certified that all corrections and suggestions from all continuous internal evaluations (CIE 1, CIE 2, and CIE 3) have been incorporated into the project and in this report.

| _____________________________ Dr. Sarasvathi Faculty Guide School of CSE, RV University | _____________________________ Program Director School of CSE RV University, Bengaluru |
| --- | --- |

# ABSTRACT

Customer purchasing decisions on modern e-commerce platforms heavily rely on aggregate star ratings and buyer reviews. However, the proliferation of incentivized, bot-generated, and promotional reviews has created severe rating inflation, distorting genuine product feedback and causing consumer dissatisfaction. Traditional moderation mechanisms rely largely on static keyword filtering or basic metadata flags, failing to capture nuanced deception tactics and failing to tell consumers why a product actually fails in real-world usage.

To address this challenge, this project introduces TrustRate AI, an end-to-end machine learning system that audits e-commerce products, detects deceptive reviews, deflates promotional ratings to their authentic scores, and diagnoses failure modes. The system employs a dual-channel Sublinear Term Frequency-Inverse Document Frequency (TF-IDF) feature union combining word n-grams (1-2) and character n-grams (3-5) with a total vocabulary of 60,000 features. Several supervised classification architectures — including Balanced Logistic Regression, Calibrated Linear Support Vector Classifiers (LinearSVC), Multinomial Naive Bayes, Complement Naive Bayes, and Calibrated Stochastic Gradient Descent (SGD) — were systematically trained, validated, and benchmarked on 4,398 curated electronics reviews. The primary Balanced Logistic Regression pipeline achieved a classification accuracy of 75.82%, a Receiver Operating Characteristic Area Under Curve (ROC-AUC) of 0.828, and a precision of 72.90% on held-out test reviews.

The system incorporates an automated rating deflator engine that strips out predicted fake reviews, revealing the genuine rating delta. Furthermore, an aspect-based diagnostic engine analyzes reviews across six hardware dimensions (Battery, Build Durability, Wireless, Audio, Handling Ergonomics, and Software Stability) to extract plain-English product failure modes and verified, non-overlapping Pros and Cons. The complete architecture is deployed via an interactive Streamlit dashboard allowing users to paste live Amazon product links, yielding immediate transparency and actionable consumer protection.

Keywords: Machine Learning, Deceptive Review Detection, TF-IDF, Logistic Regression, Rating Inflation, Aspect-Based Sentiment Analysis, E-Commerce Forensics.

## 1. Introduction

In the contemporary digital economy, online retail platforms such as Amazon, Flipkart, and Newegg have established consumer reviews and numerical star ratings as the definitive currency of consumer trust. According to recent market studies, over 88% of consumers consult customer reviews before committing to an electronics purchase, with higher star ratings correlating directly with elevated sales volumes. Consequently, predatory third-party vendors and incentivized syndicates have developed sophisticated mechanisms to artificially inflate product ratings. These operations recruit participants through external channels to generate large batches of fabricated five-star reviews in exchange for free products, direct refunds, or cash rewards.

This phenomenon, commonly characterized as rating inflation, produces significant market distortions. Products with severe underlying hardware vulnerabilities — such as rapid battery degradation, overheating charging circuits, or unstable wireless firmware — frequently boast advertised ratings exceeding 4.4 out of 5 stars. Unsuspecting buyers, relying on the prominent aggregate score, make purchasing decisions only to experience hardware failures within weeks of delivery. Furthermore, authentic customer complaints detailing technical failure modes are effectively buried beneath hundreds of generic, uninformative five-star praises ('Best product ever!', 'Works perfectly, five stars!').

Existing commercial countermeasures remain inadequate. Platform-level moderation systems rely heavily on post-purchase account flags or proprietary filtering algorithms that are entirely opaque to consumers. When platform algorithms remove a subset of fraudulent reviews, the advertised aggregate rating often fails to adjust proportionally, preserving the distorted commercial baseline. There is a pressing need for an explainable, consumer-facing audit solution that can parse product reviews in real time, distinguish genuine user feedback from deceptive spam, re-compute an honest star rating, and articulate the specific technical reasons why a product is prone to failure.

## 2. Problem Statement

E-commerce platforms exhibit severe consumer trust degradation due to pervasive rating inflation and deceptive review campaigns. Current e-commerce interfaces exhibit three primary systemic deficiencies:

## 1. Obfuscated Authenticity: Advertised aggregate star ratings fail to delineate between organic consumer experiences and paid promotional fabrications, frequently inflating 3.0-star hardware into apparent 4.5-star products.

## 2. Absence of Real-Time Deflation: Consumers lack an independent, automated tool capable of ingesting an arbitrary product URL, isolating suspicious reviews using rigorous machine learning classifiers, and displaying the mathematical 'deflated' rating delta.

## 3. Inaccessible Failure Analysis: Even when legitimate critical reviews exist, consumers cannot easily parse hundreds of comments to discern recurrent engineering defects (e.g., distinguishing between minor cosmetic flaws and critical thermal runaway risks).

Therefore, the objective of this project is to design, implement, and experimentally validate an intelligent Natural Language Processing (NLP) system, 'TrustRate AI', that accepts e-commerce product links or review corpora, applies supervised machine learning to classify review veracity, re-computes the genuine organic star rating, and automatically diagnoses root failure causes with deduplicated, authentic Pros and Cons.

## 3. Objectives

The primary engineering and analytical objectives of the TrustRate AI project are defined as follows:

3.1 Curate and preprocess a balanced, deduplicated dataset of real-world e-commerce customer reviews, mitigating reviewer-level data leakage.

3.2 Engineer a high-dimensional feature representation utilizing a hybrid FeatureUnion of sublinear word n-grams (1-2) and character n-grams (3-5).

3.3 Train, benchmark, and cross-validate multiple supervised classification architectures (Logistic Regression, LinearSVC, Naive Bayes, SGD) and select the optimal forensic pipeline.

3.4 Mathematically formulate and implement an automated Rating Deflator Engine that calculates authentic star ratings and inflation deltas from live Amazon product links.

3.5 Develop a domain-specific Aspect-Based Sentiment and Diagnostic Engine mapping customer feedback across six hardware dimensions to detect recurring root-cause failure modes.

3.6 Deploy a modular, production-grade Streamlit web interface delivering explainable forensic scorecards, model evaluation benchmarks, and live URL inspection.

## 4. Scope of the Project

The operational scope of TrustRate AI is defined within realistic academic and engineering boundaries:

• Target Domain: Consumer electronics, encompassing smartphones, wireless earbuds, laptops, fast-charging accessories, smartwatches, and Bluetooth speakers, comprising an indexed database of 311 cataloged devices and over 2,990 Amazon product ASINs.

• Algorithmic Scope: Supervised classification of linguistic and stylistic patterns. The model operates directly on raw review text, evaluating lexical choices, syntactic density, character punctuation, and sentiment extremity.

• Live URL Audit: Extraction of real-time product titles and advertised star ratings from live Amazon product pages using optimized mobile headers to bypass bot-detection CAPTCHAs.

• Diagnostic Scope: Granular aspect classification across six predefined hardware dimensions, extracting verified praise snippets and critical failure causes.

Assumptions and Limitations: The system assumes the English language for review parsing. Verification is probabilistic based on historical research labels and campaign tracking rather than forensic judicial verification of reviewer identities. The system functions as an explainable consumer decision-support mechanism.

## 5. Literature Review

A systematic survey of prior research in opinion spam detection, rating distortion, and aspect-based sentiment analysis was conducted to establish foundational insights and identify research gaps. Table 5.1 summarizes the key benchmark studies in this domain:

| Sl.No. | Conference / Journal | Authors & Year | Inference & Key Contribution | Identified Research Gap |
| --- | --- | --- | --- | --- |
| 1 | ACM SIGKDD Int. Conf. on Knowledge Discovery and Data Mining | J. Jindal & B. Liu (2008) | Foundational formulation of review spam detection; proved that duplicate and promotional reviews follow identifiable linguistic and behavioral anomalies. | Focused primarily on duplicate detection; lacked aspect-level failure extraction and real-time rating deflation. |
| 2 | IEEE Transactions on Knowledge and Data Engineering (TKDE) | G. Wang et al. (2012) | Analyzed online review manipulation in commercial marketplaces; revealed that deceptive reviews exhibit extreme rating deviations from product true baselines. | Relied heavily on user graph metadata, which is inaccessible to consumer-facing real-time web applications. |
| 3 | Assoc. for Computational Linguistics (ACL) | M. Ott et al. (2011) | Demonstrated that automated text classification using n-grams and psychological deception cues outperforms human judges in detecting fabricated reviews. | Evaluated synthetic crowdsourced reviews in hotel domains rather than real-world e-commerce electronics corpora. |
| 4 | Expert Systems with Applications (Elsevier) | S. Rayana & L. Akoglu (2015) | Developed collective classification framework combining behavioral metadata with text to score review honesty and compute ranking adjustments. | High computational complexity; does not provide plain-English product breakdown diagnostics for shoppers. |
| 5 | Association for Computational Linguistics (ACL) | J. Li, M. Ott, C. Cardie & E. Hovy (2014) | Examined whether deceptive opinion spam can be identified using generalizable linguistic patterns across domains. | Focused on deceptive text classification; does not provide live product-rating deflation or hardware aspect diagnostics. |
| 6 | ACM International Conference on World Wide Web (WWW) | A. Mukherjee, B. Liu & N. Glance (2012) | Modeled deceptive reviewer groups in commercial forums; proved collective collusion patterns across temporal audit windows. | Focused on user group graph clustering; did not develop text-based rating deflation or hardware aspect diagnostics. |

*Table 5.1: Comparative Literature Review Summary*

## 6. Proposed Methodology

The proposed TrustRate AI architecture adopts a modular four-tier methodology: Ingestion, Representation, Classification, and Diagnostic Synthesis. The four interconnected tiers operate as follows:

## 1. Ingestion & Preprocessing Tier: Raw review data is ingested either via catalog indices or live Amazon HTTP extraction. Data undergoes string normalization, reviewer-level deduplication to eliminate user-specific leakage, and length verification.

## 2. Feature Engineering Tier: Text is transformed through a dual FeatureUnion comprising word n-grams (1-2) with sublinear scaling and character n-grams (3-5). This dual representation captures both semantic fraud keywords ('miracle', 'five stars') and stylistic irregularities (excessive capitalization, punctuation clusters).

## 3. Classification & Optimization Tier: High-dimensional vectors are evaluated by supervised linear classifiers. The model computes posterior probabilities using the Sigmoid function and is optimized using Binary Cross-Entropy loss via Gradient Descent.

## 4. Deflation & Aspect Diagnostic Tier: Reviews flagged as suspicious are stripped from the sample. The authentic star rating is re-computed. Remaining reviews are parsed by the Aspect Analyzer across six hardware dimensions to detect failure patterns and formulate non-overlapping Pros and Cons.

## 7. Dataset Description

The training and evaluation of TrustRate AI utilizes a rigorously curated e-commerce dataset derived from real-world online consumer reviews in the consumer electronics domain.

• Source: Large-scale public e-commerce review corpus combined with ground-truth moderation tracking.

• Total Curated Dataset Size: 4,398 verified review instances.

• Training Split: 3,298 instances (75.0% stratified split).

• Testing Split: 1,100 held-out instances (25.0% stratified split).

• Class Balance: Exactly balanced distribution (50.0% genuine organic reviews, 50.0% deceptive/suspicious reviews) to eliminate majority-class accuracy bias.

• Target Variable: Binary classification label — 'genuine' (0) versus 'suspicious' (1).

The formal schema and attribute definitions of the curated dataset are presented in Table 7.1:

| Attribute Name | Data Type | Description | Role in Machine Learning |
| --- | --- | --- | --- |
| review_id | String / UUID | Unique identifier for each review submission | Tracking & audit identification |
| reviewer_id | String / Hash | Unique identifier of the submitting customer account | Used for reviewer-level deduplication |
| product_title | String | Full commercial product title of the electronic device | Aspect mapping & device categorization |
| category | Categorical | Electronics classification (Earbuds, Laptops, Phones, etc.) | Stratified benchmarking & catalog indexing |
| review_rating | Numeric (1.0 - 5.0) | Numerical star rating assigned by reviewer | Rating deflator baseline calculation |
| review_text | String (Text) | Complete written narrative text of the customer review | Primary input feature for NLP vectorizer |
| label | Categorical / Binary | Supervised truth label ('genuine' vs 'suspicious') | Ground-truth target variable (y) |

*Table 7.1: Curated Training Dataset Schema & Attribute Specifications*

## 8. Data Preprocessing

Text data in customer reviews is notoriously noisy, containing colloquialisms, typos, excessive punctuation, and formatting irregularities. The data preprocessing pipeline implements systematic cleaning stages:

## 1. Missing Value Imputation & Null Elimination: Records with missing review narratives or invalid star ratings outside [1.0, 5.0] were purged. Missing product titles were assigned standard categorical fallbacks.

## 2. Reviewer-Level Deduplication (Data Leakage Prevention): In typical review datasets, aggressive promotional reviewers submit dozens of reviews across multiple products. If reviews from the same reviewer appear in both training and test sets, the model risks memorizing idiosyncratic reviewer phrasing rather than general deception signals. We enforced strict reviewer-level deduplication, retaining exactly one review per reviewer_id before train-test splitting.

## 3. String Trimming & Length Thresholding: Very short comments (< 12 characters, e.g., 'good', 'ok') lack sufficient semantic context for stylometric analysis and were filtered out.

## 4. Feature Normalization & Sublinear Scaling: Rather than raw term counts, Sublinear Term Frequency (1 + ln(count)) was applied to dampen extreme term frequencies.

## 5. Dual FeatureUnion Pipeline: A scikit-learn FeatureUnion combined word-level n-grams (1-2 words, max 35,000 features, min_df=2) with character-level n-grams (3-5 characters, max 25,000 features, min_df=3). Character n-grams effectively capture sub-word stylistic patterns, such as repeated punctuation (e.g., '!!!') and capitalization anomalies, without requiring manual regex extraction.

## 9. Exploratory Data Analysis (EDA)

Exploratory Data Analysis was performed on the curated corpus to uncover distinctive behavioral, statistical, and linguistic properties separating deceptive reviews from genuine ones:

## 1. Star Rating Distribution Discrepancy: Analysis revealed a stark bimodal rating distortion. Deceptive reviews exhibit an overwhelming 89.2% concentration at exactly 5.0 stars, with minimal representation at 2.0 or 3.0 stars. Conversely, verified genuine reviews display a natural bell-shaped distribution with significant density across 3.0-star and 4.0-star ratings, reflecting authentic consumer trade-offs.

## 2. Review Length & Verbosity Analysis: Contrary to popular assumptions that fake reviews are always short, incentivized syndicates frequently generate medium-length paragraphs (50-80 words). However, authentic critical reviews exhibit significantly higher word counts when detailing hardware breakdowns (averaging 118 words), detailing usage timelines ('after 3 weeks of daily use', 'stopped working after the update').

## 3. Sentiment Polarity & Exclamation Density: Deceptive reviews exhibit extreme positive sentiment polarity (VADER compound scores > 0.90) coupled with high exclamation mark density (exceeding 2.8 exclamations per review). Genuine reviews maintain moderate compound scores (0.35 - 0.70) with descriptive clauses rather than hyperbole.

The most discriminative linguistic markers identified via exploratory feature weighting are presented in Table 9.1:

| Top Suspicious / Promotional Tokens | Learned Weight (+) | Top Genuine / Natural Tokens | Learned Weight (-) |
| --- | --- | --- | --- |
| "perfect" | +3.075 | "not" | -3.976 |
| "easy to" | +2.019 | "only" | -2.047 |
| "fast" | +2.124 | "but" | -1.937 |
| "these" | +2.006 | "however" | -1.708 |
| "nice" | +1.956 | "broke" | -1.676 |
| "well" | +1.951 | "months" | -1.617 |
| "really" | +1.929 | "not work" | -1.584 |
| "super" | +1.669 | "worked" | -1.537 |
| "expectations" | +1.647 | "disappointed" | -1.524 |
| "is good" | +1.549 | "stopped" | -1.498 |

*Table 9.1: Top Predictive Lexical Tokens Identified via Exploratory Feature Analysis*

## 10. Model Development

The model development methodology followed a rigorous experimental design comparing five diverse classifier families across identical stratified splits.

### 10.1 Model Selection Rationale

• Logistic Regression (Balanced TF-IDF): Selected as the primary operational model due to its high computational efficiency, probabilistic calibration via Sigmoid, and clear mathematical interpretability of feature coefficients.

• Linear Support Vector Classifier (LinearSVC): Evaluated with Platt calibration (CalibratedClassifierCV) to assess maximum-margin separation on high-dimensional sparse text.

• Multinomial & Complement Naive Bayes: Evaluated as baseline probabilistic generative benchmarks known for fast execution on word frequency counts.

• Stochastic Gradient Descent (SGDClassifier): Evaluated with modified Huber loss to assess incremental online learning performance.

### 10.2 Training Methodology & Hyperparameter Tuning

• Inverse Regularization Strength (C): Tuned over grid values [0.1, 0.5, 1.0, 2.5, 5.0]. The optimal setting for Logistic Regression was established at C = 2.5 using the liblinear solver.

• Class Weight Balancing: Given real-world fluctuations in fraud incidence, class_weight='balanced' was enforced, automatically adjusting weights inversely proportional to class frequencies.

• Cross-Validation Strategy: A 3-fold cross-validation scheme was employed during calibration and tuning, followed by testing on a pristine held-out test split of 1,100 instances.

## 11. Implementation Details

The technical architecture of TrustRate AI is structured across modular Python components:

• Programming Language: Python 3.10+

• Core Libraries: Scikit-Learn (v1.2+), Pandas (v2.0+), NumPy (v1.24+), Altair (v5.0+), Requests, Joblib, Streamlit (v1.30+).

• Development Environment: Visual Studio Code, Git, Windows 11 64-bit.

• Codebase Architecture:

## 1. train_model.py: Ingestion, FeatureUnion creation, model benchmarking, and artifact serialization (model.joblib, metrics.json).

## 2. model_utils.py: Rating deflator calculations, star redistribution algorithms, and inference pipelines.

## 3. scraper.py: Mobile-header Amazon HTML parser extracting live product titles, ratings, and review counts.

## 4. aspect_analyzer.py: Aspect-based sentiment engine mapping feedback across six hardware dimensions to output plain-English defect causes.

## 5. app.py: High-performance Streamlit graphical user interface featuring Live URL Auditing, Forensic Reports, Catalog browsing, and Model Studio.

## 12. Results and Performance Evaluation

Experimental benchmarking was conducted on the held-out test split of 1,100 customer reviews. The comparative performance metrics across all five evaluated model architectures are summarized in Table 12.1:

| Model Architecture | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
| --- | --- | --- | --- | --- | --- |
| Calibrated LinearSVC | 76.55% | 75.73% | 72.13% | 73.89% | 0.8267 |
| Logistic Regression (Balanced TF-IDF) | 75.82% | 72.90% | 75.49% | 74.17% | 0.8276 |
| Multinomial Naive Bayes | 75.09% | 71.89% | 75.30% | 73.55% | 0.8207 |
| Complement Naive Bayes | 74.82% | 71.48% | 75.30% | 73.34% | 0.8198 |
| Calibrated SGD (Modified Huber) | 74.45% | 72.64% | 71.34% | 71.98% | 0.7940 |

*Table 12.1: Experimental Performance Benchmark Across Candidate Classifier Architectures*

### Confusion Matrix Analysis (Held-out Test Split: 1,100 Reviews)

For the deployed Balanced Logistic Regression model, the confusion matrix is structured as follows:

• True Negatives (Actual Genuine classified as Genuine): 452 reviews (41.1% of test set)

• False Positives (Actual Genuine classified as Suspicious): 142 reviews (12.9% of test set)

• False Negatives (Actual Suspicious classified as Genuine): 124 reviews (11.3% of test set)

• True Positives (Actual Suspicious classified as Suspicious): 382 reviews (34.7% of test set)

Total Correct Classifications: 834 / 1,100 (75.82% overall accuracy). The model maintains a balanced performance profile with high recall (75.49%), ensuring that over three-quarters of all fraudulent promotional reviews are successfully intercepted.

## 13. Discussion

The experimental results provide compelling confirmation of our architectural choices. Calibrated LinearSVC and Balanced Logistic Regression consistently outperformed Naive Bayes architectures by 1.5% to 2.0% in accuracy and over 0.03 in ROC-AUC. This is attributed to the presence of feature dependencies in natural text; while Naive Bayes assumes conditional independence between features, Logistic Regression and SVM effectively learn correlated weight combinations across character and word n-grams.

A critical observation is the behavior of the Rating Deflator in live evaluations. In real-world audits of electronics products (such as fast-charging adapters and wireless earbuds), advertised ratings of 4.30★ to 4.50★ were successfully deflated to genuine baselines of 3.40★ to 3.80★, revealing an average inflation delta of +0.70★ to +0.90★ (+18% to +26% inflation). The aspect diagnostic engine successfully identified recurring battery heating complaints and firmware stutter, providing consumers with immediate, transparent risk assessments that raw star ratings completely obscured.

## 14. Conclusion

This project successfully developed and deployed TrustRate AI, an automated e-commerce review authenticity engine and rating deflator. By synthesizing dual-channel TF-IDF feature representations with balanced supervised classifiers, the system achieved a robust 75.82% accuracy and 0.828 ROC-AUC on real-world electronics customer reviews. The project bridges the critical gap between machine learning classification and practical consumer utility by transforming abstract probability scores into actionable rating deflation deltas and root-cause hardware diagnostics. The resulting application represents a significant practical contribution toward restoring digital transparency and consumer empowerment in online retail.

## 15. Future Scope

Future iterations of TrustRate AI can expand along several promising technical dimensions:

## 1. Transformer-Based Deep Ensembles: Fine-tuning domain-specific transformer architectures (such as RoBERTa or DeBERTa) to capture contextual semantics in complex sentences.

## 2. Multilingual Opinion Auditing: Extending text parsing capabilities to regional languages (e.g., Hindi, Kannada, Spanish) to protect international consumer bases.

## 3. Cross-Platform Browser Extension: Packaging the inference pipeline into a lightweight Chrome/Firefox browser extension that overlays deflated ratings directly onto Amazon and Flipkart product pages.

## 4. Temporal Review Influx Tracking: Incorporating time-series tracking to detect coordinated brigading campaigns where hundreds of reviews appear within a 24-hour window.

## 16. References

[1] N. Jindal and B. Liu, "Opinion spam and analysis," in Proc. 2008 Int. Conf. on Web Search and Data Mining (WSDM), 2008, pp. 219–230.

[2] M. Ott, Y. Choi, C. Cardie, and J. T. Hancock, "Finding deceptive opinion spam by any stretch of the imagination," in Proc. 49th Annu. Meeting of the Assoc. for Computational Linguistics (ACL), 2011, pp. 309–319.

[3] G. Wang, S. Xie, B. Liu, and P. S. Yu, "Identify online store review spammers via social review graph," ACM Trans. Intell. Syst. Technol., vol. 3, no. 4, pp. 61:1–61:21, 2012.

[4] S. Rayana and L. Akoglu, "Collective opinion spam detection: Bridging review, individual and product level approaches," in Proc. 21st ACM SIGKDD Int. Conf. on Knowledge Discovery and Data Mining, 2015, pp. 985–994.

[5] J. Li, M. Ott, C. Cardie, and E. Hovy, "Towards a general rule for identifying deceptive opinion spam," in Proc. 52nd Annual Meeting of the Association for Computational Linguistics (ACL), 2014, pp. 1566–1576.

[6] F. Pedregosa et al., "Scikit-learn: Machine learning in Python," Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.

[7] A. Géron, Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow, 3rd ed. Sebastopol, CA, USA: O'Reilly Media, 2022.

[8] C. M. Bishop, Pattern Recognition and Machine Learning. New York, NY, USA: Springer, 2006.

[9] A. Mukherjee, B. Liu, and N. Glance, "Spotting fake reviewer groups in consumer reviews," in Proc. 21st Int. Conf. on World Wide Web (WWW), 2012, pp. 191–200.

## 17. Appendix

### 17.1 Mathematical Optimization Appendix (Calculus Integration)

The model optimization uses regularized Binary Cross-Entropy (BCE) loss:

J(w, b) = −(1/m) Σ [y(i) ln(h(i)) + (1 − y(i)) ln(1 − h(i))] + (λ / 2m) ‖w‖₂²

Applying the multivariate chain rule across the sigmoid activation h = σ(z):

∂J / ∂wj = (∂J / ∂h) · (∂h / ∂z) · (∂z / ∂wj) = [(h − y) / (h(1 − h))] · [h(1 − h)] · xj = (h − y)xj

Yielding the exact vectorized Gradient Descent update parameter rule:

w(t+1) := w(t) − α · [ (1/m) Xᵀ (σ(Xw + b) − y) + (λ/m) w ]

### 17.2 Core Model Pipeline Code Snippet

    # Python 3 — FeatureUnion & Classifier Pipeline Definition
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline, FeatureUnion
    word_char_union = FeatureUnion([
    ('word_tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=35000, min_df=2, sublinear_tf=True)),
    ('char_tfidf', TfidfVectorizer(ngram_range=(3, 5), analyzer='char', max_features=25000, min_df=3, sublinear_tf=True))
    ])
    pipeline = Pipeline([
    ('features', word_char_union),
    ('classifier', LogisticRegression(C=2.5, max_iter=2000, solver='liblinear', class_weight='balanced', random_state=42))
    ])
    pipeline.fit(X_train, y_train)
## 18. AI Tool Usage Report (Mandatory)

In accordance with institutional requirements, the following disclosure documents the utilization of AI tools during project development:

## 1. Name of AI Tools Used: Google Gemini, Antigravity Assistant, and GitHub Copilot.

## 2. Purpose of Usage: Assisted in syntax debugging for Altair interactive chart formatting, refining regular expression patterns for mobile Amazon header extraction, and structuring mathematical equation rendering for documentation.

## 3. Sample Prompts Used:

• 'How to construct a scikit-learn FeatureUnion combining sublinear word n-grams and character n-grams without memory overflow?'

• 'Write a regex pattern to extract advertised star ratings from raw Amazon product HTML containing decimal values.'

## 4. Generated Outputs: Code templates for FeatureUnion pipelines and regex pattern suggestions.

## 5. Modifications Made by Students: All generated code templates were heavily customized, integrated into the multi-tier system architecture, calibrated against the curated electronics corpus, and experimentally validated through custom benchmark suites.

## 6. Student Contribution: Students designed the end-to-end system architecture, curated and deduplicated the training dataset, formulated the Rating Deflator equation, implemented the aspect failure diagnostic logic, conducted model training and cross-validation, and authored this comprehensive technical report.
