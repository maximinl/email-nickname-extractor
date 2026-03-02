# Email Nickname Extractor

Extracts informal nicknames of users from their sent and received emails using an LLM pipeline.

Built as a proof of concept for information extraction over semi-structured corporate email data. The system generates a synthetic dataset of financial advisor emails, runs an LLM to identify nicknames per person, and evaluates extraction quality against ground truth.

## How It Works

**1. Synthetic data generation** (`generate_emails.py`) — Creates 120 emails between 10 financial advisors at a fictional firm. Seven of the ten have nicknames that appear naturally in email text. Three have no nicknames, serving as negative controls.

**2. Nickname extraction** (`extract_nicknames.py`) — For each advisor, collects all emails they sent or received and sends them to DeepSeek in a single prompt. The model identifies any nicknames used for that person, along with evidence and confidence scores. Processing is done per person (not per email) to give the model enough context for cross-referencing.

**3. Evaluation** (`evaluate.py`) — Compares extracted nicknames against ground truth. Reports precision, recall, and F1. Includes a per-person breakdown showing true positives, false positives, and misses.

## Quick Start
```bash
pip install -r requirements.txt
export DEEPSEEK_API_KEY="your-key"

python generate_emails.py
python extract_nicknames.py
python evaluate.py
```

## Results

| Metric | Score |
|---|---|
| Precision | 100% |
| Recall | 100% |
| F1 | 100% |
| True Positives | 12 |
| False Positives | 0 |
| False Negatives | 0 |

## Design Decisions

| Decision | Rationale |
|---|---|
| Synthetic data with templates | Gives reliable ground truth for evaluation. Real emails would need manual labeling. |
| Per-person extraction (not per-email) | More context per API call. The model sees nickname usage patterns across multiple emails. |
| 70/30 nickname usage split | Realistic: people don't always use nicknames. Tests the extractor on mixed signals. |
| Advisors without nicknames | Tests false positive rate. A good extractor shouldn't hallucinate nicknames. |
| JSON structured output | Parseable, auditable. Evidence field allows debugging. |

## Extending This

Some natural next steps for a production version:
- Real email ingestion via Gmail API or Microsoft Graph
- Multi-model comparison (GPT-4, Claude, Gemini) with cost/accuracy tradeoffs
- Async batch processing for cost efficiency at scale
- Confidence thresholds to only surface high-confidence nicknames
- Incremental updates when new emails arrive without reprocessing everything
