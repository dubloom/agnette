import json
import logging
import re
from http import HTTPStatus

from agnette.prompts import compose_middleware_prompt
from agnette.requests import extract_request_context
from agnette.runner import AgentRunner

from .models import AgentMiddlewareDefinition, PromptMiddlewareOutput

from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response

logger = logging.getLogger("uvicorn.error")

_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL | re.IGNORECASE)


def _default_response_text_for_status(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return "Request blocked by Agnette middleware."


async def handle_middleware(
    definition: AgentMiddlewareDefinition,
    request: Request,
) -> tuple[PromptMiddlewareOutput, float | None]:
    request_context = await extract_request_context(request)
    final_prompt = compose_middleware_prompt(definition, request_context)
    cost = None
    try:
        decision_text, cost = await AgentRunner.run(final_prompt, definition.agent_options)
        return parse_prompt_middleware_output(decision_text), cost
    except Exception as exc:
        logger.exception("Middleware agent '%s' failed", definition.name)
        return parse_prompt_middleware_output(
            json.dumps(
                {
                    "allow": False,
                    "status_code": 500,
                    "response_text": f"Middleware execution failed: {exc}",
                }
            )
        ), cost

def _extract_json_object(raw_text: str) -> str:
    text = raw_text.strip()
    m = _FENCE_RE.match(text)
    if m:
        return m.group(1).strip()
    return text


def parse_prompt_middleware_output(raw_text: str) -> PromptMiddlewareOutput:
    """Parse middleware model output from a JSON object."""
    try:
        payload = json.loads(_extract_json_object(raw_text))
    except json.JSONDecodeError:
        return PromptMiddlewareOutput(
            allow=False,
            status_code=500,
            response_text="Middleware agent returned invalid JSON output.",
        )

    if not isinstance(payload, dict):
        return PromptMiddlewareOutput(
            allow=False,
            status_code=500,
            response_text="Middleware agent output must be a JSON object.",
        )

    allow = payload.get("allow")
    if not isinstance(allow, bool):
        return PromptMiddlewareOutput(
            allow=False,
            status_code=500,
            response_text="Middleware agent output missing boolean `allow`.",
        )

    status_code = payload.get("status_code", 403)
    if not isinstance(status_code, int):
        status_code = 403

    default_text = _default_response_text_for_status(status_code)
    response_text = payload.get("response_text", default_text)
    if not isinstance(response_text, str):
        response_text = default_text

    return PromptMiddlewareOutput(allow=allow, status_code=status_code, response_text=response_text)


def to_blocking_response(result: PromptMiddlewareOutput) -> Response:
    return PlainTextResponse(result.response_text, status_code=result.status_code)
