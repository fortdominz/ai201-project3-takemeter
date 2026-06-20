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

- **Source:** Manually collected posts and comments from r/soccer, r/PremierLeague, r/football
- **Total examples:** 223
- **Split:** 70% train / 15% val / 15% test → 156 / 33 / 34
- **Label distribution:** `analysis` 74 | `hot_take` 74 | `reaction` 75

### Difficult annotation cases

See [`planning.md`](planning.md#labeling-decisions--3-genuinely-difficult-cases) for 3 documented hard calls with reasoning.

## Model

- **Base model:** `distilbert-base-uncased`
- **Fine-tuning platform:** Google Colab (T4 GPU)
- **Training approach:** *(to be filled)*
- **Key hyperparameter decision:** *(to be filled — e.g., learning rate choice)*

## Baseline

Zero-shot comparison using Groq `llama-3.3-70b-versatile` on the same test set.

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

# Install dependencies (for the Groq baseline script)
pip install groq pandas scikit-learn
```

Fine-tuning runs in Google Colab — see [`notebooks/`](notebooks/) for the training notebook.

## Project Structure

```
ai201-project3-takemeter/
├── planning.md              # Label taxonomy, edge cases, data plan
├── README.md
├── data/
│   ├── raw/                 # Collected posts before labeling
│   ├── labeled.csv          # Full annotated dataset
│   ├── train.csv
│   ├── val.csv
│   └── test.csv
├── notebooks/
│   └── takemeter_training.ipynb
└── outputs/
    ├── evaluation_results.json
    └── confusion_matrix.png
```
