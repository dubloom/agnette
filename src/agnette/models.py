from dataclasses import dataclass

from glyph import AgentOptions


@dataclass(slots=True)
class AgentRouteDefinition:
    path: str
    methods: tuple[str, ...]
    prompt: str
    agent_options: AgentOptions
    name: str


@dataclass(slots=True)
class AgentMiddlewareDefinition:
    prompt: str
    agent_options: AgentOptions
    name: str


@dataclass(slots=True)
class PromptMiddlewareOutput:
    allow: bool
    status_code: int = 403
    response_text: str = "Request blocked by Agnette middleware."
