import re
from typing import Dict, List, Optional, Tuple
from .models import (
    ClassificationResult, FailureClass, FailureBudgetClass,
    Severity, Detectability, BlastRadius, FailureRecord
)

# (pattern, weight) pairs per class
_CLASS_SIGNALS: Dict[str, List[Tuple[str, float]]] = {
    "CLASS_1_MODEL_DRIFT": [
        (r"upstream model update", 3.0),
        (r"(production|training) distribut\w+ (drift|shift)", 3.0),
        (r"out.of.distribution", 2.5),
        (r"silently updated (gpt|model|llm)", 2.5),
        (r"model (drift|degradat\w+)", 2.5),
        (r"behaviour (chang\w+|differ\w+) (without|after) (notice|update)", 2.0),
        (r"no changelog", 2.0),
        (r"distributional (drift|shift)", 2.5),
        (r"(intent|query) distribut\w+ (shift|drift|chang\w+)", 2.5),
        (r"new (intent|category|class) not (in|represent\w+) (train|eval)", 2.0),
        (r"factual error.*(model|output)", 1.5),
        (r"hallucin\w+.*(factual|scientific|domain)", 1.5),
        (r"confabulat\w+ (financial|figure\w*)", 2.0),
        (r"training (distribut\w+|data).*(drift|shift|mismatch)", 2.0),
    ],
    "CLASS_2_INFRASTRUCTURE": [
        (r"p99 latency", 3.0),
        (r"(kv.cache) exhaust\w+", 3.0),
        (r"oom|out.of.memory", 2.5),
        (r"routing (misclassif\w+)", 2.5),
        (r"api breaking change", 3.0),
        (r"latency (regression|spike|breach|slo)", 2.5),
        (r"(infrastructure|serving) (overload|failure|outage)", 2.5),
        (r"resource exhaust\w+", 2.5),
        (r"cold.start (latency|spike)", 2.5),
        (r"kv.cache (exhaust|full|overflow)", 3.0),
        (r"request drop\w*.*500 error", 2.0),
        (r"dimensionality change", 2.0),
        (r"(embedding|api) (schema|dimension\w*) change", 2.5),
        (r"multi.model rout\w+.*(wrong|misclassif\w+)", 2.0),
        (r"traffic surge.*(overload|overwhelm)", 2.0),
    ],
    "CLASS_3_INTEGRATION": [
        (r"prompt injection", 3.0),
        (r"jailbreak", 2.5),
        (r"tool.call hallucin\w+", 3.0),
        (r"rag.*(mismatch|stale)", 2.5),
        (r"stale (vector|embed\w+|index)", 2.5),
        (r"context (truncat\w+|overflow)", 2.5),
        (r"system prompt (leak\w*|extract\w*|bypass\w*)", 2.5),
        (r"adversarial input\w*", 2.0),
        (r"infinite (tool.call|loop)", 2.5),
        (r"hallucin\w+ (tool|function) name", 2.5),
        (r"(vector store|retrieval).*(stale|outdated|refresh)", 2.5),
        (r"multi.turn (corrupt\w+|state|context)", 2.5),
        (r"(silent\w*)? truncat\w+.*(context|window|input)", 2.0),
        (r"data exfiltrat\w+", 2.5),
        (r"role.play (framing|bypass)", 2.0),
    ],
    "CLASS_4_EVALUATION": [
        (r"metric (gaming|collapse)", 3.0),
        (r"benchmark gaming", 3.0),
        (r"goodhart", 2.5),
        (r"(eval|test) set contamin\w+", 3.0),
        (r"benchmark (contamin\w+|gaming|inflat\w+)", 3.0),
        (r"bleu (score|metric).*(gaming|overfit)", 2.5),
        (r"eval (gap|mismatch|distribut\w+)", 2.5),
        (r"production (distribut\w+|query) gap", 2.0),
        (r"(benchmark|eval).*(score\w*|metric\w*).*(inflat\w+|overfit\w+|gaming)", 2.5),
        (r"pre.training (corpus|data).*(benchmark|test set)", 2.0),
        (r"real.world (task|performance).*(vs|differ\w+).*(benchmark|eval)", 2.0),
        (r"point.vs.distributional", 2.0),
        (r"mmlu.*(train\w+|contamin\w+)", 2.5),
    ],
    "CLASS_5_SAFETY_COMPLIANCE": [
        (r"pii (leak\w*|exfiltrat\w+)", 3.0),
        (r"(personal|sensitive|proprietary) data (leak\w*|stored|expos\w+)", 3.0),
        (r"hallucin\w+ (citation\w+|case\w+|statute\w+)", 3.0),
        (r"gdpr|fca|hipaa|ftc", 3.0),
        (r"right to erasu\w+", 3.0),
        (r"fictitious (case|citation\w+|statute\w+)", 3.0),
        (r"copyright (infring\w+|reproduct\w+|violat\w+)", 2.5),
        (r"(verbatim|near.verbatim) reproduct\w+", 2.5),
        (r"(policy|clinical guideline\w*) violat\w+", 2.5),
        (r"racial bias|demographic bias|disparate impact", 2.5),
        (r"(audit|explainabilit\w+) (gap|absent|missing)", 2.5),
        (r"cannot (explain|audit|comply) (individual|decision)", 2.5),
        (r"wrongful (prosecut\w+|convict\w+)", 2.5),
        (r"regulat\w+ (non.complian\w+|violat\w+|scrutin\w+)", 2.0),
        (r"cross.user (contamin\w+|expos\w+)", 2.5),
    ],
    "CLASS_6_OPERATIONAL": [
        (r"monitoring (blind.?spot|gap)", 3.0),
        (r"no (alert\w*|monitoring alert)", 2.5),
        (r"only.*(after|via).*(complaint\w+|support ticket)", 2.5),
        (r"runbook (absent|miss\w+|no)", 3.0),
        (r"no (rollback|runbook|documented) (procedure|process|runbook)", 3.0),
        (r"escalation (routing|breakdown|wrong team)", 2.5),
        (r"alert\w* routed to wrong (team|queue)", 2.5),
        (r"canary (gap|skip\w+|absent|not run)", 2.5),
        (r"(shadow.scor\w+|canary) (not|without|skip\w+)", 2.5),
        (r"slo (breach|violat\w+).*(not alert\w+|weekend|miss\w+)", 2.5),
        (r"on.call (could not|unable).*(find|locate|rollback)", 2.0),
        (r"degradat\w+.*(user complaint\w+|support ticket\w+)", 2.0),
        (r"no (p95|p99|output length) monitor\w+", 2.5),
        (r"weekday.only (alert\w+|schedule)", 2.5),
    ],
}

_SEVERITY_SIGNALS: List[Tuple[str, Severity, float]] = [
    (r"critical|wrongful prosecut\w+|\$[0-9]+[bm] (market cap|loss)", Severity.CRITICAL, 2.0),
    (r"court sanction\w*|class.action|ftc action", Severity.CRITICAL, 2.0),
    (r"700\+ (wrongful|prosecut\w+)", Severity.CRITICAL, 2.5),
    (r"(incorrect|wrong) (dosage|medication)", Severity.CRITICAL, 2.5),
    (r"(high|significant) severity|major (outage|breach)", Severity.HIGH, 1.5),
    (r"p99 latency (regression|breach).{0,30}40%", Severity.HIGH, 1.5),
    (r"medium severity|moderate impact", Severity.MEDIUM, 1.5),
    (r"low severity|minor impact", Severity.LOW, 1.5),
]

_DETECTABILITY_SIGNALS: List[Tuple[str, Detectability, float]] = [
    (r"silent(ly)?|no alert|undetected|blind.spot|not (detected|caught|noticed)", Detectability.SILENT, 2.0),
    (r"only (caught|found|discovered).*(complaint|audit|quarterly|monthly|review)", Detectability.SILENT, 2.5),
    (r"(immediate|instant\w*|within (seconds|minutes))", Detectability.IMMEDIATE, 2.0),
    (r"(delayed|after|days? later|weeks? later|hours? later)", Detectability.DELAYED, 1.5),
    (r"caught.*(after|via) (user complaint|support|ticket)", Detectability.DELAYED, 2.0),
]

_BLAST_RADIUS_SIGNALS: List[Tuple[str, BlastRadius, float]] = [
    (r"(all|global|public|every) (user\w*|tier\w*|customer\w*)", BlastRadius.PUBLIC, 2.0),
    (r"org.wide|organisation.wide|entire (company|firm|organisation)", BlastRadius.ORG_WIDE, 2.0),
    (r"(team|department|squad)", BlastRadius.TEAM, 1.5),
    (r"(cohort|subset|percentage) of user\w*|user_cohort", BlastRadius.USER_COHORT, 1.5),
    (r"single user|one customer|a (grieving|specific) customer", BlastRadius.SINGLE_USER, 2.0),
    (r"single request|one request", BlastRadius.SINGLE_REQUEST, 2.0),
]

_BUDGET_CLASS_SIGNALS: List[Tuple[str, FailureBudgetClass, float]] = [
    (r"legal (brief|court|sanction)|court (order|ruling|sanction)", FailureBudgetClass.FC_A, 3.0),
    (r"clinical|medical|dosage|healthcare|gdpr|right to erasu\w+", FailureBudgetClass.FC_A, 3.0),
    (r"(financial|trading|portfolio) (decision\w*|order\w*|rebalanc\w+)", FailureBudgetClass.FC_A, 3.0),
    (r"auditabilit\w+ (gap|absent)|cannot (explain|audit)", FailureBudgetClass.FC_A, 2.5),
    (r"regulatory (non.complian\w+|filing|order)", FailureBudgetClass.FC_A, 2.5),
    (r"escalat\w+ (routing|breakdown).*(compliance|regulatory)", FailureBudgetClass.FC_A, 2.5),
    (r"(stale|outdated).*(regulatory|compliance).*(doc\w*|guideline\w*)", FailureBudgetClass.FC_A, 3.0),
    (r"Basel (II|III|IV)|capital requirement\w*|prudential", FailureBudgetClass.FC_A, 3.0),
    (r"financial.*(regulatory|compliance).*(doc\w*|corpus|guideline\w*)", FailureBudgetClass.FC_A, 2.5),
    (r"(customer.facing|end.user|chatbot|user.visible) (error|failure|output)", FailureBudgetClass.FC_B, 2.0),
    (r"(pii|personal data).*(wrong user|expos\w+|leak\w+)", FailureBudgetClass.FC_B, 2.0),
    (r"(latency|outage|slo breach).*(user\w*|customer\w*)", FailureBudgetClass.FC_B, 1.5),
    (r"(internal|developer|eng\w*) (tool|productivity|workflow)", FailureBudgetClass.FC_C, 2.0),
    (r"benchmark (gaming|contamin\w+|inflat\w+)", FailureBudgetClass.FC_C, 2.0),
    (r"monitoring (blind.?spot|gap).*(internal|operational)", FailureBudgetClass.FC_C, 1.5),
    (r"experimental|research (prototype|paper|study)", FailureBudgetClass.FC_D, 2.0),
]

_SUB_CLASS_MAP = {
    "CLASS_1_MODEL_DRIFT": {
        "1a": [r"upstream model update", r"silently updated", r"no changelog", r"provider updated model"],
        "1b": [r"(production|training) distribut\w+ (drift|shift)", r"out.of.distribution", r"distributional (drift|shift)", r"new (intent|category) not (in|represent\w+) train"],
        "1c": [r"context window (saturat\w+|exhaust\w+|full)", r"context (overflow|length)"],
    },
    "CLASS_2_INFRASTRUCTURE": {
        "2a": [r"p99 latency", r"latency (regression|spike)", r"cold.start latency"],
        "2b": [r"kv.cache exhaust\w+", r"oom|out.of.memory", r"resource exhaust\w+", r"request drop\w*.*500"],
        "2c": [r"routing misclassif\w+", r"multi.model rout\w+.*(wrong|misclassif\w+)"],
        "2d": [r"api breaking change", r"dimensionality change", r"embedding.*(schema|dimension\w*) change"],
    },
    "CLASS_3_INTEGRATION": {
        "3a": [r"prompt injection", r"jailbreak", r"system prompt (leak|extract|bypass)", r"role.play (framing|bypass)", r"adversarial input"],
        "3b": [r"context (truncat\w+|overflow)", r"(silent\w*)? truncat\w+.*(context|window)"],
        "3c": [r"tool.call hallucin\w+", r"infinite (tool.call|loop)", r"hallucin\w+ (tool|function) name"],
        "3d": [r"rag.*(mismatch|stale)", r"stale (vector|embed\w+|index)", r"(vector store|retrieval).*(stale|outdated|refresh)", r"retrieval.*(failure|mismatch)"],
        "3e": [r"multi.turn (corrupt\w+|state|context)", r"turn.level"],
    },
    "CLASS_4_EVALUATION": {
        "4a": [r"metric (gaming|collapse)", r"benchmark gaming", r"goodhart", r"bleu.*(gaming|overfit)"],
        "4b": [r"(eval|test) set contamin\w+", r"benchmark contamin\w+", r"mmlu.*(train\w+|contamin\w+)", r"pre.training.*(benchmark|test set)"],
        "4c": [r"eval (gap|distribut\w+ gap|mismatch)", r"production (distribut\w+|query) gap"],
        "4d": [r"point.vs.distributional", r"distributional failure"],
    },
    "CLASS_5_SAFETY_COMPLIANCE": {
        "5a": [r"pii (leak|exfiltrat\w+)", r"(personal|sensitive) data (leak\w*|expos\w+)", r"cross.user (contamin\w+|expos\w+)"],
        "5b": [r"hallucin\w+ (citation\w+|case\w+|statute\w+)", r"fictitious (case|citation\w+|statute\w+)"],
        "5c": [r"(policy|clinical guideline\w*) violat\w+", r"racial bias|demographic bias", r"(incorrect|wrong) (dosage|medication)"],
        "5d": [r"(audit|explainabilit\w+) (gap|absent)", r"right to erasu\w+", r"gdpr.*(erasure|complian\w+)", r"cannot (explain|audit)"],
        "5e": [r"copyright (infring\w+|reproduct\w+)", r"(verbatim|near.verbatim) reproduct\w+"],
    },
    "CLASS_6_OPERATIONAL": {
        "6a": [r"monitoring (blind.?spot|gap)", r"no (alert\w*|monitoring)", r"only.*(complaint|support ticket)", r"no (p95|p99|output) monitor\w+"],
        "6b": [r"runbook (absent|miss\w+|no)", r"no (rollback|documented) (procedure|runbook)", r"on.call.*(could not|unable).*(find|rollback)"],
        "6c": [r"escalation (routing|breakdown|wrong team)", r"alert\w* routed to wrong"],
        "6d": [r"canary (gap|skip\w+|absent)", r"(shadow.scor\w+|canary) (not|without|skip\w+)", r"without shadow.scor\w+"],
    },
}


def _score_text(text: str, signals: List[Tuple[str, float]]) -> float:
    score = 0.0
    for pattern, weight in signals:
        if re.search(pattern, text, re.IGNORECASE):
            score += weight
    return score


def _pick_sub_class(failure_class: str, text: str) -> Optional[str]:
    sub_map = _SUB_CLASS_MAP.get(failure_class, {})
    best_sub = None
    best_score = 0.0
    for sub_id, patterns in sub_map.items():
        score = sum(1.0 for p in patterns if re.search(p, text, re.IGNORECASE))
        if score > best_score:
            best_score = score
            best_sub = sub_id
    return best_sub


def _infer_severity(text: str) -> Severity:
    best = Severity.MEDIUM
    best_score = 0.0
    for pattern, sev, weight in _SEVERITY_SIGNALS:
        if re.search(pattern, text, re.IGNORECASE):
            if weight > best_score:
                best_score = weight
                best = sev
    return best


def _infer_detectability(text: str) -> Detectability:
    best = Detectability.DELAYED
    best_score = 0.0
    for pattern, det, weight in _DETECTABILITY_SIGNALS:
        if re.search(pattern, text, re.IGNORECASE):
            if weight > best_score:
                best_score = weight
                best = det
    return best


def _infer_blast_radius(text: str) -> BlastRadius:
    best = BlastRadius.USER_COHORT
    best_score = 0.0
    for pattern, br, weight in _BLAST_RADIUS_SIGNALS:
        if re.search(pattern, text, re.IGNORECASE):
            if weight > best_score:
                best_score = weight
                best = br
    return best


def _infer_budget_class(failure_class: str, text: str) -> FailureBudgetClass:
    scores: Dict[FailureBudgetClass, float] = {fc: 0.0 for fc in FailureBudgetClass}
    for pattern, fc, weight in _BUDGET_CLASS_SIGNALS:
        if re.search(pattern, text, re.IGNORECASE):
            scores[fc] += weight
    # CLASS_5 sub-class overrides
    if failure_class == "CLASS_5_SAFETY_COMPLIANCE":
        if re.search(r"pii|gdpr|right to erasu\w+|hallucin\w+ citation|auditabilit\w+|racial bias", text, re.IGNORECASE):
            scores[FailureBudgetClass.FC_A] += 2.0
        else:
            scores[FailureBudgetClass.FC_B] += 1.0
    # CLASS_6 operational bias toward FC_C unless compliance-routing
    if failure_class == "CLASS_6_OPERATIONAL":
        if re.search(r"compliance|regulatory|escalat\w+.*(compliance|regulat)", text, re.IGNORECASE):
            scores[FailureBudgetClass.FC_A] += 1.5
        else:
            scores[FailureBudgetClass.FC_C] += 1.0
    best = max(scores, key=lambda k: scores[k])
    if scores[best] == 0.0:
        return FailureBudgetClass.FC_C
    return best


_REMEDIATION_HINTS = {
    "CLASS_1_MODEL_DRIFT": "Pin model version; add regression eval on each upstream update; monitor output distribution metrics.",
    "CLASS_2_INFRASTRUCTURE": "Add latency SLOs with alerting; implement KV cache quotas; version API contracts; canary new deployments.",
    "CLASS_3_INTEGRATION": "Sanitise inputs; validate tool names against registry; add context overflow detection; implement RAG freshness checks.",
    "CLASS_4_EVALUATION": "Diversify eval metrics; deduplicate benchmarks from training; align eval distribution with production queries.",
    "CLASS_5_SAFETY_COMPLIANCE": "Add output guardrails; ground on verified sources; implement audit logging; enforce data governance policies.",
    "CLASS_6_OPERATIONAL": "Define runbooks for model rollback; add 24/7 alerting; document escalation paths; gate changes with shadow-scoring.",
}


class RuleBasedClassifier:
    def classify(self, record: FailureRecord) -> ClassificationResult:
        text = f"{record.title} {record.description} {record.domain}"
        return _classify_text_internal(text)

    def classify_text(self, title: str, description: str, domain: Optional[str] = None) -> ClassificationResult:
        text = f"{title} {description} {domain or ''}"
        return _classify_text_internal(text)


def _classify_text_internal(text: str) -> ClassificationResult:
    scores = {cls: _score_text(text, signals) for cls, signals in _CLASS_SIGNALS.items()}
    total = sum(scores.values()) or 1.0
    best_cls = max(scores, key=lambda k: scores[k])
    best_score = scores[best_cls]

    if best_score == 0.0:
        failure_class = FailureClass.UNKNOWN
        confidence = 0.0
    else:
        failure_class = FailureClass(best_cls)
        confidence = round(min(best_score / (total * 0.6), 1.0), 3)

    sub_class = _pick_sub_class(best_cls, text) if failure_class != FailureClass.UNKNOWN else None
    severity = _infer_severity(text)
    detectability = _infer_detectability(text)
    blast_radius = _infer_blast_radius(text)
    budget_class = _infer_budget_class(best_cls, text)

    return ClassificationResult(
        failure_class=failure_class,
        sub_class=sub_class,
        severity=severity,
        detectability=detectability,
        blast_radius=blast_radius,
        failure_budget_class=budget_class,
        confidence=confidence,
        primary_cause=f"Matched {best_cls} with score {best_score:.1f}",
        class_reasoning=f"Top scores: " + ", ".join(f"{k}={v:.1f}" for k, v in sorted(scores.items(), key=lambda x: -x[1])[:3]),
        remediation_hint=_REMEDIATION_HINTS.get(best_cls, "Review failure taxonomy for remediation guidance."),
    )


def classify_text(title: str, description: str, domain: Optional[str] = None) -> ClassificationResult:
    return _classify_text_internal(f"{title} {description} {domain or ''}")
