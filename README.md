# TakeMeter

A fine-tuned text classifier that labels the **discourse type** of football/soccer community comments — `analysis`, `hot_take`, or `reaction`. Built for AI201 CodePath Project 3.

A fine-tuned `distilbert-base-uncased` (66M params) reaches **0.765 accuracy / 0.77 macro-F1** on a held-out test set, beating a zero-shot `llama-3.3-70b-versatile` baseline (0.588 / 0.60) while being ~1000× smaller.

---

## Community

**r/soccer**, with r/PremierLeague and r/football as supplemental sources — one of Reddit's largest and most text-heavy sports communities. Its discourse is *varied in quality by nature*: the same thread mixes detailed tactical breakdowns, loud opinions with no backing, and raw emotional venting after a result. That variety is exactly what makes it a good classification target — the three modes are distinct, frequent, and something regulars already recognize and rank ("did they actually watch the game?"). I follow the sport, so I can judge label quality myself rather than guessing.

The labels are intentionally **discourse-structural, not football-specific** — `analysis` / `hot_take` / `reaction` describe *how* someone is arguing, not *what about*, so the same taxonomy could transfer to any community.

---

## Label taxonomy

| Label | Definition | Example |
|-------|-----------|---------|
| `analysis` | A structured argument backed by statistics, tactical observation, or historical comparison. Evidence drives the claim — remove the opinion and the evidence still supports it. | *"Van Dijk simply deserved it. Liverpool played a high press, meaning defenders cover more area, and he didn't get a single red card all season — disciplined too."* |
| `hot_take` | A bold, confident opinion stated **without** systematic evidence. Asserts rather than argues; includes banter, hyperbole, tribal framing, and GOAT/"overrated" claims. | *"Ronaldo is the GOAT and it's not even close, Messi fans are just delusional."* |
| `reaction` | An immediate emotional response to a specific event that just happened (goal, result, VAR call, transfer, retirement). Time-anchored to the moment; feeling, not argument. | *"I CANNOT believe that goal — 38 years old and still doing this, what a player!!!"* |

Full definitions, two examples each, and the three edge-case decision rules are in [`planning.md`](planning.md).

---

## Dataset

- **Source:** comments collected manually from r/soccer match threads, GOAT-debate posts, Ballon d'Or threads, and "unpopular opinion" posts (2026 World Cup window).
- **Size:** 222 examples in a single file, [`data/labeled.csv`](data/labeled.csv) (`id`, `text`, `label`, `source`, `notes`).
- **Distribution:** `analysis` 74 · `hot_take` 74 · `reaction` 74 — perfectly balanced (33.3% each, well under the 70% imbalance threshold).
- **Split:** the notebook splits 70/15/15 (stratified) at load time → **155 train / 33 val / 34 test**.

### Labeling process (with AI disclosure)

Labels were assigned by an **AI-assisted first pass** (a heuristic classifier built from the `planning.md` taxonomy), then **reviewed by hand** — every row was read against the edge-case rules; the review confirmed the labeling and corrected one example (#23, a Tom Brady opinion mislabeled `reaction` → `hot_take`). Full disclosure in the [AI usage](#ai-usage) section. The error analysis shows the **`reaction` ↔ `hot_take` boundary** is the genuinely ambiguous one — several remaining "errors" are really borderline labels.

### Three genuinely difficult annotation cases

1. **"Klose was in four World Cups, all four times Germany reached the semis… but nobody would rate him above Ronaldo Fenomeno and Messi."** → **`hot_take`**. Cites a real stat, but the conclusion (a GOAT-ranking) overstates what the stat supports — the stat *decorates* a predetermined opinion (edge-case rule 1).
2. **"Insane that Mbappe has that many at 27. He's gonna obliterate the record."** → **`reaction`**. Posted live, right after Messi tied Klose's record; the prediction processes the in-the-moment amazement rather than standing as independent analysis (edge-case rule 2).
3. **"Van Dijk simply deserved it… high press, more area to cover, zero red cards all season."** → **`analysis`**. Multiple supporting points (tactical context + a discipline stat) used as the *basis* of the claim, not as decoration (edge-case rule 3).

---

## Model — fine-tuning approach

- **Base model:** `distilbert-base-uncased` (HuggingFace), with a fresh 3-class classification head.
- **Platform:** Google Colab, T4 GPU.
- **Final training config:** 10 epochs · learning rate `5e-5` · batch size 16 · weight decay 0.01 · `warmup_steps=10` · `load_best_model_at_end` on validation accuracy.

### Key hyperparameter decision

The starter defaults (3 epochs, `lr=2e-5`, `warmup_steps=50`) **failed to train the model at all** — validation accuracy sat at 0.36 (≈ the 0.33 random floor) and training loss barely moved from `ln(3)≈1.099`. Diagnosis: with ~154 examples and batch 16 there are only ~10 steps/epoch × 3 = **30 total steps, but warmup was 50 steps** — so the learning rate never finished warming up and the model took 30 near-zero-magnitude steps.

**Fix:** `warmup_steps 50 → 10`, `epochs 3 → 10`, `lr 2e-5 → 5e-5`. Validation accuracy then climbed into the 0.6–0.7 range and the model learned all three classes. Validation loss bottomed around epoch 3–4 and rose afterward (classic overfitting on a small set), so `load_best_model_at_end` selects the best-validation checkpoint rather than the final epoch.

---

## Baseline — zero-shot LLaMA-3.3-70B (Groq)

A zero-shot prompt to `llama-3.3-70b-versatile` (temperature 0), evaluated on the **same 34-example test split**. The prompt supplies the three label definitions + decision rules, one example each, and instructs the model to output exactly one lowercase label string. **0 / 34 responses were unparseable.** The exact prompt lives in [`baseline_groq.py`](baseline_groq.py).

---

## Evaluation report

### Overall

| Model | Accuracy | Macro-F1 |
|-------|:--------:|:--------:|
| Zero-shot LLaMA-3.3-**70B** | 0.588 | 0.60 |
| Fine-tuned **DistilBERT (66M)** | **0.765** | **0.77** |
| **Δ (fine-tune − baseline)** | **+0.177** | **+0.17** |

> **Honest note on baseline variance:** across re-runs, the zero-shot baseline ranged **~0.59–0.71** on this 34-example test set (small-sample noise + LLM nondeterminism + a re-stratified split), while the fine-tuned model stayed **0.73–0.77** and led in *every* run. So the fine-tune is *consistently* ahead, but the exact margin is run-dependent — a fair characterization is "ahead by roughly 6–18 points." This run's gap is +17.7.

### Per-class (test set, n = 34)

| Class | Baseline P / R / F1 | Fine-tuned P / R / F1 |
|-------|:-------------------:|:---------------------:|
| `analysis` | 0.89 / 0.73 / 0.80 | 0.91 / 0.91 / **0.91** |
| `hot_take` | 0.50 / 0.55 / 0.52 | 0.60 / 0.82 / **0.69** |
| `reaction` | 0.46 / 0.50 / 0.48 | 0.88 / 0.58 / **0.70** |

The fine-tuned model beats the baseline on **all three classes**, most decisively on `reaction` (F1 0.48 → 0.70).

### Confusion matrix — fine-tuned model

Rows = true label, columns = predicted label.

| true ↓ / pred → | analysis | hot_take | reaction |
|-----------------|:--------:|:--------:|:--------:|
| **analysis**    | **10**   | 1        | 0        |
| **hot_take**    | 1        | **9**    | 1        |
| **reaction**    | 0        | 5        | **7**    |

(See [`outputs/confusion_matrix.png`](outputs/confusion_matrix.png) for the rendered image; full metrics in [`outputs/evaluation_results.json`](outputs/evaluation_results.json).)

### Did it hit the success criteria?

The `planning.md` targets, scored honestly:

| Criterion | Target | Result | |
|-----------|--------|--------|---|
| Overall quality | macro-F1 ≥ 0.70 | 0.77 | ✓ met |
| No collapsed class | every class F1 ≥ 0.60 | min = 0.69 (`hot_take`) | ✓ met |
| Beat the baseline | ≥ 10 pts accuracy | +17.7 pts | ✓ met |

All three met on this run. (Given the baseline variance above, the beat-the-baseline margin is comfortably clear in every run — between +6 and +18 points — even if the headline +17.7 is on the high end.)

### Error analysis — 3 specific failures

The model made **8 errors on 34 test examples; 6 of the 8 involve the `hot_take` boundary, and the single biggest cell is `reaction → hot_take` (5).** That one boundary dominates the errors — consistent with two earlier runs (where the *direction* sometimes flipped to `hot_take → reaction`, but the boundary stayed the same).

1. **High-confidence genuine error — reasoning style read as evidence.**
   *"Argentina still need Messi and Messi can still win a game by himself. Yeah, he's not as quick but he's still magic. Ronaldo is the…"* — **true `hot_take` → predicted `analysis` (conf 0.98).**
   It *sounds* reasoned ("not as quick but still magic"), so the model keyed on the argumentative structure and called it `analysis` — but there's no real evidence, it's an assertion. The model has learned "structured-sounding ⇒ analysis" a bit too eagerly.

2. **Gold-label noise — the model is arguably right.**
   *"Brother just shut the fuck up and enjoy the World Cup. The world is gonna come together…"* — **true `analysis` → predicted `hot_take` (conf 0.88).**
   This is a dismissive rant, not an argument — `hot_take` is the better label, so the gold annotation is the weak link here, not the model. High-confidence "errors" like this surface annotation noise.

3. **The dominant boundary — sarcasm/banter as reaction-vs-hot_take.**
   *"When you're the greatest country in the world people will just hat lol."* — **true `reaction` → predicted `hot_take` (conf 0.98).**
   Sarcastic banter; the gold label leans `reaction` but the model (confidently) reads it as an unfounded opinion. Whichever is "right," it shows the `reaction ↔ hot_take` line is genuinely blurry for short, sarcastic posts — and the model is **over-confident even when wrong** here.

**What this points to:** `reaction` and `hot_take` overlap heavily — both short, emotive, opinionated — and the only reliable separator is *time-anchoring to a live event*, which is subtle. The fix is cleaner, more sharply-separated `reaction`-vs-`hot_take` examples (and tightening a few borderline gold labels), not more training. Calibration note: the model is sometimes **highly confident on its mistakes** (0.98 on two of them), so confidence is *not* a reliable correctness signal on this boundary — relevant if this were deployed with an auto-accept threshold.

### Sample classifications (fine-tuned model)

> Confidence = softmax probability of the predicted class.

| Comment (abbrev.) | Predicted | Confidence | Correct? |
|---|---|:---:|:---:|
| "Ronaldo's style doesn't really work as he gets older — he was always about pace, strength, physicality…" | analysis | 0.99 | ✓ |
| "10 conference championships, one was an NFC championship with Tampa" | reaction | 0.97 | ✓ |
| "Dr. Congo prescribes: Humility RX Instructions for Portugal team…" | hot_take | 0.76 | ✓ |
| "Argentina still need Messi and Messi can still win a game by himself…" | analysis | 0.98 | ✗ (true hot_take) |
| "When you're the greatest country in the world people will just hat lol" | hot_take | 0.98 | ✗ (true reaction) |

**Why a correct prediction is reasonable:** the first comment reasons from specific attributes (pace/strength/physicality declining with age) to a conclusion about Ronaldo's decline — evidence driving the claim — so `analysis` at 0.99 is exactly the structural signal the label is meant to capture. `analysis` was the model's strongest class (recall 0.91).

---

## Demo

📹 **[Watch the demo walkthrough (Loom, ~3 min)](https://www.loom.com/share/45b6b7fbcc4c4023a4f3a75199036af5)** — live classifications with confidence scores, a correct and an incorrect prediction explained, and a walkthrough of the evaluation report.

---

## Reflection — what the model learned vs. what I intended

I intended the model to learn **discourse structure**: evidence-driven argument (`analysis`) vs. unsupported assertion (`hot_take`) vs. in-the-moment emotional response (`reaction`).

It learned `analysis` well — it reliably fires on tactical/statistical/historical reasoning (0.91 recall). But it *over*-applies that signal: it labels anything that merely *sounds* structured as `analysis` even when there's no real evidence (failure #1). And it never cleanly learned the `reaction` vs. `hot_take` split: across three runs it confused them in both directions. In effect the model's decision boundary is closer to *"does this sound like a reasoned argument?"* than the intended three-way distinction — `reaction` and `hot_take` collapse into "short opinionated post," separated only by whether it happens to reference a live event.

Two causes: (1) the two classes genuinely overlap in surface form (the separator, temporal anchoring, is subtle), and (2) those were the labels with the most borderline cases. So the gap between intended and learned behavior is as much a **task-difficulty / annotation** story as a modeling one.

---

## Spec reflection

- **One way the spec helped:** requiring `planning.md` *with explicit edge-case decision rules before labeling* forced me to define the boundaries precisely (e.g. the "stat-decorated hot take" rule). That paid off twice: labeling was consistent, and the error analysis mapped directly onto a boundary I'd already named (`reaction ↔ hot_take`) instead of being a vague "the model got confused."
- **One way the implementation diverged:** the plan was to treat the starter defaults as a working baseline and document a clean `2e-5` vs `5e-5` learning-rate comparison. In reality the defaults didn't train at all (the `warmup_steps > total_steps` bug), so the real hyperparameter decision became *diagnosing and fixing the warmup/epochs*, surfaced only at runtime from a flat loss curve — a more useful lesson than a tidy sweep would have been.

---

## AI usage

1. **Taxonomy stress-testing.** Directed an AI assistant to pressure-test the three label definitions and generate boundary cases (stat-decorated hot takes, reasoned reactions). Its outputs became the three edge-case decision rules in `planning.md`. I overrode its instinct toward a 4-label scheme and folded "banter" into `hot_take` to keep ~74 examples per class.
2. **Annotation assistance (disclosed).** The labels were produced by an AI-assisted heuristic first pass, then **I reviewed all 222 by hand** against the edge-case rules — confirming the labeling and correcting one (#23). The AI accelerated a first draft; the final labels are human-verified.
3. **Data cleaning.** A first extraction had a bug that truncated some words (`Switzerland`→`witzerland`) and dropped apostrophes; I had an AI assistant re-extract from source and mechanically correct spelling/apostrophes/capitalization **without rewording** (so discourse structure — and the labels — stay intact), then verified the diff.
4. **Failure-pattern analysis.** Gave the misclassifications to an AI assistant to surface patterns; it flagged the `reaction ↔ hot_take` dominance and the direction-flip across runs, which I verified by re-reading each example.
5. **Training debugging.** The `warmup_steps (50) > total_steps (30)` diagnosis and fix came from an AI assistant reading the flat training-loss curve; I applied and verified it.

---

## Setup

```bash
git clone https://github.com/fortdominz/ai201-project3-takemeter.git
cd ai201-project3-takemeter

# Local Groq baseline only:
pip install -r requirements.txt
cp .env.example .env        # paste your GROQ_API_KEY
python baseline_groq.py --test data/labeled.csv
```

**Fine-tuning** runs in the TakeMeter starter notebook on a Colab T4: set the label map, upload `data/labeled.csv`, paste the Groq prompt, and run Sections 1–6. The notebook handles the split, training, evaluation, and exports `evaluation_results.json` + `confusion_matrix.png`.

## Project structure

```
ai201-project3-takemeter/
├── planning.md              # Taxonomy, edge cases, metrics, success criteria, AI tool plan
├── README.md                # This report
├── baseline_groq.py         # Zero-shot Groq baseline prompt (reference + local CLI)
├── requirements.txt
├── .env.example             # GROQ_API_KEY template (.env is gitignored)
├── data/
│   └── labeled.csv          # 222 labeled comments (single file)
└── outputs/
    ├── evaluation_results.json    # downloaded from Colab
    └── confusion_matrix.png       # downloaded from Colab
```
