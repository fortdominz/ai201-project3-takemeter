# TakeMeter — Planning Document

## Project Summary

**Community:** r/soccer (and r/PremierLeague, r/football as supplemental sources)

**Task:** Classify the discourse quality of football community posts and comments into one of three structural categories that reflect how fans actually talk about the sport.

**Why these distinctions matter to the community:** In football Reddit, discourse quality is constantly debated — fans distinguish between "actually watching the game" analysis, loud opinions with no backing, and emotional venting after results. The labels below map to these three recognized modes of participation that regulars in the community already implicitly rank and call out.

**Long-term vision:** Labels are designed to be discourse-structural, not football-specific. `analysis`, `hot_take`, and `reaction` apply to any community — this dataset trains the foundation of a general-purpose discourse quality classifier.

---

## Label Taxonomy

### Labels

| Label | One-sentence definition |
|-------|------------------------|
| `analysis` | The post makes a structured argument backed by statistics, tactical observations, or historical comparisons — evidence drives the claim. |
| `hot_take` | A bold, confident opinion stated without supporting evidence; the post asserts rather than argues, often with hyperbole or tribal framing. |
| `reaction` | An immediate emotional response to a specific ongoing event (goal, result, transfer, VAR decision); expresses feeling in the moment with little to no argument. |

---

### Label 1: `analysis`

**Definition:** The post constructs an argument where specific, verifiable evidence is the foundation — not decoration. Remove the opinion framing and the evidence alone should still support the conclusion. Includes statistical breakdowns, tactical observations (formations, pressing, defensive shape), historical comparisons, and data-driven player evaluations.

**Clear examples:**

> "Saka's underlying numbers this season are genuinely elite — 0.31 xA per 90 and 6.1 progressive carries per 90 puts him in the top 5% of wingers across the top 5 leagues. The 'inconsistent' narrative doesn't hold up when you look at the actual data."

→ `analysis`: cites specific, verifiable stats; stats support the conclusion; evidence precedes the opinion.

> "The reason City concede against low blocks isn't personnel — it's a system issue. Their 4-3-3 vacates the halfspaces when the 8s push wide to overload the wings, and that's exactly where Villa and Newcastle have been scoring against them since October. It's a structural vulnerability Pep hasn't addressed."

→ `analysis`: identifies a tactical mechanism, links it to specific outcomes, names a time pattern. The claim is supported, not asserted.

**One uncertain case:** See Edge Cases section below.

---

### Label 2: `hot_take`

**Definition:** A bold, confident opinion stated without systematic evidence. The post asserts rather than argues. May include banter, hyperbole, tribal rivalry content, or "unpopular opinion" framing. The defining feature: if you remove the opinion, there's no evidence chain left — just the claim.

**Clear examples:**

> "Haaland is honestly just a poacher and not a real striker. Any target man with pace could do what he does in that City system. Completely system-dependent."

→ `hot_take`: bold claim, no evidence, no tactical backing — pure assertion.

> "Ronaldo's legacy is permanently ruined by going to Saudi. He'll be a footnote in 15 years. Messi won the World Cup and Ronaldo is playing in a retirement league."

→ `hot_take`: compares careers with tribal framing, no statistical support, conclusion overstates what the comparison shows.

**One uncertain case:** See Edge Cases section below.

---

### Label 3: `reaction`

**Definition:** An immediate emotional response to a specific, ongoing event — a goal, result, controversial VAR call, transfer announcement, or injury news. The post is expressing a feeling triggered by something that just happened, not making a general argument about the sport. Time-anchored to the moment.

**Clear examples:**

> "THAT VAR DECISION IS AN ABSOLUTE JOKE. HOW IS THAT NOT A RED CARD. THE REFEREE IS BLIND."

→ `reaction`: all-caps, triggered by a specific call in a live match, expresses emotion not argument.

> "I literally cannot stop shaking. That 94th-minute winner after being 2-0 down... I've been a fan for 20 years and this is the best night of my life."

→ `reaction`: personal emotional response to a specific result, no argument or claim being made.

**One uncertain case:** See Edge Cases section below.

---

## Edge Cases and Decision Rules

### Edge Case 1: The stat-decorated hot take (analysis vs. hot_take)

**Example post:**
> "Mbappe's move to Real Madrid clearly hasn't worked out — he got 27 goals in La Liga compared to 45 in all competitions at PSG. The drop-off is obvious."

**Why it's ambiguous:** It cites specific numbers (27 vs 45), which looks like `analysis`. But the comparison is between different leagues (La Liga vs Ligue 1), different competitions (league-only vs all comps), and 27 La Liga goals is actually strong by most standards. The numbers were selected to support a predetermined conclusion.

**Decision rule:** If the evidence chain meaningfully supports the conclusion — that is, removing the opinion framing, the numbers alone still tell the same story — label it `analysis`. If the stats are selectively chosen or the conclusion overstates what the numbers actually show, label it `hot_take`. The post above → `hot_take`: the comparison is apples-to-oranges and the conclusion ("clearly hasn't worked out") overstates the data.

---

### Edge Case 2: The reasoned reaction (reaction vs. analysis)

**Example post:**
> "That penalty decision cost us the game and it's the 4th time this season a VAR call has gone against us in the final 20 minutes. There is a systemic bias in how these decisions are reviewed."

**Why it's ambiguous:** It's triggered by a specific match event (→ `reaction`), but it also makes a data-backed claim about a pattern over the season (→ `analysis`).

**Decision rule:** If the post is clearly anchored to a specific moment that just happened AND the argument serves to express or justify the emotional response rather than explain a phenomenon, label it `reaction`. If the post could stand alone as a general argument without the triggering event, label it `analysis`. The post above → `reaction`: the "systemic bias" claim exists to validate the immediate frustration, not as a standalone structural argument.

---

### Edge Case 3: The confident opinion with a single fact (hot_take vs. analysis)

**Example post:**
> "Trent Alexander-Arnold is the most overrated player in Premier League history. Yes, he creates chances — but his defensive numbers are in the bottom 20% of fullbacks in the league. His attacking stats are a mirage built on a system that papers over his weaknesses."

**Why it's ambiguous:** The defensive stat is specific and potentially verifiable. But "most overrated in Premier League history" is pure hyperbole, and the single stat is embedded in a clearly partisan argument.

**Decision rule:** A single verifiable stat does not make a post `analysis`. For `analysis`, the evidence must be (1) multiple data points or a coherent tactical observation, AND (2) used as the basis of the argument, not to add credibility to a claim that was already made. One stat wrapped in hyperbole → `hot_take`.

---

## Mutual Exclusivity Check

| Boundary | How to distinguish |
|----------|-------------------|
| `analysis` vs `hot_take` | Does the evidence drive the conclusion, or decorate it? Would the numbers alone — without the opinion framing — support the same claim? |
| `hot_take` vs `reaction` | Is the post triggered by a specific event happening right now? `reaction` is time-anchored. `hot_take` is a general opinion that could be posted any day. |
| `analysis` vs `reaction` | Does the post construct an argument that stands independently of any triggering event? If so, `analysis`. If the argument exists to process an emotion about something just happening, `reaction`. |

---

## Dataset Plan

### Data Sources
- **Primary:** r/soccer (largest English-language football community, ~3M members)
- **Secondary:** r/PremierLeague, r/football (UK-centric)
- **Post types to target:**
  - Match threads → rich in `reaction` examples
  - "Who else thinks..." / "Unpopular opinion" posts → rich in `hot_take`
  - Tactical breakdown posts, "why X team struggles against Y" → rich in `analysis`

### Collection Method
Manual collection using Reddit's web interface. Copy top-level comments and short posts. Aim for variety across clubs, topics, and time periods to avoid encoding team bias.

### Target Distribution

| Label | Target count | % |
|-------|-------------|---|
| `analysis` | 70+ | ~33% |
| `hot_take` | 70+ | ~33% |
| `reaction` | 70+ | ~33% |
| **Total** | **210+** | 100% |

### Train / Val / Test Split

| Split | Size | Purpose |
|-------|------|---------|
| Train | ~147 (70%) | Fine-tuning |
| Val | ~32 (15%) | Hyperparameter tuning |
| Test | ~31 (15%) | Final evaluation (held out until end) |

---

## Annotation Guidelines

1. **Classify by structure, not topic.** A detailed post about a terrible manager can still be `analysis` if it uses evidence. A short post about a beautiful tactical goal can still be `reaction` if it's just expressing feeling.
2. **When uncertain, apply the decision rules above in order:** edge case 1 first (stat-decorated hot take), then edge case 2 (reasoned reaction).
3. **Posts that are 50/50 even after applying the rules:** label with the category that captures the dominant intent of the post.
4. **Exclude:** posts under 10 words, posts that are only memes/images with no text, posts in languages other than English.

---

## Labeling Decisions — 3 Genuinely Difficult Cases

*(To be filled in after annotation is complete — document 3 hard calls, what you labeled them, and why.)*

1. **Post:** [to be filled]  **Decided:** [label] **Why:**
2. **Post:** [to be filled]  **Decided:** [label] **Why:**
3. **Post:** [to be filled]  **Decided:** [label] **Why:**

---

## Fine-Tuning Plan

- **Base model:** `distilbert-base-uncased` (HuggingFace)
- **Platform:** Google Colab (free T4 GPU)
- **Key hyperparameter decision to document:** learning rate (likely 2e-5 vs 5e-5) — will run both and report val loss

---

## Baseline Comparison Plan

- **Baseline model:** Groq `llama-3.3-70b-versatile` (zero-shot)
- **Prompt strategy:** Provide label definitions + ask for single-word label output
- **Evaluation:** Same 31-example test set for both models

---

## Stretch Features Planned

- [ ] Deployed Gradio interface (builds on Project 2 skills)
- [ ] Error pattern analysis (systematic failure modes)
- [ ] Inter-annotator reliability (have a groupmate label 30 examples)
