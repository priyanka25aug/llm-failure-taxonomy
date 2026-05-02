# LLM Failure Taxonomy

**Author:** Priyanka Bajaj

Companion code for: *Beyond Hallucination: A System-Level Failure Taxonomy for Production LLMs*

A structured, empirically-grounded taxonomy of failures observed in production large language model (LLM) systems, together with a labeled incident dataset, a rule-based classifier, a Claude API-powered classifier, and a per-use-case failure budget calculator.

---

## Failure Taxonomy — 6 Classes

| Class | Name | Description |
|-------|------|-------------|
| CLASS_1 | **Model Drift** | Output distribution shifts over time without intentional change |
| CLASS_2 | **Infrastructure** | Serving stack failures: latency, OOM, routing, API contract |
| CLASS_3 | **Integration** | Application/LLM boundary failures: injection, truncation, tool-calls, RAG |
| CLASS_4 | **Evaluation** | Eval framework failures: metric gaming, contamination, distribution gap |
| CLASS_5 | **Safety & Compliance** | PII leaks, hallucinated citations, policy violations, copyright, auditability |
| CLASS_6 | **Operational** | Monitoring blind-spots, missing runbooks, escalation breakdowns, canary gaps |

### Sub-classes

| Class | Sub | Name |
|-------|-----|------|
| CLASS_1 | 1a | Upstream model update |
| CLASS_1 | 1b | Production distribution shift |
| CLASS_1 | 1c | Context window saturation |
| CLASS_2 | 2a | Latency regression |
| CLASS_2 | 2b | OOM / resource exhaustion |
| CLASS_2 | 2c | Routing misclassification |
| CLASS_2 | 2d | API breaking change |
| CLASS_3 | 3a | Prompt injection / jailbreak |
| CLASS_3 | 3b | Context truncation |
| CLASS_3 | 3c | Tool-call hallucination |
| CLASS_3 | 3d | RAG retrieval mismatch |
| CLASS_3 | 3e | Multi-turn corruption |
| CLASS_4 | 4a | Metric gaming |
| CLASS_4 | 4b | Eval contamination |
| CLASS_4 | 4c | Production distribution gap |
| CLASS_4 | 4d | Point vs distributional |
| CLASS_5 | 5a | PII leak |
| CLASS_5 | 5b | Hallucinated citations |
| CLASS_5 | 5c | Policy violation |
| CLASS_5 | 5d | Auditability gap |
| CLASS_5 | 5e | Copyright reproduction |
| CLASS_6 | 6a | Monitoring blind-spot |
| CLASS_6 | 6b | Runbook absence |
| CLASS_6 | 6c | Escalation breakdown |
| CLASS_6 | 6d | Canary gap |

---

## Failure Budget Risk Classes

| Class | Name | Max Failure Rate | Use Cases |
|-------|------|-----------------|-----------|
| **FC_A** | Decision-Critical | 1 / 1,000 requests | Legal, medical, financial, regulatory |
| **FC_B** | Customer-Facing | 5 / 1,000 requests | Chatbots, APIs, user-visible features |
| **FC_C** | Internal Productivity | 20 / 1,000 requests | Internal tools, developer workflows |
| **FC_D** | Experimental | 100 / 1,000 requests | Research prototypes, non-production |

---

## Repository Structure

```
llm-failure-taxonomy/
├── data/
│   └── public_incidents/
│       └── incidents.csv          # 50 labeled real-world LLM incidents
├── taxonomy/
│   └── taxonomy.yaml              # Full taxonomy definition
├── src/
│   ├── classifier/
│   │   ├── models.py              # Dataclasses and enums
│   │   ├── rule_based.py          # Weighted regex classifier
│   │   └── llm_classifier.py      # Claude API-powered classifier
│   ├── failure_budget/
│   │   └── calculator.py          # Per-use-case failure budget calculator
│   └── analysis/
│       └── analyzer.py            # 7 matplotlib analysis figures
├── tests/
│   └── test_classifier.py         # 11 unit tests (stdlib only)
├── paper/
│   └── draft_outline.md           # Paper outline for arXiv / MLSys 2026
├── outputs/
│   └── charts/                    # Generated figures (gitignored)
└── requirements.txt
```

---

## Quick Start

```bash
pip install -r requirements.txt

# Run all 11 unit tests
python tests/test_classifier.py

# Classify an incident with the rule-based classifier
python - <<'EOF'
from src.classifier.rule_based import classify_text
r = classify_text(
    "Hallucinated Legal Citations",
    "Attorney submitted brief with fictitious case citations. Court sanctioned lawyers.",
    domain="legal"
)
print(r.failure_class, r.failure_budget_class, r.confidence)
EOF

# Failure budget example
python - <<'EOF'
from src.failure_budget.calculator import FailureBudgetCalculator
calc = FailureBudgetCalculator()
uc = calc.create_use_case("legal-ai", "FC_A", 100_000)
for _ in range(50):
    calc.record_failure("legal-ai", "CLASS_5_SAFETY_COMPLIANCE", "high")
calc.generate_report().print_report()
EOF

# Generate all 7 analysis figures
python src/analysis/analyzer.py

# LLM classifier demo (requires ANTHROPIC_API_KEY)
python src/classifier/llm_classifier.py
```

---

## Dataset Statistics

- **Total incidents:** 50
- **Date range:** 2000–2024
- **Silent failures:** ~50% (detectability=silent)
- **Source types:** court documents, regulatory filings, academic papers, company postmortems, public news, synthetic
- **Domains:** legal, financial services, healthcare, enterprise productivity, general, e-commerce, content generation, code generation

---

## Generated Figures

| Figure | Description |
|--------|-------------|
| fig1_class_distribution.png | Bar chart of incident counts by failure class |
| fig2_severity_heatmap.png | Heatmap of severity × failure class |
| fig3_detectability.png | Stacked bar of detectability by failure class |
| fig4_blast_radius.png | Pie chart of blast radius distribution |
| fig5_domain_breakdown.png | Horizontal bar of incident counts by domain |
| fig6_mttd_boxplot.png | Boxplot of mean time to detect by class (log scale) |
| fig7_failure_budget_class.png | Bar chart of FC-A/B/C/D distribution |

---

## Citation

```bibtex
@misc{bajaj2026llmfailure,
  title   = {Beyond Hallucination: A System-Level Failure Taxonomy for Production LLMs},
  author  = {Bajaj, Priyanka},
  year    = {2026},
  note    = {arXiv preprint},
  url     = {https://github.com/priyanka25aug/llm-failure-taxonomy}
}
```

---

## Licence

MIT Licence. See `LICENSE` for details.
