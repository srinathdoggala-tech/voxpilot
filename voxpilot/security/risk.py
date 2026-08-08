"""Human-in-the-Loop Risk Classifier and Confirmation Engine."""

from typing import Literal
from pydantic import BaseModel

RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "BLOCKED"]


class RiskAssessment(BaseModel):
    """Assessment of tool execution risk level."""
    tool_name: str
    risk_level: RiskLevel
    requires_user_confirmation: bool
    explanation: str


class RiskClassifier:
    """Classifies tool execution risk into LOW, MEDIUM, HIGH, BLOCKED and enforces confirmation boundaries."""

    def __init__(self):
        # Declarative tool risk classification map
        self.tool_risk_map: dict[str, RiskLevel] = {
            "calculator": "LOW",
            "weather_search": "LOW",
            "knowledge_search": "LOW",
            "calendar_scheduler": "MEDIUM",
            "task_creator": "MEDIUM",
            "crm_customer_lookup": "MEDIUM",
            "send_email": "HIGH",
            "execute_payment": "HIGH",
            "system_shell": "BLOCKED"
        }

    def assess_risk(self, tool_name: str, kwargs: dict) -> RiskAssessment:
        """Evaluate tool execution risk level and return confirmation requirements."""
        risk_level = self.tool_risk_map.get(tool_name, "HIGH")

        if risk_level == "BLOCKED":
            return RiskAssessment(
                tool_name=tool_name,
                risk_level="BLOCKED",
                requires_user_confirmation=False,
                explanation=f"Tool '{tool_name}' is permanently BLOCKED by security policy."
            )
        elif risk_level in ["MEDIUM", "HIGH"]:
            return RiskAssessment(
                tool_name=tool_name,
                risk_level=risk_level,
                requires_user_confirmation=True,
                explanation=f"Tool '{tool_name}' has {risk_level} side-effect risk and requires explicit user confirmation."
            )
        else:
            return RiskAssessment(
                tool_name=tool_name,
                risk_level="LOW",
                requires_user_confirmation=False,
                explanation=f"Tool '{tool_name}' has LOW risk and can execute automatically."
            )


# Global RiskClassifier singleton instance
risk_classifier = RiskClassifier()
