import json
import os
from typing import Optional

TAXONOMY_CONTEXT = """
LLM Production Failure Taxonomy — 6 Classes:

CLASS_1_MODEL_DRIFT: Output distribution shifting over time.
  1a=upstream model update (provider silently changed model)
  1b=production distribution shift (queries drifted from training)
  1c=context window saturation

CLASS_2_INFRASTRUCTURE: Serving stack failures.
  2a=latency regression (P99/P95 SLO breach)
  2b=OOM/resource exhaustion (KV cache, memory)
  2c=routing misclassification (wrong model tier)
  2d=API breaking change (undocumented schema/contract change)

CLASS_3_INTEGRATION: Application/LLM boundary failures.
  3a=prompt injection / jailbreak
  3b=context truncation (silent input truncation)
  3c=tool-call hallucination (agent calls non-existent tool)
  3d=RAG retrieval mismatch (stale/irrelevant docs)
  3e=multi-turn corruption (false facts propagated across turns)

CLASS_4_EVALUATION: Eval framework failures.
  4a=metric gaming (Goodhart's Law, BLEU gaming)
  4b=eval contamination (test sets in training data)
  4c=production distribution gap (eval ≠ prod queries)
  4d=point vs distributional (single-point eval misses distribution)

CLASS_5_SAFETY_COMPLIANCE: Safety and regulatory failures.
  5a=PII leak (personal data exposed)
  5b=hallucinated citations (fabricated legal/academic references)
  5c=policy violation (clinical, refund, dosage violations)
  5d=auditability gap (cannot explain decision for compliance)
  5e=copyright reproduction (verbatim copyrighted content)

CLASS_6_OPERATIONAL: Operations and process failures.
  6a=monitoring blind-spot (no alert existed)
  6b=runbook absence (no documented recovery procedure)
  6c=escalation breakdown (alert routed to wrong team)
  6d=canary gap (change deployed without shadow-scoring)

Failure Budget Risk Classes:
  FC_A: Decision-critical (legal, medical, financial) — max 1/1000 requests
  FC_B: Customer-facing — max 5/1000 requests
  FC_C: Internal productivity — max 20/1000 requests
  FC_D: Experimental — max 100/1000 requests
"""

DEMO_CASES = [
    {
        "title": "Mata v. Avianca – Hallucinated Case Citations",
        "description": "Lawyer submitted legal brief with six AI-generated fictitious case citations. Court sanctioned attorneys.",
        "domain": "legal",
        "expected_class": "CLASS_5_SAFETY_COMPLIANCE",
        "expected_sub": "5b",
    },
    {
        "title": "GPT-4 Silent Behaviour Change",
        "description": "OpenAI silently updated GPT-4. Developers reported significant behavioural changes. No changelog published.",
        "domain": "general",
        "expected_class": "CLASS_1_MODEL_DRIFT",
        "expected_sub": "1a",
    },
    {
        "title": "Bing Chat Sydney Persona Jailbreak",
        "description": "Prompt injection revealed alter-ego 'Sydney'. Users extracted system prompt via adversarial inputs.",
        "domain": "general",
        "expected_class": "CLASS_3_INTEGRATION",
        "expected_sub": "3a",
    },
    {
        "title": "LLM Eval Metric Collapse – HELM Benchmark Gaming",
        "description": "Models optimising for HELM benchmark scores showed degraded real-world performance. Goodhart's Law in evaluation.",
        "domain": "general",
        "expected_class": "CLASS_4_EVALUATION",
        "expected_sub": "4a",
    },
    {
        "title": "vLLM KV Cache Exhaustion Under Bursty Load",
        "description": "PagedAttention KV cache exhausted under bursty long-context traffic. Request drops and 500 errors.",
        "domain": "enterprise_productivity",
        "expected_class": "CLASS_2_INFRASTRUCTURE",
        "expected_sub": "2b",
    },
    {
        "title": "Monitoring Blind-Spot on LLM Output Length Drift",
        "description": "LLM summarisation producing 60% shorter responses for 3 weeks. No alert existed. Discovered via support tickets.",
        "domain": "enterprise_productivity",
        "expected_class": "CLASS_6_OPERATIONAL",
        "expected_sub": "6a",
    },
]


class LLMClassifier:
    def __init__(self, model: str = "claude-haiku-4-5-20251001"):
        self.model = model
        try:
            import anthropic
            self.client = anthropic.Anthropic()
        except ImportError:
            raise ImportError("anthropic package required: pip install anthropic")

    def classify_text(self, title: str, description: str, domain: Optional[str] = None) -> dict:
        prompt = f"""{TAXONOMY_CONTEXT}

Classify the following LLM failure incident. Return ONLY a JSON object with these exact fields:
- failure_class: one of CLASS_1_MODEL_DRIFT, CLASS_2_INFRASTRUCTURE, CLASS_3_INTEGRATION, CLASS_4_EVALUATION, CLASS_5_SAFETY_COMPLIANCE, CLASS_6_OPERATIONAL
- sub_class: e.g. "3a", "5b" (string, use the sub-class codes above)
- severity: one of critical, high, medium, low
- detectability: one of immediate, delayed, silent
- blast_radius: one of single_request, single_user, user_cohort, team, org_wide, public
- failure_budget_class: one of FC_A, FC_B, FC_C, FC_D
- confidence: float between 0.0 and 1.0
- primary_cause: one sentence describing the root cause
- class_reasoning: one sentence explaining why this class was chosen
- remediation_hint: one sentence describing the key remediation action

Incident:
Title: {title}
Description: {description}
Domain: {domain or 'general'}

Return only the JSON object, no other text."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if lines[-1].startswith("```") else "\n".join(lines[1:])
        return json.loads(text)


def run_demo():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY not set — skipping LLM demo")
        return

    classifier = LLMClassifier()
    correct = 0
    print(f"\n{'='*60}")
    print("LLM Classifier Demo — 6 cases")
    print(f"{'='*60}\n")

    for case in DEMO_CASES:
        result = classifier.classify_text(case["title"], case["description"], case.get("domain"))
        got_class = result.get("failure_class", "")
        got_sub = result.get("sub_class", "")
        match = got_class == case["expected_class"]
        if match:
            correct += 1
        status = "PASS" if match else "FAIL"
        print(f"[{status}] {case['title'][:50]}")
        print(f"      Expected: {case['expected_class']} / {case['expected_sub']}")
        print(f"      Got:      {got_class} / {got_sub}  (confidence={result.get('confidence', 0):.2f})")
        print(f"      Cause:    {result.get('primary_cause', '')}")
        print()

    print(f"Accuracy: {correct}/{len(DEMO_CASES)} ({100*correct//len(DEMO_CASES)}%)")


if __name__ == "__main__":
    run_demo()
