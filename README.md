# TakeMeter

A fine-tuned text classifier that evaluates discourse quality in football/soccer online communities. Built for AI201 CodePath Project 3.

## Community

**r/soccer** (with r/PremierLeague and r/football as supplemental sources) — one of Reddit's largest and most text-heavy sports communities, with discourse ranging from detailed tactical breakdowns to emotional match reactions to unfounded hot takes.

## Labels

| Label | Definition |
|-------|-----------|
| `analysis` | Structured argument backed by statistics, tactical observations, or historical comparisons. Evidence drives the claim. |
| `hot_take` | Bold opinion stated without supporting evidence. Asserts rather than argues; often includes hyperbole or tribal framing. |
| `reaction` | Immediate emotional response to a specific event (goal, result, VAR call, transfer). Time-anchored to the moment. |

See [`planning.md`](planning.md) for full label definitions, concrete examples, and edge case decision rules.

## Dataset

- **Source:** Collected posts and comments from r/soccer (and related football subreddits)
- **Total examples:** 223, in a single file [`data/labeled.csv`](data/labeled.csv) (`text`, `label`, `notes`)
- **Split:** the notebook splits 70% / 15% / 15% (≈156 / 33 / 34) automatically at load time
- **Label distribution:** `reaction` 75 | `analysis` 74 | `hot_take` 74 (balanced — no class over 70%)

### Difficult annotation cases

See [`planning.md`](planning.md#labeling-decisions--3-genuinely-difficult-cases) for 3 documented hard calls with reasoning.

## Model

- **Base model:** `distilbert-base-uncased`
- **Fine-tuning platform:** Google Colab (T4 GPU), via the TakeMeter starter notebook
- **Training setup:** 3 epochs, learning rate `2e-5`, batch size 16 (starter defaults)
- **Key hyperparameter decision:** *(to be filled after the run — defaults vs. an adjusted learning rate)*

## Baseline

Zero-shot comparison using Groq `llama-3.3-70b-versatile` on the same held-out test split.
The classification prompt (label definitions + single-word output) is implemented in
[`baseline_groq.py`](baseline_groq.py) and pasted into the notebook's baseline section.

## Results

*(To be filled after evaluation)*

| Model | Overall Accuracy |
|-------|-----------------|
| Fine-tuned DistilBERT | — |
| Zero-shot LLaMA 3.3 70B | — |

Full evaluation report including per-class metrics and confusion matrix: [`outputs/evaluation_results.json`](outputs/evaluation_results.json)

## Setup

```bash
# Clone the repo
git clone https://github.com/fortdominz/ai201-project3-takemeter.git
cd ai201-project3-takemeter

# Install dependencies (for the local Groq baseline)
pip install -r requirements.txt

# Add your Groq key
cp .env.example .env        # then edit .env and paste your GROQ_API_KEY
```

**Fine-tuning** runs in Google Colab on a T4 GPU using the TakeMeter starter notebook:

1. Open the starter notebook → **File → Save a copy in Drive**.
2. **Runtime → Change runtime type → T4 GPU.**
3. Add `GROQ_API_KEY` via the 🔑 **Secrets** panel (enable notebook access).
4. Section 1: set the label map and upload [`data/labeled.csv`](data/labeled.csv); Section 2 splits + tokenizes.
5. Section 5: paste the Groq prompt (from [`baseline_groq.py`](baseline_groq.py)) and run the baseline.
6. Sections 3–4: fine-tune DistilBERT and evaluate; Section 6 writes `evaluation_results.json`.
7. Download `evaluation_results.json` + `confusion_matrix.png` into `outputs/` and commit.

**Groq baseline (local reference, optional)** — the prompt also runs standalone, no GPU:

```bash
python baseline_groq.py --test data/labeled.csv   # writes outputs/baseline_results.json
```

## Project Structure

```
ai201-project3-takemeter/
├── planning.md              # Label taxonomy, edge cases, metrics, success criteria, AI tool plan
├── README.md
├── baseline_groq.py         # Groq zero-shot baseline prompt (reference + local CLI)
├── requirements.txt         # Local dependencies
├── .env.example             # Template for GROQ_API_KEY (.env is gitignored)
├── data/
│   └── labeled.csv          # Full annotated dataset, single file (223 examples)
└── outputs/
    ├── evaluation_results.json    # (downloaded from Colab after the run)
    └── confusion_matrix.png       # (downloaded from Colab after the run)
```

> Fine-tuning happens in your Drive copy of the **starter notebook**, so the notebook itself
> isn't committed here — only the data, docs, and the outputs you download from it.
