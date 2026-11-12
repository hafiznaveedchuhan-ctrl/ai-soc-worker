"""RunHooks: price every LLM call, enforce the run budget, keep masked breadcrumbs."""

import logging
from typing import Any

from agents import Agent, RunContextWrapper, RunHooks
from agents.items import ModelResponse

from agent_service.context import WorkerContext

log = logging.getLogger("agent_service")


class CostHooks(RunHooks[WorkerContext]):
    def __init__(self, model_names: dict[str, str]) -> None:
        self._models = model_names  # agent name → model name (for pricing)

    async def on_llm_end(
        self,
        context: RunContextWrapper[WorkerContext],
        agent: Agent[WorkerContext],
        response: ModelResponse,
    ) -> None:
        u = response.usage
        model = self._models.get(agent.name, "unknown")
        entry = context.context.budget.record(agent.name, model, u.input_tokens, u.output_tokens)
        log.info(
            "llm request=%s agent=%s model=%s in=%d out=%d cost=$%.6f",
            entry.request_id,
            agent.name,
            model,
            u.input_tokens,
            u.output_tokens,
            entry.cost_usd,
        )

    async def on_handoff(
        self,
        context: RunContextWrapper[WorkerContext],
        from_agent: Agent[Any],
        to_agent: Agent[Any],
    ) -> None:
        context.context.events.append(f"handoff {from_agent.name} -> {to_agent.name}")

    async def on_tool_start(
        self, context: RunContextWrapper[WorkerContext], agent: Agent[Any], tool: Any
    ) -> None:
        context.context.events.append(f"tool {getattr(tool, 'name', tool)} by {agent.name}")
