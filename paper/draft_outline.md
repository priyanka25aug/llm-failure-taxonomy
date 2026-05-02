# Beyond Hallucination: A System-Level Failure Taxonomy for Production LLMs

**Author:** Priyanka Bajaj
**Target venues:** arXiv cs.LG / cs.SE · MLSys 2026
**Submission deadline:** October 2025 (MLSys) / rolling (arXiv)

---

## Abstract (draft)

Large language models deployed in production fail in ways that extend far beyond factual hallucination. We present a six-class system-level taxonomy — Model Drift, Infrastructure, Integration, Evaluation, Safety & Compliance, and Operational — grounded in 50 labeled real-world incidents drawn from court documents, regulatory filings, academic papers, and engineering postmortems. For each class we define sub-classes, failure budget risk tiers (FC-A through FC-D), and detection/remediation patterns. We validate the taxonomy using a rule-based classifier (11/11 unit tests) and a Claude API-powered classifier, and demonstrate that the majority of production failures (>60%) are *silent* — undetectable without purpose-built observability. We further introduce a per-use-case failure budget model that translates taxonomy class into quantitative reliability targets. The taxonomy, dataset, and tooling are released openly to support reproducible LLMOps research.

---

## Section Structure

### 1. Introduction

- Motivation: LLM failures in production are not just hallucination — they span infrastructure, evaluation, compliance, and operations
- Gap: no unified, system-level taxonomy exists; AIID (McGregor 2021) covers AI incidents broadly, not LLM-specific production failure modes
- Contributions:
  1. Six-class LLM production failure taxonomy with 22 sub-classes
  2. 50-incident labeled dataset with public provenance
  3. Failure budget risk model (FC-A → FC-D) analogous to SRE error budgets
  4. Rule-based and LLM-powered classifiers with empirical validation
- Paper roadmap

### 2. Related Work

- **ML system failures broadly:** Sculley et al. (2015) *Hidden Technical Debt in ML Systems* — identifies data dependencies, feedback loops; does not cover LLM-specific failure modes
- **SE for ML:** Amershi et al. (2019) *Software Engineering for ML Applications* — 9-stage ML workflow; we extend to LLM serving-time concerns
- **Hallucination surveys:** Ji et al. (2023) *Survey of Hallucination in NLG* — covers factual errors but not infrastructure/operational classes
- **Evaluation frameworks:** Liang et al. (2022) *HELM* — benchmark evaluation; we use HELM gaming as a CLASS_4 specimen
- **AI incident databases:** McGregor et al. (2021) *AIID* — incident reporting; broader than LLMs, lower taxonomic specificity
- **LLM security:** prompt injection literature (Greshake et al. 2023); covered in CLASS_3_INTEGRATION
- **SRE reliability:** Beyer et al. (2016) *Site Reliability Engineering* — error budget concept adapted for failure budget model

### 3. Taxonomy Framework

- Design principles: exhaustive, mutually exclusive at class level, empirically grounded, actionable
- Relationship to SRE error budgets: failure budget class ≡ SLO tier
- Taxonomy structure diagram: 6 classes × sub-classes × detectability × blast radius
- Labelling methodology: dual annotation, inter-annotator agreement (Cohen's κ)
- Limitations: classes are not always mutually exclusive at sub-class level; taxonomy v1.0

### 4. The Six Failure Classes

#### 4.1 CLASS_1: Model Drift
- Definition and detection signals
- Sub-classes: 1a (upstream update), 1b (distribution shift), 1c (context saturation)
- Case studies: GPT-4 silent update (FTX-0007), Distributional drift in banking intent classifier (FTX-0049)
- Detection: output distribution monitoring, regression evals on every upstream update
- Remediation: model version pinning, continuous eval pipelines

#### 4.2 CLASS_2: Infrastructure
- Definition and detection signals
- Sub-classes: 2a (latency), 2b (OOM/KV cache), 2c (routing), 2d (API contract)
- Case studies: vLLM KV cache exhaustion (FTX-0035), OpenAI embedding dimensionality change (FTX-0022)
- Detection: P99 latency SLOs, KV cache utilisation metrics, API contract tests
- Remediation: canary deployments, versioned API endpoints, request-level KV cache quotas

#### 4.3 CLASS_3: Integration
- Definition and detection signals
- Sub-classes: 3a (injection), 3b (truncation), 3c (tool-call hallucination), 3d (RAG mismatch), 3e (multi-turn corruption)
- Case studies: Bing Sydney jailbreak (FTX-0005), Production RAG stale regulatory docs (FTX-0030)
- Detection: input sanitisation tests, context length monitoring, tool-name validation, RAG freshness metadata
- Remediation: registered tool allowlists, vector index refresh schedules, context overflow errors

#### 4.4 CLASS_4: Evaluation
- Definition and detection signals
- Sub-classes: 4a (metric gaming), 4b (contamination), 4c (production gap), 4d (point vs distributional)
- Case studies: HELM benchmark gaming (FTX-0019), LLaMA eval contamination (FTX-0029)
- Detection: human evaluation audits, benchmark deduplication against training corpus
- Remediation: diversified eval suites, held-out production query sets, adversarial eval

#### 4.5 CLASS_5: Safety and Compliance
- Definition and detection signals
- Sub-classes: 5a (PII), 5b (citations), 5c (policy), 5d (auditability), 5e (copyright)
- Case studies: Mata v. Avianca (FTX-0001), GDPR right-to-erasure (FTX-0045), NHS triage bias (FTX-0026)
- Detection: output guardrails, citation verification, audit logging, demographic fairness metrics
- Remediation: grounding on verified sources, data lineage tracking, per-request audit trails

#### 4.6 CLASS_6: Operational
- Definition and detection signals
- Sub-classes: 6a (monitoring blind-spot), 6b (runbook absence), 6c (escalation breakdown), 6d (canary gap)
- Case studies: P99 SLO breach on weekend (FTX-0048), Prompt template regression (FTX-0038)
- Detection: by definition, detected only after failure — prevention is key
- Remediation: 24/7 alerting, documented rollback runbooks, shadow-scoring CI gates

### 5. Failure Budget Model

- Motivation: quantitative reliability targets for LLM use cases analogous to SRE error budgets
- FC-A → FC-D risk tiers: max failure rates per 1,000 requests
- Severity weighting: critical=3×, high=2×, medium=1×, low=0.5×
- Budget utilisation and status thresholds: HEALTHY / ELEVATED / WARNING / BREACHED
- Case study: FC_A legal advisor use case at 100% budget utilisation
- Worked example: FC_C internal productivity tool at 5% utilisation

### 6. Dataset Validation

- Dataset composition: 50 incidents, 6 classes, public provenance
- Source distribution: court documents (4), academic papers (14), public news (18), regulatory filings (4), company postmortems (3), synthetic (7)
- Key statistics: 50% silent detectability, 34% FC_A (decision-critical)
- Classifier validation: rule-based 11/11 tests; LLM classifier accuracy on demo cases
- Distribution analysis: 7 figures (class distribution, severity heatmap, detectability, blast radius, domain, MTTD, budget class)
- Threat to validity: selection bias toward publicly disclosed incidents; dark figure of unreported failures

### 7. Discussion

- Silent failures as the dominant risk (50% of incidents): observability gap in LLM systems
- Failure budget model as a bridge between LLMOps and SRE practice
- Taxonomy evolution: v1.0 covers known failure modes; agentic multi-step failures (CLASS_3c) will grow
- Open questions: automated taxonomy labeling at scale; cross-organization incident sharing norms
- Limitations: taxonomy is descriptive not causal; root causes require human judgment

### 8. Conclusion

- Summary of contributions
- Impact: provides LLMOps teams a structured language for failure classification, monitoring design, and reliability targeting
- Release: taxonomy, dataset, and tooling at https://github.com/priyanka25aug/llm-failure-taxonomy
- Call to action: community incident submissions to extend dataset beyond 50

---

## Key References

1. Sculley, D. et al. (2015). *Hidden Technical Debt in Machine Learning Systems*. NeurIPS.
2. Amershi, S. et al. (2019). *Software Engineering for Machine Learning: A Case Study*. ICSE-SEIP.
3. Ji, Z. et al. (2023). *Survey of Hallucination in Natural Language Generation*. ACM CSUR.
4. Liang, P. et al. (2022). *Holistic Evaluation of Language Models*. arXiv:2211.09110.
5. McGregor, S. (2021). *Preventing Repeated Real World AI Failures by Cataloging Incidents: The AI Incident Database*. AAAI.
6. Greshake, K. et al. (2023). *Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection*. AISec.
7. Beyer, B. et al. (2016). *Site Reliability Engineering*. O'Reilly.
8. Goodhart, C. (1975). *Problems of Monetary Management: The U.K. Experience*. (Goodhart's Law)

---

## 8-Week Writing Schedule

| Week | Dates | Milestone |
|------|-------|-----------|
| 1 | May 5–11 | Complete taxonomy YAML; finalize 50-incident dataset; inter-annotator agreement run |
| 2 | May 12–18 | Write Sections 1 (Introduction) and 2 (Related Work) — full draft |
| 3 | May 19–25 | Write Section 3 (Taxonomy Framework) and Section 5 (Failure Budget Model) |
| 4 | May 26–Jun 1 | Write Section 4 (Six Classes) — all 6 sub-sections with case studies |
| 5 | Jun 2–8 | Write Section 6 (Dataset Validation) and generate all figures |
| 6 | Jun 9–15 | Write Sections 7 (Discussion) and 8 (Conclusion); complete abstract |
| 7 | Jun 16–22 | Full paper revision pass; peer review from co-authors; fix classifier to match paper claims |
| 8 | Jun 23–29 | Final proofread; arXiv submission; begin MLSys 2026 formatting |
