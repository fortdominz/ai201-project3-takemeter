"""
Zero-shot baseline for TakeMeter using Groq's llama-3.3-70b-versatile.

Classifies football-discourse comments into analysis / hot_take / reaction
with no fine-tuning — just label definitions in the prompt. Used as the
comparison point for the fine-tuned DistilBERT model on the same test set.

Run locally:
    pip install -r requirements.txt
    # put GROQ_API_KEY in a .env file (see .env.example)
    python baseline_groq.py

Or import and call run_baseline(...) from the training notebook.
"""

import os
import re
import json
import time
import argparse

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

LABELS = ["analysis", "hot_take", "reaction"]

SYSTEM_PROMPT = """You are a text classifier for an online football (soccer) community. \
You assign each comment exactly ONE of three labels based on its DISCOURSE STRUCTURE, not its topic.

Labels:
- analysis: a structured argument backed by statistics, tactical observations, or historical \
comparisons. Evidence drives the claim. Removing the opinion, the evidence alone still supports the conclusion.
- hot_take: a bold, confident opinion stated WITHOUT systematic evidence. Asserts rather than argues. \
Includes banter, hyperbole, tribal/rivalry framing, GOAT debates, and "overrated/underrated" claims.
- reaction: an immediate emotional response to a specific event (a goal, result, VAR call, transfer, \
retirement) that just happened. Time-anchored to the moment, expressing feeling rather than argument.

Decision rules:
- A single stat wrapped in hyperbole is a hot_take, not analysis.
- If an argument exists only to justify an emotional response to something that just happened, it is a reaction.
- Classify by structure, not topic: a detailed post about a terrible manager is still analysis if it uses evidence.

Respond with ONLY the label: analysis, hot_take, or reaction. No other words, no punctuation."""


def _parse_label(raw: str) -> str:
    """Map a raw model response to one of the three labels (best-effort)."""
    t = raw.strip().lower()
    # direct hits first
    if "hot_take" in t or "hot take" in t or "hot-take" in t:
        return "hot_take"
    if "analysis" in t or "analytical" in t:
        return "analysis"
    if "reaction" in t or "reactive" in t:
        return "reaction"
    # fall back to first label word found
    for lbl in LABELS:
        if re.search(rf"\b{lbl}\b", t):
            return lbl
    return "hot_take"  # safe default: the majority/asserting class


def classify_text(client, text: str, model: str = "llama-3.3-70b-versatile") -> str:
    """Zero-shot classify a single comment. Retries once on transient errors."""
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=model,
                temperature=0,
                max_tokens=8,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f'Classify this comment:\n\n"{text}"'},
                ],
            )
            return _parse_label(resp.choices[0].message.content)
        except Exception as e:  # rate limit / transient
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
            else:
                raise e


def run_baseline(test_csv_path: str, api_key: str = None,
                 model: str = "llama-3.3-70b-versatile", pause: float = 1.0) -> dict:
    """Classify every row of the test set and return a metrics dict."""
    from groq import Groq

    key = api_key or os.environ.get("GROQ_API_KEY")
    if not key:
        raise RuntimeError(
            "No Groq API key found. Set GROQ_API_KEY in your environment or pass api_key=..."
        )
    client = Groq(api_key=key)

    df = pd.read_csv(test_csv_path)
    y_true, y_pred = [], []
    for i, row in df.iterrows():
        pred = classify_text(client, str(row["text"]), model=model)
        y_true.append(row["label"])
        y_pred.append(pred)
        print(f"[{i + 1}/{len(df)}] true={row['label']:<9} pred={pred:<9} | {str(row['text'])[:60]}")
        time.sleep(pause)  # stay under free-tier rate limits

    acc = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, labels=LABELS, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=LABELS).tolist()

    print("\n=== Groq zero-shot baseline ===")
    print(f"Model: {model}")
    print(f"Accuracy: {acc:.3f}")
    print(classification_report(y_true, y_pred, labels=LABELS, zero_division=0))

    return {
        "model": model,
        "approach": "zero-shot",
        "accuracy": acc,
        "classification_report": report,
        "confusion_matrix": {"labels": LABELS, "matrix": cm},
        "predictions": [
            {"text": str(t), "true": yt, "pred": yp}
            for t, yt, yp in zip(df["text"], y_true, y_pred)
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="Groq zero-shot baseline for TakeMeter")
    parser.add_argument("--test", default="data/test.csv", help="Path to test CSV")
    parser.add_argument("--out", default="outputs/baseline_results.json", help="Where to write results JSON")
    parser.add_argument("--model", default="llama-3.3-70b-versatile")
    args = parser.parse_args()

    # Load GROQ_API_KEY from .env if present (local runs)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    results = run_baseline(args.test, model=args.model)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved baseline results to {args.out}")


if __name__ == "__main__":
    main()
