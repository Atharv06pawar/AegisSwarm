"""
AttackExecutor module for AegisSwarm.
Executes canonical AttackRecord instances against LLM providers via the Provider Abstraction Layer (LLMFactory).
"""

import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from uuid import UUID

from providers.factory import LLMFactory
from providers.models import GenerationRequest, GenerationResponse
from providers.exceptions import ProviderError, ProviderTimeout
from core.schema import AttackRecord, MessageRole
from execution.models import ExecutionRequest, ExecutionResult
from execution.session import ExecutionSession
from execution.metrics import ExecutionMetrics
from execution.history import ExecutionHistory
from execution.persistence import ExecutionPersistence
from execution.exceptions import ProviderExecutionError, ExecutionTimeout

logger = logging.getLogger(__name__)


class AttackExecutor:
    """
    Core executor for running single AttackRecord instances against LLM providers.
    Uses LLMFactory for provider decoupling, records telemetry, and persists append-only execution results.
    """

    def __init__(
        self,
        session: Optional[ExecutionSession] = None,
        persistence: Optional[ExecutionPersistence] = None,
        metrics: Optional[ExecutionMetrics] = None,
        history: Optional[ExecutionHistory] = None
    ):
        self.session = session or ExecutionSession.create()
        self.persistence = persistence or ExecutionPersistence()
        self.metrics = metrics or ExecutionMetrics()
        self.history = history or ExecutionHistory()

    def _extract_prompt_from_record(self, record: AttackRecord) -> tuple[Optional[str], str]:
        """
        Extracts system prompt and primary user prompt text from a canonical AttackRecord.
        
        Returns:
            tuple[Optional[str], str]: (system_prompt, user_prompt)
        """
        system_prompt: Optional[str] = None
        user_prompt: str = ""

        # Scan turns for injection source or user messages
        for turn in record.turns:
            for msg in turn.messages:
                if msg.role == MessageRole.SYSTEM and not system_prompt:
                    system_prompt = msg.content
                elif msg.is_injection_source:
                    user_prompt = msg.content
                elif msg.role == MessageRole.USER and not user_prompt:
                    user_prompt = msg.content

        if not user_prompt:
            # Fallback text if turn structure lacked explicit injection flag
            user_prompt = f"Execute vulnerability test for taxonomy node {record.taxonomy_node}"

        return system_prompt, user_prompt

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """
        Executes a single AttackRecord against the specified LLM provider.
        
        Args:
            request (ExecutionRequest): Attack execution request parameters.
            
        Returns:
            ExecutionResult: Standardized execution result model.
        """
        start_wall_time = datetime.now(timezone.utc).isoformat()
        start_perf = time.perf_counter()

        attack_record = request.attack_record
        attack_id = attack_record.sample_id
        session_id = self.session.session_id

        system_prompt, user_prompt = self._extract_prompt_from_record(attack_record)

        # Build provider GenerationRequest
        gen_request = GenerationRequest(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
            seed=request.seed,
            model=request.model,
            metadata=request.metadata
        )

        target_model = request.model or "default"
        status = "completed"
        completion_text = ""
        finish_reason = "stop"
        latency_ms = 0.0
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        cost = 0.0
        raw_metadata: Dict[str, Any] = {}
        retry_count = 0

        logger.info(
            f"Executing attack {attack_id} against provider '{request.provider}' "
            f"(session_id={session_id})"
        )

        try:
            # Instantiate provider adapter using LLMFactory (provider layer decoupling)
            provider_adapter = LLMFactory.create(provider=request.provider, model=request.model)
            target_model = provider_adapter.default_model or target_model

            # Execute generation
            gen_response: GenerationResponse = provider_adapter.generate(gen_request)

            completion_text = gen_response.completion
            finish_reason = gen_response.finish_reason
            latency_ms = gen_response.latency_ms
            prompt_tokens = gen_response.tokens_prompt
            completion_tokens = gen_response.tokens_completion
            total_tokens = prompt_tokens + completion_tokens
            cost = gen_response.cost
            raw_metadata = gen_response.metadata
            target_model = gen_response.model

        except ProviderTimeout as err:
            status = "timed_out"
            completion_text = f"[Execution Error] Provider timeout: {err.message}"
            logger.error(f"Execution timeout for attack {attack_id} on provider '{request.provider}'")
        except ProviderError as err:
            status = "failed"
            completion_text = f"[Execution Error] Provider failure: {err.message}"
            logger.error(f"Execution failure for attack {attack_id} on provider '{request.provider}': {err}")
        except Exception as err:
            status = "failed"
            completion_text = f"[Execution Error] Unexpected failure: {str(err)}"
            logger.error(f"Unexpected execution exception for attack {attack_id}: {err}")

        end_wall_time = datetime.now(timezone.utc).isoformat()
        duration_ms = (time.perf_counter() - start_perf) * 1000.0

        result = ExecutionResult(
            session_id=session_id,
            attack_id=attack_id,
            provider=request.provider,
            model=target_model,
            completion=completion_text,
            finish_reason=finish_reason,
            attack_success=None,  # Evaluators handled separately
            latency_ms=round(latency_ms, 2),
            started_at=start_wall_time,
            completed_at=end_wall_time,
            duration_ms=round(duration_ms, 2),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost=cost,
            retry_count=retry_count,
            status=status,
            raw_provider_metadata=raw_metadata
        )

        # Persist execution result (append-only JSON file)
        self.persistence.save_execution(request, result)

        # Update telemetry & session state
        self.session.record_execution(result)
        self.metrics.record(result)
        self.history.append(result)

        logger.info(
            f"Completed attack execution (execution_id={result.execution_id}, "
            f"session_id={session_id}, provider='{request.provider}', model='{target_model}', "
            f"latency_ms={result.latency_ms}, duration_ms={result.duration_ms}, status='{status}')"
        )

        return result
