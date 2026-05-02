from dataclasses import dataclass, field
from typing import Dict, List, Optional

BUDGET_RATES: Dict[str, float] = {
    "FC_A": 1.0,
    "FC_B": 5.0,
    "FC_C": 20.0,
    "FC_D": 100.0,
}

SEVERITY_WEIGHTS: Dict[str, float] = {
    "critical": 3.0,
    "high": 2.0,
    "medium": 1.0,
    "low": 0.5,
}


@dataclass
class FailureEvent:
    failure_class: str
    severity: str
    weight: float = field(init=False)

    def __post_init__(self):
        self.weight = SEVERITY_WEIGHTS.get(self.severity.lower(), 1.0)


@dataclass
class UseCaseConfig:
    name: str
    budget_class: str
    total_requests: int
    failure_events: List[FailureEvent] = field(default_factory=list)

    @property
    def max_failures_allowed(self) -> float:
        rate = BUDGET_RATES.get(self.budget_class, 20.0)
        return (rate / 1000.0) * self.total_requests

    @property
    def weighted_failure_count(self) -> float:
        return sum(e.weight for e in self.failure_events)

    @property
    def failure_rate_per_1000(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.weighted_failure_count / self.total_requests) * 1000.0

    @property
    def budget_utilisation_pct(self) -> float:
        max_allowed = self.max_failures_allowed
        if max_allowed == 0:
            return 100.0
        return (self.weighted_failure_count / max_allowed) * 100.0

    @property
    def is_over_budget(self) -> bool:
        return self.weighted_failure_count > self.max_failures_allowed

    @property
    def status(self) -> str:
        pct = self.budget_utilisation_pct
        if pct >= 100.0:
            return "BREACHED"
        elif pct >= 80.0:
            return "WARNING"
        elif pct >= 50.0:
            return "ELEVATED"
        return "HEALTHY"


@dataclass
class BudgetReport:
    use_cases: List[UseCaseConfig] = field(default_factory=list)

    def summary(self) -> Dict[str, object]:
        return {
            "total_use_cases": len(self.use_cases),
            "breached": [uc.name for uc in self.use_cases if uc.status == "BREACHED"],
            "warning": [uc.name for uc in self.use_cases if uc.status == "WARNING"],
            "elevated": [uc.name for uc in self.use_cases if uc.status == "ELEVATED"],
            "healthy": [uc.name for uc in self.use_cases if uc.status == "HEALTHY"],
        }

    def print_report(self) -> None:
        print(f"\n{'='*60}")
        print("FAILURE BUDGET REPORT")
        print(f"{'='*60}")
        for uc in self.use_cases:
            print(f"\nUse Case : {uc.name}")
            print(f"  Budget Class    : {uc.budget_class} (max {BUDGET_RATES[uc.budget_class]}/1000 requests)")
            print(f"  Total Requests  : {uc.total_requests:,}")
            print(f"  Max Failures    : {uc.max_failures_allowed:.1f} (weighted)")
            print(f"  Actual Failures : {uc.weighted_failure_count:.1f} (weighted)")
            print(f"  Rate / 1000     : {uc.failure_rate_per_1000:.2f}")
            print(f"  Utilisation     : {uc.budget_utilisation_pct:.1f}%")
            print(f"  Status          : {uc.status}")
        summary = self.summary()
        print(f"\n{'='*60}")
        print(f"SUMMARY: {summary['total_use_cases']} use cases | "
              f"BREACHED={len(summary['breached'])} | "
              f"WARNING={len(summary['warning'])} | "
              f"ELEVATED={len(summary['elevated'])} | "
              f"HEALTHY={len(summary['healthy'])}")
        print(f"{'='*60}\n")


class FailureBudgetCalculator:
    def __init__(self):
        self._use_cases: Dict[str, UseCaseConfig] = {}

    def create_use_case(self, name: str, budget_class: str, total_requests: int) -> UseCaseConfig:
        if budget_class not in BUDGET_RATES:
            raise ValueError(f"Unknown budget class: {budget_class}. Must be one of {list(BUDGET_RATES.keys())}")
        uc = UseCaseConfig(name=name, budget_class=budget_class, total_requests=total_requests)
        self._use_cases[name] = uc
        return uc

    def record_failure(self, use_case_name: str, failure_class: str, severity: str) -> None:
        uc = self._use_cases.get(use_case_name)
        if uc is None:
            raise KeyError(f"Use case '{use_case_name}' not found. Call create_use_case first.")
        uc.failure_events.append(FailureEvent(failure_class=failure_class, severity=severity))

    def generate_report(self) -> BudgetReport:
        return BudgetReport(use_cases=list(self._use_cases.values()))

    def check_budget(self, use_case_name: str) -> UseCaseConfig:
        uc = self._use_cases.get(use_case_name)
        if uc is None:
            raise KeyError(f"Use case '{use_case_name}' not found.")
        return uc

    @staticmethod
    def required_sample_size(budget_class: str, confidence: float = 0.95, precision: float = 0.001) -> int:
        rate = BUDGET_RATES.get(budget_class, 20.0) / 1000.0
        import math
        if confidence == 0.95:
            z = 1.96
        elif confidence == 0.99:
            z = 2.576
        else:
            z = 1.645
        n = (z ** 2 * rate * (1 - rate)) / (precision ** 2)
        return int(math.ceil(n))
