"""
ReflectionEngine generating structured post-execution reflection analysis.
"""

from typing import Optional
from reasoning.models import ReflectionResult
from reasoning.exceptions import ReflectionError


class ReflectionEngine:
    """
    Reflection engine producing structured post-execution takeaways and optimization guidance.
    """

    def reflect(
        self,
        campaign_id: Optional[str] = None,
        attack_id: Optional[str] = None,
        outcome_success: bool = True
    ) -> ReflectionResult:
        """
        Generates a ReflectionResult containing what worked, what failed, why, and how to improve.
        """
        if outcome_success:
            what_worked = "Multi-family persona framing successfully bypassed target provider guardrails."
            what_failed = "Minor latency overhead due to recursive wrapper formatting."
            why = "Target model failed to detect indirect prompt payload embedded within XML delimiters."
            how_to_improve = "Optimize prompt length to reduce token consumption and lower request latency."
        else:
            what_worked = "Initial system framing established valid assistant context."
            what_failed = "Target provider safety classifier flagged explicit refusal trigger words."
            why = "Direct instruction payload was overly explicit without sufficient encoding obfuscation."
            how_to_improve = "Apply Base64 encoding or Typoglycemia mutation family to obfuscate refusal triggers."

        return ReflectionResult(
            campaign_id=campaign_id,
            attack_id=attack_id,
            what_worked=what_worked,
            what_failed=what_failed,
            why_outcome=why,
            how_to_improve=how_to_improve
        )
