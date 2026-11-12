"""WorkerContext — what agents, tools, hooks and guardrails see (RunContextWrapper[WorkerContext]).

It is LOCAL state only: the SDK never sends the context object to the model.
"""

from dataclasses import dataclass, field
from typing import Literal

from soc_shared.masking import MaskMap
from soc_shared.models import ScopeVerdict

from agent_service.budget import RunBudget

Flow = Literal["ask", "triage"]


@dataclass
class WorkerContext:
    request_id: str
    user_id: str
    flow: Flow
    budget: RunBudget
    mask_map: MaskMap = field(default_factory=MaskMap)
    scope: ScopeVerdict | None = None
    alert_rule_level: int | None = None
    alert_mitre: list[str] = field(default_factory=list)
    seen_stable_ids: set[str] = field(default_factory=set)  # every stable_id KSOR returned this run
    web_urls: set[str] = field(default_factory=set)  # every URL web_search returned this run
    injection_suspected: bool = False
    tickets: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)  # audit-style breadcrumbs (masked only)
