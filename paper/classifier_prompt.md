# Standalone Classification Prompt

Copy-paste this entire prompt into Claude.ai (or the API) to classify any LLM production failure.
Replace the `[PASTE TITLE HERE]` and `[PASTE DESCRIPTION HERE]` placeholders at the bottom.

---

You are an expert ML systems engineer classifying production LLM failures.

## The 6-Class LLM Production Failure Taxonomy

**CLASS_1_MODEL_DRIFT** — Failures caused by the LLM's output distribution shifting over time without model weight changes. Upstream provider silent updates, production distribution diverging from eval set, context saturation drift.
Sub-classes: 1a=upstream model update, 1b=production distribution shift, 1c=context window saturation

**CLASS_2_INFRASTRUCTURE** — Failures in the serving stack, not the model itself. P99 latency spikes, OOM/KV-cache exhaustion, routing misclassification under load, API breaking changes, cold-start pathology, cascading dependency failures.
Sub-classes: 2a=latency regression, 2b=OOM/resource exhaustion, 2c=routing misclassification, 2d=API breaking change

**CLASS_3_INTEGRATION** — Failures at the boundary between LLM and the application. Prompt injection, system prompt leakage, context truncation (silent), tool-call hallucination, RAG retrieval mismatch (stale index), multi-turn state corruption.
Sub-classes: 3a=prompt injection/jailbreak, 3b=context truncation, 3c=tool-call hallucination, 3d=RAG mismatch, 3e=multi-turn corruption

**CLASS_4_EVALUATION** — Failures in the evaluation framework, not the model. Metric proxy collapse (BLEU/ROUGE gaming), eval set contamination, production distribution gap, point accuracy vs distributional measurement.
Sub-classes: 4a=metric gaming/collapse, 4b=eval contamination, 4c=production distribution gap, 4d=point vs distributional

**CLASS_5_SAFETY_COMPLIANCE** — Failures producing outputs that violate safety, regulatory, or data governance rules. PII leakage, hallucinated legal/medical citations, policy boundary violations, auditability gaps, copyright reproduction.
Sub-classes: 5a=PII leakage, 5b=hallucinated citations, 5c=policy violation, 5d=auditability gap, 5e=copyright

**CLASS_6_OPERATIONAL** — Failures in the processes and runbooks around the LLM. Monitoring blind-spots (no alert), runbook absence, escalation routing breakdown, canary/shadow test gaps. The model and infra may be fine; the ops envelope failed.
Sub-classes: 6a=monitoring blind-spot, 6b=runbook absence, 6c=escalation breakdown, 6d=canary gap

## Failure Budget Risk Classes
- FC_A = Decision-Critical (credit, medical, legal decisions) — max 0.1% failure rate
- FC_B = Customer-Facing (public chatbot, product features) — max 0.5% failure rate
- FC_C = Internal Productivity (internal tools, summarisation) — max 2.0% failure rate
- FC_D = Experimental (R&D, sandbox) — max 10% failure rate

## Detectability
- **immediate**: alert fires within minutes (error rate, 500s, latency breach)
- **delayed**: caught within hours–days (user complaints, monitoring lag)
- **silent**: only discovered via audit, manual review, or external report (weeks–months)

## Blast Radius
single_request → single_user → user_cohort → team → org_wide → public

---

Classify the following production LLM failure incident.

**Title:** [PASTE TITLE HERE]

**Description:** [PASTE DESCRIPTION HERE]

**Domain (if known):** [e.g. financial_services / healthcare / legal / e_commerce / enterprise_productivity / general]

Return ONLY a valid JSON object with exactly these fields:

```json
{
  "failure_class": "<CLASS_1_MODEL_DRIFT | CLASS_2_INFRASTRUCTURE | CLASS_3_INTEGRATION | CLASS_4_EVALUATION | CLASS_5_SAFETY_COMPLIANCE | CLASS_6_OPERATIONAL>",
  "sub_class": "<e.g. 3d — or null if unclear>",
  "severity": "<critical | high | medium | low>",
  "detectability": "<immediate | delayed | silent>",
  "blast_radius": "<single_request | single_user | user_cohort | team | org_wide | public>",
  "failure_budget_class": "<FC_A | FC_B | FC_C | FC_D>",
  "confidence": 0.0,
  "primary_cause": "one sentence root cause",
  "class_reasoning": "2-3 sentences: why this class and not another",
  "remediation_hint": "one actionable sentence for the engineering team"
}
```
