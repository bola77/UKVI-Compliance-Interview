from pathlib import Path
import yaml

BASE = Path(__file__).resolve().parent.parent.parent
SCORING_CFG = BASE / "config" / "scoring_rules.yaml"

with open(SCORING_CFG, "r", encoding="utf-8") as f:
    SCORING_RULES = yaml.safe_load(f)

RISK_SCORES = SCORING_RULES.get("risk_scores", {})
READINESS_THRESHOLDS = SCORING_RULES.get("readiness_thresholds", {})

def analyse_funding_transcript(text: str) -> dict:
    t = text.lower()
    has_sponsor = any(w in t for w in ["sponsor", "father", "mother", "uncle", "aunty"])
    has_job = any(w in t for w in ["engineer", "banker", "teacher", "civil servant", "business", "trader"])
    mentions_naira = "naira" in t
    mentions_pounds = any(w in t for w in ["pound", "gbp", "sterling"])
    mentions_saving_period = any(w in t for w in ["years", "months", "28 days", "since", "for a long time"])
    mentions_recent = any(w in t for w in ["recently", "just", "last month", "last week"])

    signals = {
        "has_sponsor": has_sponsor,
        "has_job": has_job,
        "mentions_naira": mentions_naira,
        "mentions_pounds": mentions_pounds,
        "mentions_saving_period": mentions_saving_period,
        "mentions_recent": mentions_recent,
    }

    risk_boost = 0
    if not has_sponsor or not has_job:
        risk_boost += 2
    if mentions_recent and not mentions_saving_period:
        risk_boost += 2
    if not mentions_naira and not mentions_pounds:
        risk_boost += 1

    return {"signals": signals, "extra_risk": risk_boost}

def analyse_intent_transcript(text: str) -> dict:
    t = text.lower()
    mentions_nigeria = any(w in t for w in ["nigeria", "lagos", "abuja", "port harcourt"])
    mentions_return = any(w in t for w in ["return", "come back", "go back"])
    mentions_job = any(w in t for w in ["job", "career", "role", "position"])
    mentions_company = any(w in t for w in ["company", "firm", "organisation", "organization"])
    mentions_post_study = any(w in t for w in ["post-study", "graduate route", "psw"])

    risk_boost = 0
    if not mentions_nigeria or not mentions_return:
        risk_boost += 2
    if not mentions_job and not mentions_company:
        risk_boost += 2
    if mentions_post_study and not (mentions_return and mentions_nigeria):
        risk_boost += 1

    signals = {
        "mentions_nigeria": mentions_nigeria,
        "mentions_return": mentions_return,
        "mentions_job": mentions_job,
        "mentions_company": mentions_company,
        "mentions_post_study": mentions_post_study,
    }
    return {"signals": signals, "extra_risk": risk_boost}

def score_answer(transcript: str, risk_tag: str = None, theme: str = None) -> dict:
    """
    Score an answer transcript on 5Cs and risk, with simple Nigeria-focused heuristics.
    """
    base_risk = RISK_SCORES.get(risk_tag, 0)
    extra_risk = 0

    # Default content score
    content = 0.6

    if theme == "funding":
        funding = analyse_funding_transcript(transcript)
        extra_risk += funding["extra_risk"]
        has_sponsor = funding["signals"]["has_sponsor"]
        has_job = funding["signals"]["has_job"]
        content = 0.7 if (has_sponsor and has_job) else 0.4
    elif theme in ("future_plans", "motivation_for_uk"):
        intent = analyse_intent_transcript(transcript)
        extra_risk += intent["extra_risk"]
        mentions_nigeria = intent["signals"]["mentions_nigeria"]
        mentions_return = intent["signals"]["mentions_return"]
        content = 0.7 if (mentions_nigeria and mentions_return) else 0.4

    # Very simple correctness/clarity/confidence/composure placeholders for now
    correctness = 0.6 if transcript.strip() else 0.0
    clarity = 0.6 if len(transcript.split()) > 10 else 0.4
    confidence = 0.6
    composure = 0.6

    risk_score = base_risk + extra_risk

    return {
        "correctness": correctness,
        "content": content,
        "clarity": clarity,
        "confidence": confidence,
        "composure": composure,
        "risk_tags": [risk_tag] if risk_tag else [],
        "risk_score": risk_score,
    }

def aggregate_session_scores(track: str, answers: list) -> dict:
    """
    Compute average 5C scores and total risk_score for a session, and READY/NOT READY.
    """
    if not answers:
        return {
            "avg_correctness": 0.0,
            "avg_content": 0.0,
            "avg_clarity": 0.0,
            "avg_confidence": 0.0,
            "avg_composure": 0.0,
            "total_risk_score": 0.0,
            "overall_avg_5c": 0.0,
            "ready": False,
        }

    n = len(answers)
    sums = {
        "correctness": 0.0,
        "content": 0.0,
        "clarity": 0.0,
        "confidence": 0.0,
        "composure": 0.0,
    }
    total_risk = 0.0

    for q in answers:
        s = q.get("scores", {})
        sums["correctness"] += s.get("correctness", 0.0)
        sums["content"] += s.get("content", 0.0)
        sums["clarity"] += s.get("clarity", 0.0)
        sums["confidence"] += s.get("confidence", 0.0)
        sums["composure"] += s.get("composure", 0.0)
        total_risk += s.get("risk_score", 0.0)

    avg_5c = {k: v / n for k, v in sums.items()}
    thresholds = READINESS_THRESHOLDS.get(track, READINESS_THRESHOLDS.get("ukvi", {}))
    min_avg_5c = thresholds.get("min_avg_5c", 0.65)
    max_total_risk = thresholds.get("max_total_risk", 6)

    overall_avg_5c = sum(avg_5c.values()) / len(avg_5c)
    ready = (overall_avg_5c >= min_avg_5c) and (total_risk <= max_total_risk)

    return {
        "avg_correctness": avg_5c["correctness"],
        "avg_content": avg_5c["content"],
        "avg_clarity": avg_5c["clarity"],
        "avg_confidence": avg_5c["confidence"],
        "avg_composure": avg_5c["composure"],
        "total_risk_score": total_risk,
        "overall_avg_5c": overall_avg_5c,
        "ready": ready,
    }