import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.classifier.rule_based import RuleBasedClassifier, classify_text
from src.classifier.models import FailureClass, FailureBudgetClass, Detectability
from src.failure_budget.calculator import FailureBudgetCalculator


def run_tests():
    passed = 0
    failed = 0
    results = []

    def check(name, condition, msg=""):
        nonlocal passed, failed
        if condition:
            passed += 1
            results.append(f"  PASS  {name}")
        else:
            failed += 1
            results.append(f"  FAIL  {name}" + (f" — {msg}" if msg else ""))

    clf = RuleBasedClassifier()

    # Test 1: Mata v. Avianca → CLASS_5_SAFETY_COMPLIANCE, FC_A
    r1 = classify_text(
        "Mata v. Avianca – Hallucinated Case Citations",
        "Lawyer submitted legal brief with six AI-generated fictitious case citations. "
        "ChatGPT hallucinated authoritative citations. Court sanctioned attorneys.",
        "legal"
    )
    check(
        "T01 Mata v Avianca → CLASS_5_SAFETY_COMPLIANCE",
        r1.failure_class == FailureClass.CLASS_5_SAFETY_COMPLIANCE,
        f"got {r1.failure_class}"
    )
    check(
        "T01 Mata v Avianca → FC_A",
        r1.failure_budget_class == FailureBudgetClass.FC_A,
        f"got {r1.failure_budget_class}"
    )

    # Test 2: Bing Sydney prompt injection → CLASS_3_INTEGRATION, sub_class="3a"
    r2 = classify_text(
        "Bing Chat Sydney Persona Jailbreak",
        "Microsoft Bing Chat revealed alter-ego personality via prompt injection. "
        "Users extracted system prompt via adversarial inputs. Jailbreak successful.",
        "general"
    )
    check(
        "T02 Bing Sydney → CLASS_3_INTEGRATION",
        r2.failure_class == FailureClass.CLASS_3_INTEGRATION,
        f"got {r2.failure_class}"
    )
    check(
        "T02 Bing Sydney → sub_class 3a",
        r2.sub_class == "3a",
        f"got {r2.sub_class}"
    )

    # Test 3: GPT-4 silent model drift → CLASS_1_MODEL_DRIFT
    r3 = classify_text(
        "GPT-4 Silent Behaviour Change",
        "OpenAI silently updated GPT-4. Upstream model update without changelog. "
        "Developers reported significant behavioural changes after upstream provider updated model.",
        "general"
    )
    check(
        "T03 GPT-4 silent update → CLASS_1_MODEL_DRIFT",
        r3.failure_class == FailureClass.CLASS_1_MODEL_DRIFT,
        f"got {r3.failure_class}"
    )

    # Test 4: vLLM KV cache OOM → CLASS_2_INFRASTRUCTURE
    r4 = classify_text(
        "vLLM PagedAttention KV Cache Exhaustion Under Bursty Load",
        "KV cache exhausted under bursty long-context traffic. OOM errors. "
        "Request drops and 500 errors due to kv-cache exhaustion.",
        "enterprise_productivity"
    )
    check(
        "T04 vLLM KV cache OOM → CLASS_2_INFRASTRUCTURE",
        r4.failure_class == FailureClass.CLASS_2_INFRASTRUCTURE,
        f"got {r4.failure_class}"
    )

    # Test 5: HELM benchmark gaming → CLASS_4_EVALUATION
    r5 = classify_text(
        "LLM Eval Metric Collapse – HELM Benchmark Gaming",
        "Optimising for HELM benchmark scores led to degraded real-world performance. "
        "Goodhart's Law in evaluation. Metric gaming caused metric collapse.",
        "general"
    )
    check(
        "T05 HELM benchmark gaming → CLASS_4_EVALUATION",
        r5.failure_class == FailureClass.CLASS_4_EVALUATION,
        f"got {r5.failure_class}"
    )

    # Test 6: Monitoring blind-spot → CLASS_6_OPERATIONAL, detectability=silent
    r6 = classify_text(
        "Monitoring Blind-Spot on LLM Output Length Drift",
        "No alert existed for output length distribution. Degradation only caught via user support tickets. "
        "Monitoring blind-spot. No p95/p99 output length monitoring.",
        "enterprise_productivity"
    )
    check(
        "T06 Monitoring blind-spot → CLASS_6_OPERATIONAL",
        r6.failure_class == FailureClass.CLASS_6_OPERATIONAL,
        f"got {r6.failure_class}"
    )
    check(
        "T06 Monitoring blind-spot → detectability=silent",
        r6.detectability == Detectability.SILENT,
        f"got {r6.detectability}"
    )

    # Test 7: Samsung PII leak → CLASS_5_SAFETY_COMPLIANCE, FC_A
    r7 = classify_text(
        "Samsung Employee PII Leak via ChatGPT",
        "Samsung engineers pasted proprietary chip design source code into ChatGPT. "
        "Sensitive data leaked and stored by OpenAI. PII leak. Personal data stored externally.",
        "financial_services"
    )
    check(
        "T07 Samsung PII leak → CLASS_5_SAFETY_COMPLIANCE",
        r7.failure_class == FailureClass.CLASS_5_SAFETY_COMPLIANCE,
        f"got {r7.failure_class}"
    )
    check(
        "T07 Samsung PII leak → FC_A",
        r7.failure_budget_class == FailureBudgetClass.FC_A,
        f"got {r7.failure_budget_class}"
    )

    # Test 8: RAG stale regulatory docs (financial_services) → CLASS_3_INTEGRATION, sub_class="3d", FC_A
    r8 = classify_text(
        "Production RAG Retriever Returning Stale Regulatory Docs",
        "RAG retrieval mismatch. Stale vector index not refreshed after regulatory corpus update. "
        "Vector store returning outdated Basel II documents instead of Basel III. "
        "No freshness metadata in retrieval pipeline.",
        "financial_services"
    )
    check(
        "T08 RAG stale docs → CLASS_3_INTEGRATION",
        r8.failure_class == FailureClass.CLASS_3_INTEGRATION,
        f"got {r8.failure_class}"
    )
    check(
        "T08 RAG stale docs → sub_class 3d",
        r8.sub_class == "3d",
        f"got {r8.sub_class}"
    )
    check(
        "T08 RAG stale docs (financial_services regulatory) → FC_A",
        r8.failure_budget_class == FailureBudgetClass.FC_A,
        f"got {r8.failure_budget_class}"
    )

    # Test 9: Failure budget FC_A 100k + 50 high-severity = 100 weighted = 100% utilisation = BREACHED
    calc9 = FailureBudgetCalculator()
    uc9 = calc9.create_use_case("legal-advisor", "FC_A", 100_000)
    for _ in range(50):
        calc9.record_failure("legal-advisor", "CLASS_5_SAFETY_COMPLIANCE", "high")
    check(
        "T09 FC_A 100k requests + 50 high → 100 weighted failures",
        abs(uc9.weighted_failure_count - 100.0) < 0.01,
        f"got {uc9.weighted_failure_count}"
    )
    check(
        "T09 FC_A utilisation = 100% → BREACHED",
        uc9.status == "BREACHED",
        f"got status={uc9.status}, util={uc9.budget_utilisation_pct:.1f}%"
    )

    # Test 10: FC_C 10k + 10 medium = 10 weighted, max=200, 5% = HEALTHY
    calc10 = FailureBudgetCalculator()
    uc10 = calc10.create_use_case("internal-qa", "FC_C", 10_000)
    for _ in range(10):
        calc10.record_failure("internal-qa", "CLASS_6_OPERATIONAL", "medium")
    check(
        "T10 FC_C 10k + 10 medium → HEALTHY",
        uc10.status == "HEALTHY",
        f"got status={uc10.status}, util={uc10.budget_utilisation_pct:.1f}%"
    )
    check(
        "T10 FC_C utilisation ≈ 5%",
        abs(uc10.budget_utilisation_pct - 5.0) < 0.5,
        f"got {uc10.budget_utilisation_pct:.2f}%"
    )

    # Test 11: Confidence scores between 0 and 1 for 3 different cases
    cases_11 = [
        ("Hallucinated citations in legal brief", "Attorney submitted fictitious case citations. Hallucinated authoritative citations.", "legal"),
        ("P99 latency regression after model update", "Latency SLO breach. P99 latency increased 40% after LLM model update.", "general"),
        ("Benchmark gaming inflated scores", "BLEU metric gaming. Models overfit to n-gram overlap. Benchmark contamination.", "general"),
    ]
    for title, desc, domain in cases_11:
        r = classify_text(title, desc, domain)
        check(
            f"T11 confidence in [0,1] for '{title[:30]}...'",
            0.0 <= r.confidence <= 1.0,
            f"got confidence={r.confidence}"
        )

    print(f"\n{'='*60}")
    print("TEST RESULTS")
    print(f"{'='*60}")
    for line in results:
        print(line)
    print(f"{'='*60}")
    print(f"Passed: {passed} / {passed + failed}")
    print(f"{'='*60}\n")
    return failed


if __name__ == "__main__":
    failures = run_tests()
    sys.exit(0 if failures == 0 else 1)
