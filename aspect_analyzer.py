"""
aspect_analyzer.py
Versight — Product Failure Root Cause & Aspect-Based Pros/Cons Diagnostic Engine

Extracts:
1. Why a certain product fails (Root Cause Diagnostics, engineering failure modes, incidence rate, severity)
2. Direct customer evidence quote snippets supporting each failure mode (clause-level targeted extraction)
3. Authentic Pros (genuine verified praise only) vs Authentic Cons (real customer limitations & compromises)
4. Comprehensive Aspect Scorecard across hardware dimensions: Battery, Build Quality, Connectivity, Audio, Ergonomics
"""

import re
from typing import List, Dict, Any, Optional
import pandas as pd


# ---------------------------------------------------------------------------
# Aspect & Failure Taxonomy with Customer-Friendly Explanations
# ---------------------------------------------------------------------------

ASPECT_DEFINITIONS = {
    "battery": {
        "title": "Battery, Power & Charging",
        "icon": "🔋",
        "keywords": [
            "battery", "charge", "charges", "charging", "charger", "overheat", "overheats", "overheating",
            "hot", "warm", "drain", "draining", "drains", "cord", "cable", "plug",
            "adapter", "power", "mah", "usb-c", "lightning", "pins", "pin", "watt", "watts",
            "standby", "recharge", "runtime", "coil whine", "electric", "short circuit"
        ],
        "failure_patterns": [
            r"\b(stopped|wont|won't|doesn't|failed to|not)\s+(charge|charging|hold a charge)\b",
            r"\b(battery|power)\s+(drains|drain|died|dies|dead|terrible|awful|horrible|poor|bad|short)\b",
            r"\b(overheat|overheats|overheating|gets\s+(very|super|dangerously|noticeably)\s+(hot|warm))\b",
            r"\b(short|less than)\s+(\d+\s*(hours?|hrs?|mins?))\s+battery\b",
            r"\b(pins?|cable|plug|wire)\s+(bent|melted|loose|burned|snapped|frayed|tore)\b",
            r"\b(swollen|swelled|spark|smoke|fire\s+hazard|humming noise)\b",
            r"\b(stopped working after|died after)\s+(\d+\s*(days?|weeks?|months?))\b"
        ],
        "positive_patterns": [
            r"\b(battery|charge)\s+(lasts|lasting|life\s+is)\s+(great|amazing|long|forever|all day|hours)\b",
            r"\b(fast|quick|rapid)\s+(charging|charge)\b",
            r"\b(good|excellent|solid|impressive)\s+battery\s+life\b"
        ],
        "customer_plain_cause": "The device tends to heat up uncomfortably during charging or high use, and the battery depletes faster than expected.",
        "con_title": "Battery Drain & Charging Heat"
    },
    "build": {
        "title": "Hardware Build & Durability",
        "icon": "🛠️",
        "keywords": [
            "broke", "broken", "crack", "cracked", "cracking", "fragile", "flimsy",
            "plastic", "snap", "snapped", "fell apart", "fall apart",
            "hinge", "crease", "durability", "durable", "casing", "screws",
            "scratches", "scratched", "sturdy", "build quality", "finish", "tore", "bubbling", "protector"
        ],
        "failure_patterns": [
            r"\b(broke|cracked|snapped|fell apart|shattered|tore|bubbling)\s+(after|within|in|along)\s+(\d+\s*(days?|weeks?|months?|uses?)|the crease)\b",
            r"\b(cheap|flimsy|fragile|poor)\s+(plastic|material|build|construction|quality|casing|wire)\b",
            r"\b(hinge|joint|clip|bracket|latch|crease)\s+(broke|snapped|loose|wobbly|cracked|noticeable|crease)\b",
            r"\b(scratches?|dents?)\s+(very\s+easily|immediately|out of the box)\b",
            r"\b(pins? bent|casing cracked|wire tore|protector started bubbling)\b"
        ],
        "positive_patterns": [
            r"\b(solid|premium|sturdy|durable|well-built|well built|robust)\s+(build|feel|material|construction)\b",
            r"\b(metal|aluminum)\s+(casing|frame|finish)\b",
            r"\b(survived|dropped\s+and\s+still\s+works)\b"
        ],
        "customer_plain_cause": "Materials or moving parts (like hinges or screen protectors) show wear, cracking, or creaking with daily handling.",
        "con_title": "Build Durability & Material Wear"
    },
    "connectivity": {
        "title": "Wireless Connectivity & Bluetooth",
        "icon": "📶",
        "keywords": [
            "bluetooth", "wireless", "disconnect", "disconnects",
            "disconnected", "disconnecting", "pair", "pairing", "paired",
            "sync", "syncing", "latency", "delay", "lag", "lagging",
            "cut out", "cutting out", "interference", "desync", "reconnect"
        ],
        "failure_patterns": [
            r"\b(keeps?|constantly|frequently|randomly)\s+(disconnecting|dropping|cutting out)\b",
            r"\b(won't|wont|unable to|fails to|refuses to)\s+(pair|connect|reconnect)\b",
            r"\b(terrible|horrible|poor|weak|short)\s+(range|signal|bluetooth)\b",
            r"\b(audio|sound)\s+(delay|lag|latency|out of sync)\b",
            r"\b(left|right)\s+(earbud|speaker|side)\s+(disconnects|loses connection|unpaired)\b"
        ],
        "positive_patterns": [
            r"\b(instant|fast|quick|seamless|easy)\s+(pairing|connection|to pair|setup)\b",
            r"\b(stable|reliable|strong|flawless)\s+(connection|bluetooth|range)\b",
            r"\b(zero|no)\s+(lag|latency|delay)\b"
        ],
        "customer_plain_cause": "Frequent Bluetooth dropouts, pairing delays, or limited wireless range.",
        "con_title": "Wireless & Bluetooth Disconnections"
    },
    "audio": {
        "title": "Audio, Acoustic & Mic Performance",
        "icon": "🔊",
        "keywords": [
            "sound", "audio", "bass", "treble", "mids", "mic", "microphone",
            "static", "buzzing", "hiss", "hissing",
            "tinny", "muffled", "distort", "distortion", "distorted", "echo",
            "acoustic", "speaker", "driver", "call quality", "earbuds"
        ],
        "failure_patterns": [
            r"\b(static|buzzing|hissing|crackling)\s+(noise|sound|in background)\b",
            r"\b(muffled|tinny|flat|hollow|muddy|harsh)\s+(sound|audio|bass|treble|voice)\b",
            r"\b(terrible|horrible|poor|bad|awful)\s+(microphone|mic|call quality|sound quality)\b",
            r"\b(one|left|right)\s+(side|ear|driver|channel)\s+(stopped|died|silent|dead|quieter)\b",
            r"\b(max|maximum)\s+volume\s+is\s+(too\s+low|quiet|inaudible)\b",
            r"\b(distorts?|distortion)\s+at\s+(high|medium)\s+volume\b"
        ],
        "positive_patterns": [
            r"\b(crisp|clear|balanced|rich|immersive|punchy|deep)\s+(sound|audio|bass|treble|highs)\b",
            r"\b(great|excellent|superb|fantastic)\s+(sound|audio|acoustic)\s+quality\b",
            r"\b(clear|clean)\s+(microphone|mic|call quality)\b"
        ],
        "customer_plain_cause": "Sound quality becomes muffled or distorted at louder volumes, and microphone picks up too much background noise.",
        "con_title": "Audio Quality & Microphone Clarity"
    },
    "ergonomics": {
        "title": "Size, Weight & Handling Comfort",
        "icon": "⚖️",
        "keywords": [
            "comfort", "comfortable", "uncomfortable", "fit", "fits", "fitting",
            "pain", "hurts", "hurting", "sore", "soreness", "ear tips", "tips",
            "tight", "loose", "bulky", "pocket", "narrow", "outer screen",
            "slips", "slipping", "falls out", "falling out", "cushion", "cushions", "padding",
            "weight", "too heavy", "quite heavy", "device is heavy", "grip", "handling"
        ],
        "failure_patterns": [
            r"\b(hurts?|painful|sore|aches?)\s+(my\s+ears?|head|hands?|fingers?)\b",
            r"\b(uncomfortable|awkward|terrible)\s+(to wear|fit|hold|use|type)\b",
            r"\b(keeps?|constantly)\s+(falling|slipping|dropping)\s+out\b",
            r"\b(too\s+(tight|heavy|bulky|large|narrow|small|loose))\b",
            r"\b(heavy in the pocket|narrow for typing|quite heavy|device is heavy)\b",
            r"\b(ear\s*tips?|cushions?)\s+(fall off|irritate|scratchy|stiff)\b"
        ],
        "positive_patterns": [
            r"\b(very|super|extremely)\s+comfortable\b",
            r"\b(comfortable|great|perfect|snug|secure)\s+(fit|grip|in hand)\b",
            r"\b(lightweight|light\s+weight|hardly\s+notice|forget\s+wearing|easy to hold)\b"
        ],
        "customer_plain_cause": "Can feel bulky, heavy in the pocket, or tiring to hold and use for extended periods.",
        "con_title": "Size, Weight & Handling Discomfort"
    },
    "software": {
        "title": "Software, Controls & Stability",
        "icon": "📱",
        "keywords": [
            "app", "software", "controls", "touch", "button", "buttons",
            "firmware", "update", "updates", "compatible", "compatibility",
            "ios", "android", "windows", "mac", "driver", "drivers",
            "glitch", "bug", "crash", "crashes", "freezing", "lag"
        ],
        "failure_patterns": [
            r"\b(app|software|update)\s+(crashes|glitches|useless|terrible|broken|doesn't work|caused occasional freezing)\b",
            r"\b(touch\s+controls?|buttons?)\s+(unresponsive|too sensitive|accidental|don't work)\b",
            r"\b(firmware\s+update)\s+(bricked|broke|ruined)\b",
            r"\b(freezing|frozen|laggy|stutter)\b"
        ],
        "positive_patterns": [
            r"\b(intuitive|responsive|easy|smooth)\s+(controls|app|buttons|setup|ui)\b",
            r"\b(app\s+has\s+(great|useful|good)\s+features|ai\s+features|multitasking)\b"
        ],
        "customer_plain_cause": "Occasional software lag, freezing after updates, or finicky touch/button controls.",
        "con_title": "Software Glitches & Response Lag"
    }
}


NEGATIVE_CUE_WORDS = {
    "broke", "broken", "crease", "bubbling", "warm", "hot", "heat", "overheat",
    "overheating", "slow", "heavy in the pocket", "quite heavy", "drain", "drains", "draining",
    "lag", "laggy", "glitch", "stutter", "crashes", "freezing", "disconnect", "disconnects",
    "dropping", "narrow", "flimsy", "cheap", "loose", "bent", "distortion", "distort",
    "noise", "static", "buzzing", "uncomfortable", "painful", "sore", "hurts",
    "poor", "terrible", "awful", "bad", "useless", "fails", "failed", "stopped"
}

POSITIVE_CUE_WORDS = {
    "great", "excellent", "amazing", "good", "love", "loved", "best", "solid",
    "smooth", "snappy", "crisp", "clear", "clean", "fast", "lasts", "lasting",
    "comfortable", "lightweight", "sturdy", "durable", "premium", "reliable",
    "top tier", "easy", "responsive", "perfect", "well built", "stabilization"
}

PROMO_HYPE_WORDS = {
    "five stars", "5 stars", "best ever", "buy now", "buy immediately",
    "must buy", "everyone must", "greatest in history", "miracle product",
    "amazing seller", "exceeded all expectations", "perfect quality",
    "unbelievable smartphone", "unbelievable audio", "unbelievably",
    "perfect fast charger", "top quality adapter", "best purchase ever"
}


def _extract_targeted_clause(text: str, target_keywords: List[str], max_words: int = 26, is_negative_context: bool = False) -> str:
    """
    Extracts the specific sentence or sub-clause that directly discusses the target aspect keywords.
    Strictly separates genuine praise from critical customer complaints.
    """
    t = str(text).strip().replace("\n", " ")
    t = re.sub(r"\s+", " ", t)

    # First attempt: break by punctuation and conjunction clauses (, but / and / however / ; / .)
    clauses = re.split(r"(?<=[.!?;])\s+|\s+(?:but|however|although|whereas)\s+", t, flags=re.IGNORECASE)

    candidates = []
    for c in clauses:
        c_low = c.lower()
        # Clean out false ergonomics match for gaming/usage load
        c_for_kw = re.sub(r"\bheavy\s+(?:gaming|use|usage|load|workload|duty|task|multitasking)\b", "", c_low)
        if any(re.search(r"\b" + re.escape(kw) + r"\b", c_for_kw) for kw in target_keywords):
            clean_c = c.strip()
            clean_c = re.sub(r"^(but|and|or|however|so)\s+", "", clean_c, flags=re.IGNORECASE).strip()
            words = clean_c.split()
            if len(words) > max_words:
                clean_c = " ".join(words[:max_words]) + "..."
            
            has_neg = any(re.search(r"\b" + re.escape(nw) + r"\b", clean_c.lower()) for nw in NEGATIVE_CUE_WORDS)
            has_pos = any(re.search(r"\b" + re.escape(pw) + r"\b", clean_c.lower()) for pw in POSITIVE_CUE_WORDS)
            has_promo = any(pw in clean_c.lower() for pw in PROMO_HYPE_WORDS)
            
            candidates.append((has_neg, has_pos, has_promo, clean_c))

    if candidates:
        if is_negative_context:
            # For complaints: prioritize negative clauses
            neg_candidates = [c for c in candidates if c[0]]
            if neg_candidates:
                return neg_candidates[0][3]
            return candidates[0][3]
        else:
            # For pros: STRICTLY FORBID clauses with negative complaints or promo spam
            pos_candidates = [c for c in candidates if not c[0] and c[1] and not c[2]]
            if pos_candidates:
                return pos_candidates[0][3]
            return ""

    # Fallback to standard sentence splitting
    sentences = re.split(r"(?<=[.!?])\s+", t)
    for s in sentences:
        s_low = s.lower()
        s_for_kw = re.sub(r"\bheavy\s+(?:gaming|use|usage|load|workload|duty|task|multitasking)\b", "", s_low)
        if any(re.search(r"\b" + re.escape(kw) + r"\b", s_for_kw) for kw in target_keywords):
            clean_s = s.strip()
            has_neg = any(re.search(r"\b" + re.escape(nw) + r"\b", clean_s.lower()) for nw in NEGATIVE_CUE_WORDS)
            has_pos = any(re.search(r"\b" + re.escape(pw) + r"\b", clean_s.lower()) for pw in POSITIVE_CUE_WORDS)
            has_promo = any(pw in clean_s.lower() for pw in PROMO_HYPE_WORDS)
            
            words = clean_s.split()
            if len(words) > max_words:
                clean_s = " ".join(words[:max_words]) + "..."
                
            if is_negative_context:
                if has_neg:
                    return clean_s
            else:
                if not has_neg and has_pos and not has_promo:
                    return clean_s

    return ""


def extract_aspect_sentiment_and_failures(
    reviews: Any,
    min_evidence_per_mode: int = 1
) -> Dict[str, Any]:
    """
    Core diagnostic pipeline:
    1. Diagnoses why a product fails in plain, human-friendly terms.
    2. Extracts targeted, non-repetitive customer review evidence quotes.
    3. Separates genuine pros (from organic reviews only, no promotional spam) from authentic cons.
    4. Computes an honest Aspect Scorecard (showing 'No Customer Feedback' instead of fake 70/100).
    """
    if isinstance(reviews, pd.DataFrame):
        rev_list = reviews.to_dict(orient="records")
    elif isinstance(reviews, list):
        rev_list = reviews
    else:
        rev_list = []

    clean_revs = []
    for r in rev_list:
        text = str(r.get("review_text", r.get("text", ""))).strip()
        if not text:
            continue
        try:
            rating = float(r.get("rating", r.get("stars", 5.0)))
        except (ValueError, TypeError):
            rating = 5.0
        
        is_susp = bool(r.get("is_suspicious", r.get("label", "") == "suspicious"))
        clean_revs.append({
            "text": text,
            "rating": rating,
            "is_suspicious": is_susp
        })

    total_reviews = len(clean_revs)
    if total_reviews == 0:
        return _empty_aspect_result()

    # Partition reviews
    critical_revs = [r for r in clean_revs if r["rating"] <= 3.0]
    # STRICT: Only verified organic positive reviews (rating >= 4 and definitely NOT suspicious)
    genuine_high_revs = [r for r in clean_revs if r["rating"] >= 4.0 and not r["is_suspicious"]]

    # -----------------------------------------------------------------------
    # 1. Product Failure Modes Analysis
    # -----------------------------------------------------------------------
    failure_modes = []
    aspect_counts = {k: {"neg": 0, "pos": 0, "quotes_neg": [], "quotes_pos": []} for k in ASPECT_DEFINITIONS}

    for rev in clean_revs:
        t_low = rev["text"].lower()
        r_val = rev["rating"]
        is_susp = rev["is_suspicious"]

        for aspect_key, spec in ASPECT_DEFINITIONS.items():
            # Exclude false ergonomics matches for "heavy gaming/use/load"
            t_kw_check = t_low
            if aspect_key == "ergonomics":
                t_kw_check = re.sub(r"\bheavy\s+(?:gaming|use|usage|load|workload|duty|task|multitasking)\b", "", t_low)

            kw_match = any(re.search(r"\b" + re.escape(kw) + r"\b", t_kw_check) for kw in spec["keywords"])
            if not kw_match:
                continue

            has_fail_pattern = any(re.search(pat, t_low) for pat in spec["failure_patterns"])
            has_pos_pattern = any(re.search(pat, t_low) for pat in spec["positive_patterns"])
            has_general_neg = any(re.search(r"\b" + re.escape(nw) + r"\b", t_low) for nw in NEGATIVE_CUE_WORDS)

            # Critical complaints
            if r_val <= 3.0 or has_fail_pattern or has_general_neg:
                q = _extract_targeted_clause(rev["text"], spec["keywords"], is_negative_context=True)
                if q:
                    aspect_counts[aspect_key]["neg"] += 1
                    if len(aspect_counts[aspect_key]["quotes_neg"]) < 4:
                        aspect_counts[aspect_key]["quotes_neg"].append({
                            "rating": int(r_val),
                            "quote": q
                        })
            # Genuine Praise: Only if NOT suspicious, rating >= 4, and strictly NO negative cues
            elif r_val >= 4.0 and not is_susp:
                q = _extract_targeted_clause(rev["text"], spec["keywords"], is_negative_context=False)
                if q:
                    aspect_counts[aspect_key]["pos"] += 1
                    if len(aspect_counts[aspect_key]["quotes_pos"]) < 4:
                        aspect_counts[aspect_key]["quotes_pos"].append({
                            "rating": int(r_val),
                            "quote": q
                        })

    total_critical = max(len(critical_revs), 1)

    for aspect_key, counts in aspect_counts.items():
        neg_count = counts["neg"]
        if neg_count == 0:
            continue

        spec = ASPECT_DEFINITIONS[aspect_key]
        incidence_pct = round((neg_count / total_critical) * 100.0, 1)

        if incidence_pct >= 40.0 or any("fire" in q["quote"].lower() or "melted" in q["quote"].lower() or "overheat" in q["quote"].lower() for q in counts["quotes_neg"]):
            severity = "Critical Failure Risk"
            severity_color = "#f43f5e"
        elif incidence_pct >= 20.0:
            severity = "High Recurrence"
            severity_color = "#f97316"
        else:
            severity = "Moderate Defect Rate"
            severity_color = "#eab308"

        failure_modes.append({
            "aspect_key": aspect_key,
            "category": spec["title"],
            "icon": spec["icon"],
            "complaint_count": neg_count,
            "incidence_pct": min(100.0, incidence_pct),
            "severity": severity,
            "severity_color": severity_color,
            "root_cause_summary": spec["customer_plain_cause"],
            "evidence_quotes": counts["quotes_neg"]
        })

    # Sort failure modes by complaint incidence
    failure_modes.sort(key=lambda x: (x["complaint_count"], x["incidence_pct"]), reverse=True)

    # -----------------------------------------------------------------------
    # 2. Authentic Cons Extraction (First Pass - Real Customer Limitations)
    # -----------------------------------------------------------------------
    cons_list = []
    seen_con_quotes = set()

    for mode in failure_modes:
        spec = ASPECT_DEFINITIONS.get(mode["aspect_key"], {})
        con_title = spec.get("con_title", f"{mode['category']} Limitations")

        selected_quote = None
        selected_rating = 2
        for eq in mode.get("evidence_quotes", []):
            q_clean = eq["quote"].strip()
            if q_clean and q_clean not in seen_con_quotes:
                selected_quote = q_clean
                selected_rating = eq["rating"]
                seen_con_quotes.add(q_clean)
                break

        if selected_quote:
            cons_list.append({
                "aspect_key": mode["aspect_key"],
                "category": mode["category"],
                "icon": mode["icon"],
                "aspect_title": con_title,
                "impact_level": mode["severity"],
                "frequency": mode["complaint_count"],
                "evidence_quote": selected_quote,
                "rating": selected_rating
            })

    # -----------------------------------------------------------------------
    # 3. Authentic Pros Extraction (Verified Organic Praise ONLY - Never in Cons)
    # -----------------------------------------------------------------------
    pros_list = []
    seen_pro_quotes = set()

    for aspect_key, counts in aspect_counts.items():
        pos_count = counts["pos"]
        neg_count = counts["neg"]
        if pos_count == 0:
            continue

        total_mentions = pos_count + neg_count
        sentiment_ratio = round((pos_count / max(total_mentions, 1)) * 100.0)

        # Must have genuine positive reviews
        if sentiment_ratio >= 40 and counts["quotes_pos"]:
            spec = ASPECT_DEFINITIONS[aspect_key]
            
            pro_titles = {
                "battery": "Reliable Battery Life & Power",
                "build": "Solid Build & Premium Materials",
                "connectivity": "Fast, Stable Wireless Connection",
                "audio": "Clear Sound Quality & Good Call Audio",
                "ergonomics": "Comfortable Grip & Everyday Fit",
                "software": "Smooth Interface & Useful Software Features"
            }
            
            best_quote = None
            for candidate in counts["quotes_pos"]:
                q_text = candidate["quote"].strip()
                if not q_text or q_text in seen_pro_quotes or q_text in seen_con_quotes:
                    continue
                # Cannot overlap with any con quote
                if any(q_text in cq or cq in q_text for cq in seen_con_quotes):
                    continue
                # Strictly forbid negative cue words
                if any(re.search(r"\b" + re.escape(nw) + r"\b", q_text.lower()) for nw in NEGATIVE_CUE_WORDS):
                    continue

                best_quote = candidate
                seen_pro_quotes.add(q_text)
                break

            if best_quote:
                pros_list.append({
                    "aspect_key": aspect_key,
                    "category": spec["title"],
                    "icon": spec["icon"],
                    "aspect_title": pro_titles.get(aspect_key, f"Commendable {spec['title']}"),
                    "sentiment_score": sentiment_ratio,
                    "frequency": pos_count,
                    "evidence_quote": best_quote["quote"],
                    "rating": max(4, int(best_quote["rating"]))
                })

    pros_list.sort(key=lambda x: (x["sentiment_score"], x["frequency"]), reverse=True)

    # Fallback only from GENUINE organic reviews (NEVER suspicious/fake reviews, and NEVER con quotes)
    if not pros_list and genuine_high_revs:
        for r in genuine_high_revs[:2]:
            q = _extract_targeted_clause(r["text"], ["great", "good", "love", "useful", "nice", "fast", "solid", "lasts", "clear"], is_negative_context=False)
            if q and q not in seen_pro_quotes and q not in seen_con_quotes:
                if not any(re.search(r"\b" + re.escape(nw) + r"\b", q.lower()) for nw in NEGATIVE_CUE_WORDS):
                    seen_pro_quotes.add(q)
                    pros_list.append({
                        "aspect_key": "general",
                        "category": "General Performance",
                        "icon": "✨",
                        "aspect_title": "Satisfactory Overall Performance",
                        "sentiment_score": 85,
                        "frequency": 1,
                        "evidence_quote": q,
                        "rating": int(r["rating"])
                    })

    # -----------------------------------------------------------------------
    # 4. Honest Aspect Scorecard (Fix 70/100 bug when 0 mentions)
    # -----------------------------------------------------------------------
    scorecard = {}
    for aspect_key, spec in ASPECT_DEFINITIONS.items():
        pos = aspect_counts[aspect_key]["pos"]
        neg = aspect_counts[aspect_key]["neg"]
        total = pos + neg

        if total == 0:
            # NO customer feedback: score is None, do NOT claim 70/100!
            scorecard[spec["title"]] = {
                "score": None,
                "has_data": False,
                "positive_count": 0,
                "negative_count": 0,
                "icon": spec["icon"],
                "status": "Not Mentioned in Reviews",
                "display": "No Customer Data"
            }
        else:
            # Legitimate customer data exists
            score = int(round((pos / total) * 100.0))
            if score >= 75:
                status = "Excellent"
            elif score >= 50:
                status = "Good / Minor Trade-offs"
            elif score >= 25:
                status = "Frequent Complaints"
            else:
                status = "High Defect Rate"

            scorecard[spec["title"]] = {
                "score": score,
                "has_data": True,
                "positive_count": pos,
                "negative_count": neg,
                "icon": spec["icon"],
                "status": status,
                "display": f"{score}/100"
            }

    # -----------------------------------------------------------------------
    # 5. Customer-Understandable Failure Summary & Guidance
    # -----------------------------------------------------------------------
    primary_failure = failure_modes[0]["category"] if failure_modes else "No recurrent defects detected"
    primary_plain_cause = failure_modes[0]["root_cause_summary"] if failure_modes else "Product exhibits typical consumer wear without major recurring defects."
    
    if failure_modes:
        top_incidence = failure_modes[0]["incidence_pct"]
        num_defects = len(failure_modes)
        failure_risk_score = min(98, int(top_incidence * 0.60 + num_defects * 7))
    else:
        failure_risk_score = 15

    if failure_risk_score >= 65:
        risk_level = "High Defect Risk"
        risk_color = "#f43f5e"
        buyer_advice = "Frequent hardware issues reported. Proceed with caution if you rely on this product daily."
    elif failure_risk_score >= 35:
        risk_level = "Moderate Trade-Offs"
        risk_color = "#f97316"
        buyer_advice = "Some noticeable flaws reported by buyers, but product remains functional for general use."
    else:
        risk_level = "Low Failure Rate"
        risk_color = "#10b981"
        buyer_advice = "Hardware stability is solid with few severe customer complaints."

    # Customer-friendly diagnostic summary
    if failure_modes:
        pct_mention = failure_modes[0]['incidence_pct']
        exec_text = (
            f"The #1 problem reported by customers is **{primary_failure}** (mentioned in **{pct_mention:.0f}%** of critical reviews). "
            f"**What happens:** {primary_plain_cause} "
            f"**Buyer Advice:** {buyer_advice}"
        )
    else:
        exec_text = "Verified reviews indicate consistent day-to-day performance with no major recurring hardware breakdowns."

    return {
        "summary": {
            "total_reviews_analyzed": total_reviews,
            "critical_reviews_count": len(critical_revs),
            "genuine_positive_count": len(genuine_high_revs),
            "primary_failure_reason": primary_failure,
            "failure_risk_score": failure_risk_score,
            "failure_risk_level": risk_level,
            "failure_risk_color": risk_color,
            "durability_verdict": buyer_advice,
            "executive_diagnostic": exec_text
        },
        "failure_modes": failure_modes,
        "pros": pros_list,
        "cons": cons_list,
        "aspect_scorecard": scorecard
    }


def _empty_aspect_result() -> Dict[str, Any]:
    return {
        "summary": {
            "total_reviews_analyzed": 0,
            "critical_reviews_count": 0,
            "genuine_positive_count": 0,
            "primary_failure_reason": "No reviews available",
            "failure_risk_score": 0,
            "failure_risk_level": "N/A",
            "failure_risk_color": "#94a3b8",
            "durability_verdict": "Insufficient data to analyze product reliability.",
            "executive_diagnostic": "No customer feedback found for this product."
        },
        "failure_modes": [],
        "pros": [],
        "cons": [],
        "aspect_scorecard": {}
    }
