# TakeMeter

A fine-tuned text classifier that labels the **discourse type** of football/soccer community comments — `analysis`, `hot_take`, or `reaction`. Built for AI201 CodePath Project 3.

A fine-tuned `distilbert-base-uncased` (66M params) reaches **0.765 accuracy / 0.75 macro-F1** on a held-out test set, beating a zero-shot `llama-3.3-70b-versatile` baseline (0.706 / 0.71) while being ~1000× smaller.

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
- **Size:** 223 examples in a single file, [`data/labeled.csv`](data/labeled.csv) (`id`, `text`, `label`, `source`, `notes`).
- **Distribution:** `reaction` 75 · `analysis` 74 · `hot_take` 74 — balanced, no class above 34% (well under the 70% imbalance threshold).
- **Split:** the notebook splits 70/15/15 (stratified) at load time → **156 train / 33 val / 34 test**.

### Labeling process (with AI disclosure)

Labels were assigned by an **AI-assisted pass**: a heuristic classifier built from the `planning.md` taxonomy pre-labeled all 223 comments, which were then reviewed against the edge-case rules. This is disclosed in full in the [AI usage](#ai-usage) section. The error analysis below shows the **`reaction` class carries the most label noise**, so that class is the priority for continued manual review.

### Three genuinely difficult annotation cases

1. **"Klose was in four World Cups, all four times Germany reached the semis… but nobody would rate him above Ronaldo Fenômeno and Messi."** → **`hot_take`**. Cites a real stat, but the conclusion (a GOAT-ranking) overstates what the stat supports — the stat *decorates* a predetermined opinion (edge-case rule 1).
2. **"Insane that Mbappé has that many at 27. He's gonna obliterate the record."** → **`reaction`**. Posted live, right after Messi tied Klose's record; the prediction processes the in-the-moment amazement rather than standing as independent analysis (edge-case rule 2).
3. **"Van Dijk simply deserved it… high press, more area to cover, zero red cards all season."** → **`analysis`**. Multiple supporting points (tactical context + a discipline stat) used as the *basis* of the claim, not as decoration (edge-case rule 3).

---

## Model — fine-tuning approach

- **Base model:** `distilbert-base-uncased` (HuggingFace), with a fresh 3-class classification head.
- **Platform:** Google Colab, T4 GPU.
- **Final training config:** 10 epochs · learning rate `5e-5` · batch size 16 · weight decay 0.01 · `warmup_steps=10` · `load_best_model_at_end` on validation accuracy.

### Key hyperparameter decision

The starter defaults (3 epochs, `lr=2e-5`, `warmup_steps=50`) **failed to train the model at all** — validation accuracy sat at 0.36 (≈ the 0.33 random floor) and training loss barely moved from `ln(3)≈1.099`. Diagnosis: with 156 examples and batch 16 there are only ~10 steps/epoch × 3 = **30 total steps, but warmup was 50 steps** — so the learning rate never finished warming up and the model took 30 near-zero-magnitude steps.

**Fix:** `warmup_steps 50 → 10`, `epochs 3 → 10`, `lr 2e-5 → 5e-5`. Validation accuracy then climbed from 0.61 to 0.67 and the model learned all three classes. Validation loss bottomed around epoch 3–4 and rose afterward (classic overfitting on a small set), so `load_best_model_at_end` selects the best-validation checkpoint rather than the final epoch.

---

## Baseline — zero-shot LLaMA-3.3-70B (Groq)

A zero-shot prompt to `llama-3.3-70b-versatile` (temperature 0), evaluated on the **same 34-example test split**. The prompt supplies the three label definitions + decision rules, one example each, and instructs the model to output exactly one lowercase label string. **0 / 34 responses were unparseable.** The exact prompt lives in [`baseline_groq.py`](baseline_groq.py).

---

## Evaluation report

### Overall

| Model | Accuracy | Macro-F1 |
|-------|:--------:|:--------:|
| Zero-shot LLaMA-3.3-**70B** | 0.706 | 0.71 |
| Fine-tuned **DistilBERT (66M)** | **0.765** | **0.75** |
| **Δ (fine-tune − baseline)** | **+0.059** | **+0.04** |

### Per-class (test set, n = 34)

| Class | Baseline P / R / F1 | Fine-tuned P / R / F1 |
|-------|:-------------------:|:---------------------:|
| `analysis` | 0.90 / 0.82 / 0.86 | 0.85 / **1.00** / **0.92** |
| `hot_take` | 0.62 / 0.73 / 0.67 | 0.67 / **0.91** / **0.77** |
| `reaction` | 0.64 / 0.58 / **0.61** | 0.83 / 0.42 / 0.56 |

### Confusion matrix — fine-tuned model

Rows = true label, columns = predicted label.

| true ↓ / pred → | analysis | hot_take | reaction |
|-----------------|:--------:|:--------:|:--------:|
| **analysis**    | **11**   | 0        | 0        |
| **hot_take**    | 0        | **10**   | 1        |
| **reaction**    | 2        | 5        | **5**    |

(See [`outputs/confusion_matrix.png`](outputs/confusion_matrix.png) for the rendered image; full metrics in [`outputs/evaluation_results.json`](outputs/evaluation_results.json).)

### Did it hit the success criteria?

The `planning.md` targets, scored honestly:

| Criterion | Target | Result | |
|-----------|--------|--------|---|
| Beat the baseline | ≥ 10 pts accuracy | +5.9 pts | ✗ narrowly missed |
| Overall quality | macro-F1 ≥ 0.70 | 0.75 | ✓ met |
| No collapsed class | every class F1 ≥ 0.60 | `reaction` = 0.56 | ✗ narrowly missed |

The headline isn't a blowout, and that's the interesting result: **a 70B zero-shot model is a strong baseline that's hard to beat by a wide margin with only 156 training examples.** The fine-tuned model still wins overall and is ~1000× smaller (a real deployment advantage), but the margin is modest and concentrated in two classes.

### Error analysis — 3 specific failures

The model made **8 errors on 34 test examples, 7 of them on the `reaction` class, and 5 of those are `reaction → hot_take`.** The confusion is directional and concentrated on one boundary.

1. **Genuine error — model weights opinion over emotion.**
   *"switzerland was so dominant but so bad too, i was borderline screaming at my TV cause they just looked incompetent…"* — **true `reaction` → predicted `hot_take` (conf 0.90).**
   "screaming at my TV" is a textbook in-the-moment emotional cue, but the model latched onto the evaluative phrasing ("dominant but bad") and confidently read it as an opinion. This is a real model weakness: it keys on opinion *content* and under-weights emotional/temporal markers.

2. **Label noise — the model is arguably right.**
   *"…he just retired, but Tom Brady should be in that group too."* — **true `reaction` → predicted `hot_take` (conf 0.95).**
   Structurally this *is* an assertion ("should be in that group"), so `hot_take` is defensible — the gold `reaction` label is questionable. High-confidence "errors" like this reveal annotation noise in the `reaction` class, not a model failure.

3. **Genuinely ambiguous boundary.**
   *"Thank god for that laser of a kick, will totally distract from the fact that his teammate just..tripped over his own feet…"* — **true `hot_take` → predicted `reaction` (conf 0.87).**
   Sarcastic banter anchored to a *specific play* — the live-event framing legitimately pulls toward `reaction`. This is the `hot_take`/`reaction` boundary genuinely blurring when banter is time-anchored, exactly the hard case `planning.md` anticipated.

**What this points to:** the `reaction ↔ hot_take` boundary is the model's weak spot because (a) both are short, opinionated, and emotionally charged, and (b) the `reaction` training labels are the noisiest. Tellingly, **the zero-shot 70B model is actually *better* on `reaction` (F1 0.61 vs 0.56)** — its broad pretraining grasp of "emotional reaction" beats a small model trained on noisy reaction labels. The fix is more about **cleaner/more `reaction` data** than more training. 

### Sample classifications (fine-tuned model)

> Confidence = softmax probability of the predicted class.

| Comment (abbrev.) | Predicted | Confidence | Correct? |
|---|---|:---:|:---:|
| "do you seriously think Mexico, in its current state politically, financially… [can host]" | analysis | 0.98 | ✓ |
| "What a dull pedestrian game to watch, incredible Roberto Martinez continues to be employed without doing anything" | hot_take | 0.78 | ✓ |
| "when youre the greatest country in the world people will just hat lol" | reaction | 0.66 | ✓ |
| "switzerland was so dominant but so bad too, i was borderline screaming at my TV…" | hot_take | 0.90 | ✗ (true reaction) |
| "Thank god for that laser of a kick, will distract from his teammate tripping…" | reaction | 0.87 | ✗ (true hot_take) |

**Why the top prediction is reasonable:** the first comment builds a reasoned case — weighing Mexico's political and financial readiness as a host — rather than just asserting, so `analysis` at 0.98 is well-judged. More broadly, every `analysis` test post was classified correctly (recall 1.00): the model reliably fires `analysis` when a comment uses tactical/statistical/historical reasoning as evidence, the clearest of the three boundaries. The confidence spread is also telling — a clean `analysis` at 0.98 vs. a correctly-labeled but genuinely borderline `reaction` at just 0.66 — which shows the model is reasonably calibrated about *which* boundaries are hard.

---

## Reflection — what the model learned vs. what I intended

I intended the model to learn **discourse structure**: evidence-driven argument (`analysis`) vs. unsupported assertion (`hot_take`) vs. in-the-moment emotional response (`reaction`).

It learned the first two boundaries well. It clearly picks up on evidence/tactical/statistical language for `analysis` (perfect recall) and on confident assertion for `hot_take`. But for `reaction` it **under-learned the "time-anchored emotional response" concept** and collapsed many reactions into `hot_take`. In effect the model's decision boundary is closer to *"evidence-backed vs. not"* (a two-way split) than the intended three-way structural distinction — it treats `reaction` as "a hot_take that happens to be short."

Two causes: (1) `reaction` and `hot_take` genuinely overlap in surface form (both short, emotive, opinionated — the only reliable separator is temporal anchoring, which is subtle), and (2) the `reaction` labels were the noisiest, so the training signal for that class was the weakest. The gap between intended and learned behavior is therefore as much a **data-quality** story as a modeling one.

---

## Spec reflection

- **One way the spec helped:** requiring `planning.md` *with explicit edge-case decision rules before labeling* forced me to define the boundaries precisely (e.g. the "stat-decorated hot take" rule). That paid off twice: labeling was consistent, and the error analysis mapped directly onto a boundary I'd already named (`reaction ↔ hot_take`) instead of being a vague "the model got confused."
- **One way the implementation diverged:** the plan was to treat the starter defaults as a working baseline and document a clean `2e-5` vs `5e-5` learning-rate comparison. In reality the defaults didn't train at all (the `warmup_steps > total_steps` bug), so the real hyperparameter decision became *diagnosing and fixing the warmup/epochs*, surfaced only at runtime from a flat loss curve — a more useful lesson than a tidy sweep would have been.

---

## AI usage

1. **Taxonomy stress-testing.** Directed an AI assistant to pressure-test the three label definitions and generate boundary cases (stat-decorated hot takes, reasoned reactions). Its outputs became the three edge-case decision rules in `planning.md`. I overrode its instinct toward a 4-label scheme and folded "banter" into `hot_take` to keep ~75 examples per class.
2. **Annotation assistance (disclosed).** The 223 labels were produced by an AI-assisted heuristic pass built from the taxonomy, then reviewed against the edge-case rules — not labeled cold by hand. The error analysis confirmed the `reaction` class needs the most continued review, which is the active priority.
3. **Failure-pattern analysis.** Gave the list of 8 misclassifications to an AI assistant to surface patterns; it flagged the directional `reaction → hot_take` confusion and the "label-noise vs. genuine error" distinction, which I then verified by re-reading each example (and which drives the error analysis above).
4. **Training debugging.** The `warmup_steps (50) > total_steps (30)` diagnosis and the fix came from an AI assistant reading the flat training-loss curve; I applied and verified it.

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
│   └── labeled.csv          # 223 labeled comments (single file)
└── outputs/
    ├── evaluation_results.json    # downloaded from Colab
    └── confusion_matrix.png       # downloaded from Colab
```
