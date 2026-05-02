from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any


class FailureClass(Enum):
    CLASS_1_MODEL_DRIFT = "CLASS_1_MODEL_DRIFT"
    CLASS_2_INFRASTRUCTURE = "CLASS_2_INFRASTRUCTURE"
    CLASS_3_INTEGRATION = "CLASS_3_INTEGRATION"
    CLASS_4_EVALUATION = "CLASS_4_EVALUATION"
    CLASS_5_SAFETY_COMPLIANCE = "CLASS_5_SAFETY_COMPLIANCE"
    CLASS_6_OPERATIONAL = "CLASS_6_OPERATIONAL"
    UNKNOWN = "UNKNOWN"


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Detectability(Enum):
    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    SILENT = "silent"


class BlastRadius(Enum):
    SINGLE_REQUEST = "single_request"
    SINGLE_USER = "single_user"
    USER_COHORT = "user_cohort"
    TEAM = "team"
    ORG_WIDE = "org_wide"
    PUBLIC = "public"


class FailureBudgetClass(Enum):
    FC_A = "FC_A"
    FC_B = "FC_B"
    FC_C = "FC_C"
    FC_D = "FC_D"


@dataclass
class ClassificationResult:
    failure_class: FailureClass
    sub_class: Optional[str]
    severity: Severity
    detectability: Detectability
    blast_radius: BlastRadius
    failure_budget_class: FailureBudgetClass
    confidence: float
    primary_cause: str
    class_reasoning: str
    remediation_hint: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "failure_class": self.failure_class.value,
            "sub_class": self.sub_class,
            "severity": self.severity.value,
            "detectability": self.detectability.value,
            "blast_radius": self.blast_radius.value,
            "failure_budget_class": self.failure_budget_class.value,
            "confidence": self.confidence,
            "primary_cause": self.primary_cause,
            "class_reasoning": self.class_reasoning,
            "remediation_hint": self.remediation_hint,
        }


@dataclass
class FailureRecord:
    id: str
    title: str
    description: str
    domain: str
    date_reported: str
    source_url: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FailureRecord":
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            domain=data.get("domain", ""),
            date_reported=data.get("date_reported", ""),
            source_url=data.get("source_url", ""),
        )
