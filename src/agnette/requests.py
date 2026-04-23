import json
from typing import Any

from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response

from agnette.prompts import compose_request_prompt

from .runner import AgentRunner
from .models import AgentRouteDefinition


async def extract_request_context(request: Request) -> dict[str, Any]:
    body = await request.body()
    body_text = body.decode("utf-8", errors="replace") if body else ""
    json_body: Any | None = None

    if body_text and "application/json" in request.headers.get("content-type", ""):
        try:
            json_body = json.loads(body_text)
        except json.JSONDecodeError:
            json_body = None

    context: dict[str, Any] = {
        "path": request.url.path,
        "method": request.method,
        "path_params": dict(request.path_params),
        "query_params": dict(request.query_params),
        "headers": dict(request.headers),
    }

    if json_body is not None:
        context["json_body"] = json_body
    elif body_text:
        context["raw_body"] = body_text

    return context


async def handle_request(request: Request, definition: AgentRouteDefinition) -> tuple[Response, float | None]:
    request_context = await extract_request_context(request)
    final_prompt = compose_request_prompt(definition, request_context)
    cost = None
    try:
        response_text, cost = await AgentRunner.run(final_prompt, definition.agent_options)
        return Response(response_text, media_type=definition.response_content_type), cost
    except Exception as exc:
        return Response(f"Agent execution failed: {exc}", status_code=500, media_type="text/plain"), cost