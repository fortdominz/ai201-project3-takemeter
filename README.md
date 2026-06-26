# TakeMeter

A fine-tuned text classifier that labels the **discourse type** of football/soccer community comments — `analysis`, `hot_take`, or `reaction`. Built for AI201 CodePath Project 3.

A fine-tuned `distilbert-base-uncased` (66M params) reaches **0.735 accuracy / 0.73 macro-F1** on a held-out test set, beating a zero-shot `llama-3.3-70b-versatile` baseline (0.676 / 0.68) while being ~1000× smaller.

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
- **Distribution:** `reaction` 75 · `analysis` 74 · `hot_take` 73 — balanced, no class above 34% (well under the 70% imbalance threshold).
- **Split:** the notebook splits 70/15/15 (stratified) at load time → **155 train / 33 val / 34 test**.

### Labeling process (with AI disclosure)

Labels were assigned by an **AI-assisted pass**: a heuristic classifier built from the `planning.md` taxonomy pre-labeled all comments, which were then reviewed against the edge-case rules. This is disclosed in full in the [AI usage](#ai-usage) section. The error analysis below shows the **`reaction` ↔ `hot_take` boundary carries the most label noise**, so those classes are the priority for continued manual review.

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

The starter defaults (3 epochs, `lr=2e-5`, `warmup_steps=50`) **failed to train the model at all** — validation accuracy sat at 0.36 (≈ the 0.33 random floor) and training loss barely moved from `ln(3)≈1.099`. Diagnosis: with ~155 examples and batch 16 there are only ~10 steps/epoch × 3 = **30 total steps, but warmup was 50 steps** — so the learning rate never finished warming up and the model took 30 near-zero-magnitude steps.

**Fix:** `warmup_steps 50 → 10`, `epochs 3 → 10`, `lr 2e-5 → 5e-5`. Validation accuracy then climbed into the 0.6–0.7 range and the model learned all three classes. Validation loss bottomed around epoch 3–4 and rose afterward (classic overfitting on a small set), so `load_best_model_at_end` selects the best-validation checkpoint rather than the final epoch.

---

## Baseline — zero-shot LLaMA-3.3-70B (Groq)

A zero-shot prompt to `llama-3.3-70b-versatile` (temperature 0), evaluated on the **same 34-example test split**. The prompt supplies the three label definitions + decision rules, one example each, and instructs the model to output exactly one lowercase label string. **0 / 34 responses were unparseable.** The exact prompt lives in [`baseline_groq.py`](baseline_groq.py).

---

## Evaluation report

### Overall

| Model | Accuracy | Macro-F1 |
|-------|:--------:|:--------:|
| Zero-shot LLaMA-3.3-**70B** | 0.676 | 0.68 |
| Fine-tuned **DistilBERT (66M)** | **0.735** | **0.73** |
| **Δ (fine-tune − baseline)** | **+0.059** | **+0.05** |

### Per-class (test set, n = 34)

| Class | Baseline P / R / F1 | Fine-tuned P / R / F1 |
|-------|:-------------------:|:---------------------:|
| `analysis` | 0.82 / 0.82 / 0.82 | 0.85 / **1.00** / **0.92** |
| `hot_take` | 0.67 / 0.55 / 0.60 | 0.75 / 0.55 / **0.63** |
| `reaction` | 0.57 / 0.67 / 0.62 | 0.62 / 0.67 / **0.64** |

The fine-tuned model beats the baseline on **all three classes**, with the biggest gain on `analysis` (perfect recall).

### Confusion matrix — fine-tuned model

Rows = true label, columns = predicted label.

| true ↓ / pred → | analysis | hot_take | reaction |
|-----------------|:--------:|:--------:|:--------:|
| **analysis**    | **11**   | 0        | 0        |
| **hot_take**    | 0        | **6**    | 5        |
| **reaction**    | 2        | 2        | **8**    |

(See [`outputs/confusion_matrix.png`](outputs/confusion_matrix.png) for the rendered image; full metrics in [`outputs/evaluation_results.json`](outputs/evaluation_results.json).)

### Did it hit the success criteria?

The `planning.md` targets, scored honestly:

| Criterion | Target | Result | |
|-----------|--------|--------|---|
| Overall quality | macro-F1 ≥ 0.70 | 0.73 | ✓ met |
| No collapsed class | every class F1 ≥ 0.60 | min = 0.63 (`hot_take`) | ✓ met |
| Beat the baseline | ≥ 10 pts accuracy | +5.9 pts | ✗ narrowly missed |

Two of three met. The headline isn't a blowout, and that's the interesting result: **a 70B zero-shot model is a strong baseline that's hard to beat by a wide margin with only ~155 training examples.** The fine-tuned model still wins overall *and on every class*, and is ~1000× smaller (a real deployment advantage) — but the accuracy margin is modest.

### Error analysis — 3 specific failures

The model made **9 errors on 34 test examples, and 7 of them are `reaction` ↔ `hot_take` confusion** (5 `hot_take → reaction`, 2 `reaction → hot_take`). The remaining 2 are `reaction → analysis`. That one boundary dominates the errors.

1. **The dominant pattern — sarcastic banter read as reaction.**
   *"Thank god for that laser of a kick, will totally distract from the fact that his teammate just.. tripped over his own feet…"* — **true `hot_take` → predicted `reaction` (conf 0.92).**
   Sarcastic banter anchored to a *specific play* — the live-event framing pulls the model toward `reaction`, even though structurally it's an unfounded jab (`hot_take`). High confidence, and exactly the hard case `planning.md` anticipated.

2. **Topical ≠ emotional.**
   *"Don't forget ICE detaining and denying entry to some of the Iraq World Cup team and its associated staffing."* — **true `hot_take` → predicted `reaction` (conf 0.86).**
   A pointed political opinion that *references* an ongoing situation. The model appears to equate "mentions a current event" with "emotional reaction to an event," when the structure here is an asserted opinion. A model weakness, not a label problem.

3. **Length/structure overriding the emotional cue.**
   *"It was truly incredible premonition. The US-coverage broadcast talent has been notably good so far, but this prediction amazed me…"* — **true `reaction` → predicted `analysis` (conf 0.87).**
   A long, expository recounting of a commentator's prediction. The amazement ("amazed me") makes it a `reaction`, but its descriptive, multi-clause structure reads like `analysis`. Here the gold label is itself borderline.

**What this points to:** `reaction` and `hot_take` overlap heavily — both are short, emotive, and opinionated about football — and the only reliable separator is *time-anchoring to a live event*, which is subtle. Notably, in an earlier run on a slightly different split the same boundary dominated the errors but in the **opposite direction** (`reaction → hot_take`). The *direction* is unstable; the *boundary* being the weak spot is consistent — strong evidence it's a genuine task difficulty, not a fluke of one split. The fix is cleaner/more `reaction`-vs-`hot_take` training data rather than more training.

### Sample classifications (fine-tuned model)

> Confidence = softmax probability of the predicted class.

| Comment (abbrev.) | Predicted | Confidence | Correct? |
|---|---|:---:|:---:|
| "do you seriously think Mexico, in its current state politically, financially… [could host]" | analysis | 0.96 | ✓ |
| "But the hosting concerns were still there! Those slaves didn't come back to life!" | reaction | 0.94 | ✓ |
| "What a dull pedestrian game to watch, incredible Roberto Martinez continues to be employed without doing anything" | hot_take | 0.65 | ✓ |
| "Thank god for that laser of a kick, will distract from his teammate tripping…" | reaction | 0.92 | ✗ (true hot_take) |
| "It was truly incredible premonition… this prediction amazed me" | analysis | 0.87 | ✗ (true reaction) |

**Why a correct prediction is reasonable:** the first comment builds a reasoned case — weighing Mexico's political and financial readiness as a host — rather than just asserting, so `analysis` at 0.96 is well-judged. More broadly, every `analysis` test post was classified correctly (recall 1.00): the model reliably fires `analysis` when a comment uses tactical/statistical/historical reasoning as evidence, the clearest of the three boundaries. The confidence spread is telling too — a clean `analysis` at 0.96 vs. a correctly-labeled but more opinion-heavy `hot_take` at just 0.65 — so the model is reasonably calibrated about which calls are hard.

---

## Reflection — what the model learned vs. what I intended

I intended the model to learn **discourse structure**: evidence-driven argument (`analysis`) vs. unsupported assertion (`hot_take`) vs. in-the-moment emotional response (`reaction`).

It learned `analysis` cleanly — perfect recall, high confidence — because evidence/tactical/statistical language is a separable signal. But it did **not** cleanly learn the `reaction` vs. `hot_take` distinction: across two runs the model confused them in *both* directions, depending on the split. In effect its decision boundary is closer to *"is this evidence-backed?"* (a clean two-way split) than the intended three-way structural distinction — it treats `reaction` and `hot_take` as nearly the same region of space, separated only by whether the comment happens to mention a current event.

Two causes: (1) the two classes genuinely overlap in surface form (both short, emotive, opinionated — the only reliable separator, temporal anchoring, is subtle), and (2) those were the noisiest labels. So the gap between intended and learned behavior is as much a **data-quality / task-difficulty** story as a modeling one.

---

## Spec reflection

- **One way the spec helped:** requiring `planning.md` *with explicit edge-case decision rules before labeling* forced me to define the boundaries precisely (e.g. the "stat-decorated hot take" rule). That paid off twice: labeling was consistent, and the error analysis mapped directly onto a boundary I'd already named (`reaction ↔ hot_take`) instead of being a vague "the model got confused."
- **One way the implementation diverged:** the plan was to treat the starter defaults as a working baseline and document a clean `2e-5` vs `5e-5` learning-rate comparison. In reality the defaults didn't train at all (the `warmup_steps > total_steps` bug), so the real hyperparameter decision became *diagnosing and fixing the warmup/epochs*, surfaced only at runtime from a flat loss curve — a more useful lesson than a tidy sweep would have been.

---

## AI usage

1. **Taxonomy stress-testing.** Directed an AI assistant to pressure-test the three label definitions and generate boundary cases (stat-decorated hot takes, reasoned reactions). Its outputs became the three edge-case decision rules in `planning.md`. I overrode its instinct toward a 4-label scheme and folded "banter" into `hot_take` to keep ~75 examples per class.
2. **Annotation assistance (disclosed).** The labels were produced by an AI-assisted heuristic pass built from the taxonomy, then reviewed against the edge-case rules — not labeled cold by hand. The error analysis confirmed the `reaction`/`hot_take` boundary needs the most continued review.
3. **Data cleaning.** A first extraction had a bug that truncated some words (`Switzerland`→`witzerland`) and dropped apostrophes; I had an AI assistant re-extract from source and mechanically correct spelling/apostrophes/capitalization **without rewording** (so discourse structure — and the labels — stay intact), then verified the diff.
4. **Failure-pattern analysis.** Gave the list of misclassifications to an AI assistant to surface patterns; it flagged the `reaction ↔ hot_take` dominance and the direction-flip across runs, which I verified by re-reading each example.
5. **Training debugging.** The `warmup_steps (50) > total_steps (30)` diagnosis and the fix came from an AI assistant reading the flat training-loss curve; I applied and verified it.

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
