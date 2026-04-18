import json
from typing import Any

from .models import AgentMiddlewareDefinition, AgentRouteDefinition

def compose_request_prompt(definition: AgentRouteDefinition, request_context: dict[str, Any]) -> str:
    request_json = json.dumps(request_context, ensure_ascii=True, indent=2)
    return (
        "You are an HTTP route agent.\n"
        f"Route reached: {definition.path}\n"
        f"Allowed methods: {', '.join(definition.methods)}\n\n"
        f"Route prompt:\n{definition.prompt}\n\n"
        f"Request context (JSON):\n{request_json}\n"
    )


def compose_middleware_prompt(
    definition: AgentMiddlewareDefinition,
    request_context: dict[str, Any],
) -> str:
    request_json = json.dumps(request_context, ensure_ascii=True, indent=2)
    return (
        "You are an HTTP middleware agent.\n"
        "Evaluate whether this request should continue.\n"
        "Output rules: respond with a single JSON object only. No markdown fences, no prose, no code blocks.\n"
        "Return valid JSON only with keys:\n"
        '- "allow": boolean (required)\n'
        '- "status_code": integer (optional, used when allow=false)\n'
        '- "response_text": string (optional, used when allow=false)\n\n'
        f"Middleware name: {definition.name}\n"
        f"Middleware prompt:\n{definition.prompt}\n\n"
        f"Request context (JSON):\n{request_json}\n"
    )
