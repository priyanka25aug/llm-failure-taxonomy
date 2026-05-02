# Beyond Hallucination: A System-Level Failure Taxonomy for Production LLMs

**Author:** Priyanka Bajaj  
**Target venue:** arXiv cs.LG → MLSys 2026 / ACM SysML  
**Target length:** 10–12 pages (conference format)  
**Status:** Outline — draft in progress

---

## Abstract (draft)

Large language models are increasingly deployed in production systems serving millions of users across regulated, high-stakes domains. Existing failure analysis focuses predominantly on model-level errors — hallucination rates, factuality benchmarks, and safety refusal classification. This framing, while necessary, is insufficient for production engineers who must reason about system reliability across the full deployment stack.

We present the first system-level failure taxonomy for production LLM deployments, comprising six classes: Model Drift, Infrastructure, Integration, Evaluation, Safety & Compliance, and Operational. Unlike model-centric taxonomies, our classification scheme captures failures that originate outside the model weights — in serving infrastructure, RAG retrieval pipelines, evaluation frameworks, and operational processes — and classifies them by their detectability profile and blast radius.

We validate the taxonomy against 50 real-world production incidents drawn from court documents, regulatory filings, academic papers, and public postmortems. Key findings: 50% of incidents were *silent* (no immediate alert; detected via audit or user complaint); Safety & Compliance and Integration failures each account for 26% of incidents; and Infrastructure failures, while less frequent, show the shortest mean time to detection.

We further introduce a *per-use-case failure budget framework* — a formal model for assigning acceptable failure rates by use case risk class (Decision-Critical, Customer-Facing, Internal Productivity, Experimental) rather than by model accuracy. This reframing shifts engineering teams from debating "which model is best" to reasoning about acceptable risk envelopes per workflow — a change with measurable operational consequences in regulated deployment contexts.

All data, code, and the taxonomy schema are released at: https://github.com/priyanka25aug/llm-failure-taxonomy

---

## 1. Introduction (target: ~1.5 pages)

**Opening hook:** The courtroom. Cite Mata v. Avianca (2023) — a lawyer submitting hallucinated case citations is a model failure. But Air Canada's chatbot stating incorrect refund policy (2024) is an integration failure. The UK Post Office Horizon system convicting 700+ postmasters is an operational failure. All three are LLM-adjacent production failures. Only the first looks like "hallucination."

**Gap statement:**  
- Existing failure taxonomies for ML systems (Sculley et al. 2015, Amershi et al. 2019) predate modern LLM deployments and don't capture LLM-specific failure modes
- LLM-specific work (hallucination surveys, jailbreak papers, alignment failure analyses) focuses exclusively on model-layer failures
- No structured, system-level classification exists for practitioners operating LLMs in production

**Contributions (enumerate clearly):**
1. A 6-class system-level failure taxonomy with sub-classes, detectability profiles, and blast radius characterisation
2. A labeled dataset of 50 real-world incidents with full provenance
3. A per-use-case failure budget framework formalising acceptable failure rates by risk class
4. A reference rule-based classifier for automated incident triage

**Paper roadmap:** one sentence per section.

---

## 2. Related Work (target: ~1 page)

**2.1 ML System Reliability**  
- Sculley et al. (2015) "Hidden Technical Debt in ML Systems" — foundational but pre-LLM  
- Amershi et al. (2019) "Software Engineering for Machine Learning" — process failures but model-agnostic  
- Paleyes et al. (2022) "Challenges in Deploying ML" — deployment taxonomy but pre-LLM

**2.2 LLM Failure Analysis**  
- Hallucination surveys (Ji et al. 2023, Huang et al. 2023) — model-layer only  
- Jailbreak/adversarial input literature (Wei et al. 2023, Perez & Ribeiro 2022) — CLASS_3 sub-class only  
- Safety alignment failures (Bai et al. 2022) — CLASS_5 sub-class only  
- Evaluation critique literature (Bowman et al. 2021, Liang et al. 2022 HELM) — CLASS_4 only

**2.3 AI Incident Databases**  
- AI Incident Database (McGregor 2021) — incident collection without structured taxonomy  
- AIAAIC — similar; narrative not structural  
- This work: first structured, layered taxonomy with formal failure budget framework

**Gap summary table:** 2×5 table mapping existing work to our 6 classes — showing no prior work covers all 6.

---

## 3. Taxonomy Framework (target: ~1.5 pages)

**3.1 Design Principles**  
Four principles guiding the taxonomy design:  
1. *Layer-specificity* — each class maps to a distinct system layer (model / infra / integration / eval / governance / ops)  
2. *Actionability* — each class implies a distinct remediation path and owning team  
3. *Detectability as first-class attribute* — not just what fails, but when and how it becomes observable  
4. *Blast radius* — scope of user/system impact as a classification attribute, not an afterthought

**3.2 Classification Dimensions**  
- Failure class (6 classes)  
- Sub-class (3–5 per class)  
- Severity (critical / high / medium / low)  
- Detectability (immediate / delayed / silent)  
- Blast radius (single_request → single_user → user_cohort → team → org_wide → public)  
- Mean time to detection (MTTD) range  
- Failure budget risk class (FC_A through FC_D)

**3.3 Comparison to Model-Centric Framing**  
Table: "Hallucination" as classified by our taxonomy — it appears in CLASS_1 (drift), CLASS_3 (RAG mismatch), CLASS_5 (high-stakes domain hallucination). Same observable symptom, three different root causes, three different remediation paths.

---

## 4. The Six Failure Classes (target: ~3 pages)

One subsection per class. Each follows a fixed structure:
- Definition (2–3 sentences)  
- Sub-classes (bullet list)  
- Key indicators (what to monitor)  
- Representative incident (anonymised or public)  
- Detectability profile  
- Failure budget applicability

**4.1 CLASS_1 — Model Drift Failures**  
Representative: GPT-4 silent behaviour change (March 2023) — upstream model update causing silent output distribution shift, detected 168h later via developer forum reports.

**4.2 CLASS_2 — Infrastructure Failures**  
Representative: vLLM PagedAttention KV cache exhaustion — bursty long-context traffic exhausting shared GPU memory, 500 errors, immediate detection but 3h MTTR.

**4.3 CLASS_3 — Integration Failures**  
Representative: Bing Chat Sydney (2023) — prompt injection via adversarial input extracting system prompt and enabling persona escape. Sub-class 3a.

**4.4 CLASS_4 — Evaluation Failures**  
Representative: HELM benchmark gaming — models optimising for benchmark proxy metrics showing degraded real-world user value. Silent failure class; MTTD measured in months.

**4.5 CLASS_5 — Safety & Compliance Failures**  
Representative: Mata v. Avianca (2023) — LLM hallucinating legal citations submitted to federal court. Sub-class 5b. FC_A use case with no verification guardrail.

**4.6 CLASS_6 — Operational Failures**  
Representative: (Anonymised composite) — LLM output-length drift unmonitored for 3 weeks; detected via support ticket backlog review. No alert existed for output distribution shift.

---

## 5. The Failure Budget Framework (target: ~2 pages)

**5.1 Motivation: Why Per-Model Accuracy is the Wrong Unit**  
Current practice: teams negotiate "which model achieves X% on Y benchmark."  
Problem: two use cases running on the *same model* can have radically different acceptable failure tolerances. A credit decisioning path and an internal summarisation tool are not equivalent — they should not share a failure budget.

**5.2 Formal Definition**  
Define: failure budget B(u) for use case u as the maximum acceptable weighted failure rate per 1,000 requests, where failures are weighted by severity.

B(u) = f(risk_class(u)) where risk_class ∈ {FC_A, FC_B, FC_C, FC_D}

Budget utilisation: U(u, t) = observed_weighted_failures(u, t) / B(u) × 100%

Status thresholds: HEALTHY (<50%), ELEVATED (50–80%), WARNING (80–100%), BREACHED (>100%)

**5.3 Risk Class Calibration**  
Table: risk class → max failure rate → required monitoring classes → example use cases  
Calibration methodology: drawn from regulated deployment practice in financial services (DORA, FCA Consumer Duty, Basel model risk framework) and healthcare (FDA SaMD guidance)

**5.4 Implementation Considerations**  
- Failure budget class assignment must precede model selection — it is a business/legal decision, not a technical one  
- Failure events should be weighted by severity (critical=3x, high=2x, medium=1x, low=0.5x)  
- Budget should be reviewed per sprint cycle; breaches trigger incident review, not just monitoring alerts  
- Budget does not replace model-level metrics — it sits above them as a system-level SLO

**5.5 Illustrative Example**  
Walk through the calculator output for a bank running three use cases (credit decisioning FC_A, customer chatbot FC_B, internal search FC_C) with different failure event histories. Show the budget utilisation report.

---

## 6. Dataset and Validation (target: ~1.5 pages)

**6.1 Dataset Construction**  
- 50 incidents; 36 from public sources, 14 synthetic composites  
- Sources: court documents, regulatory filings, academic papers, company postmortems, public news  
- Labeling: single annotator (author); sub-class, severity, detectability, blast radius, MTTD/MTTR  
- Availability: full dataset at repository URL with source citations

**6.2 Dataset Statistics**  
- Class distribution: CLASS_5 (26%) and CLASS_3 (26%) dominate — safety/compliance and integration are the most-reported public failure classes  
- 50% of incidents are *silent* — the largest single finding; motivates monitoring design recommendations  
- 36% are *critical* severity; 60% *high*  
- MTTD ranges: CLASS_2 (0.1–8h) vs CLASS_4 (months) — six orders of magnitude difference  
- Domain: financial services (22%) and enterprise productivity (24%) dominate

**6.3 Classifier Validation**  
- Rule-based classifier evaluated against 50 labeled incidents  
- Report precision/recall per class  
- Confusion matrix — highlight CLASS_1/CLASS_4 confusion (both can appear as "silent quality degradation")  
- Note: rule-based is a reference implementation; LLM-based classification reported separately

**6.4 Limitations**  
- Dataset skewed toward publicly reported incidents — severe failures are over-represented  
- Single annotator; inter-rater reliability study planned  
- Synthetic incidents not used in empirical frequency claims

---

## 7. Discussion (target: ~1 page)

**7.1 The Silent Majority**  
50% of failures are silent. This has a direct architectural implication: monitoring systems built around alert-on-error are insufficient for production LLM systems. Distributional monitoring (output length, token distribution, semantic drift) must complement error-rate monitoring.

**7.2 Safety & Compliance Is Not a Model Problem**  
CLASS_5 accounts for 26% of incidents but spans model memorisation (5a), hallucinated citations (5b), policy boundary violation (5c), auditability gaps (5d), and copyright (5e). The shared property is not model behaviour — it is the *absence of a verification layer* between model output and consequential action. Taxonomy enables targeted remediation: each sub-class implies a distinct control.

**7.3 Evaluation Failure Is Underreported**  
CLASS_4 is 10% of incidents — likely an undercount. Evaluation failures are meta-failures (the signal that would catch other failures is itself broken) and rarely surface as reportable incidents. Dedicated evaluation infrastructure is a first-class engineering concern.

**7.4 Failure Budget as Org Design Tool**  
The failure budget framework is not just a monitoring concept — it is a forcing function for cross-team alignment. Assigning a use case to FC_A requires legal, compliance, ML, and product to agree on acceptable risk before a single model is selected. This conversation rarely happens today.

---

## 8. Conclusion (target: ~0.5 pages)

- Restate the gap, the contribution, the key finding (silent failures, layer specificity)
- Call to action: adopt system-level failure thinking in LLM deployments
- Open problems: inter-rater reliability study, LLM-based classifier, domain-specific budget calibration, temporal analysis (are failure patterns changing as the industry matures?)
- Repository and dataset released for community extension

---

## References (target: 25–35 citations)

Key references to include:
- Sculley et al. (2015) NIPS — Hidden Technical Debt
- Amershi et al. (2019) ICSE — SE for ML
- Paleyes et al. (2022) — Challenges in Deploying ML
- Ji et al. (2023) — Survey of Hallucination in NLG
- Huang et al. (2023) — Survey of LLM Hallucination
- Wei et al. (2023) — Jailbroken: How does LLM safety training fail
- Liang et al. (2022) — HELM
- McGregor (2021) — AI Incident Database
- Shankar et al. (2020) — Evaluating Machine Learning Systems
- Ribeiro et al. (2020) — CheckList (evaluation blind spots)
- Bommasani et al. (2021) — Foundation Models
- Weidinger et al. (2021) — DeepMind taxonomy (partial overlap; distinguish)
- Bender et al. (2021) — Stochastic Parrots
- Court documents: Mata v. Avianca, NYT v. OpenAI
- Regulatory: FCA Consumer Duty LLM Review 2024, EU AI Act 2024, DORA

---

## Appendix A — Full Taxonomy Schema

Reproduce `taxonomy/taxonomy.yaml` in formatted table form.

## Appendix B — Dataset Sample

10 representative incidents (2 per class) with full label set.

## Appendix C — Failure Budget Calculator Implementation

Key pseudocode from `src/failure_budget/calculator.py`.

---

## Writing Schedule

| Week | Task |
|------|------|
| Week 1 | Draft Sections 1–2 (intro + related work) |
| Week 2 | Draft Sections 3–4 (taxonomy framework + 6 classes) |
| Week 3 | Draft Sections 5–6 (failure budget + dataset validation) |
| Week 4 | Draft Sections 7–8 (discussion + conclusion) |
| Week 5 | References, figures, appendices |
| Week 6 | Internal review + revision |
| Week 7 | arXiv submission |
| Week 8–12 | MLSys / SysML submission preparation |
