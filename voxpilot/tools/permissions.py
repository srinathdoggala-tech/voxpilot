"""Tool Permission Policy and Execution Boundary Guards."""

import logging
from pydantic import BaseModel
from voxpilot.security.risk import risk_classifier, RiskAssessment

logger = logging.getLogger("voxpilot.tools.permissions")


class PermissionGuardResult(BaseModel):
    """Result of permission boundary guard evaluation."""
    allowed: bool
    requires_confirmation: bool
    reason: str


class ToolPermissionPolicy:
    """Enforces immutable permission boundaries on LLM tool invocation requests."""

    def validate_tool_permission(self, tool_name: str, kwargs: dict, user_confirmed: bool = False) -> PermissionGuardResult:
        """Validate if tool execution complies with permission rules and confirmation state."""
        assessment: RiskAssessment = risk_classifier.assess_risk(tool_name, kwargs)

        if assessment.risk_level == "BLOCKED":
            logger.error(f"Security Alert: Attempted execution of BLOCKED tool '{tool_name}'!")
            return PermissionGuardResult(
                allowed=False,
                requires_confirmation=False,
                reason=f"Execution of '{tool_name}' is forbidden by system security policy."
            )

        if assessment.requires_user_confirmation and not user_confirmed:
            logger.info(f"Tool '{tool_name}' requires pending user confirmation before execution.")
            return PermissionGuardResult(
                allowed=False,
                requires_confirmation=True,
                reason=f"Tool '{tool_name}' ({assessment.risk_level} risk) requires explicit user confirmation."
            )

        return PermissionGuardResult(
            allowed=True,
            requires_confirmation=False,
            reason="Tool permission granted."
        )


# Global ToolPermissionPolicy singleton instance
tool_permission_policy = ToolPermissionPolicy()
