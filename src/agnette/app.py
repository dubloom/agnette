from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, Callable

from glyph import AgentOptions
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from agnette.requests import handle_request

from .middleware import handle_middleware, to_blocking_response
from .models import AgentMiddlewareDefinition, AgentRouteDefinition

logger = logging.getLogger("uvicorn.error")


class Agnette:
    def __init__(
        self,
        default_agent_options: AgentOptions,
        prompt: str | None = None,
    ) -> None:
        self._total_cost_usd: float = 0.0
        self._total_cost_lock = asyncio.Lock()
        self._default_agent_options: AgentOptions = default_agent_options
        self._starlette_app: Starlette = Starlette(lifespan=self._lifespan)

        # if prompt is provided, no routes can be registered
        if prompt:
            """ This is what a LLM has to say on this variable naming:
              +------------------------------------------------------------------------------------------------------------------+
              | + [N0] Unprofessional variable naming                                                                            |
              | file: src/agnette/app.py                                                                                         |
              |                                                                                                                  |
              | Why: Line 36, 39, 189: The variable name '_vibiiiiiiiing' is playful but unprofessional for production code.     |
              | While it fits the 'vibe mode' theme, it may harm code maintainability and professional perception.               |
              |                                                                                                                  |
              | Fix: Consider renaming to '_vibe_mode' or '_app_level_prompt_mode' for better clarity and professionalism        |
              +------------------------------------------------------------------------------------------------------------------+
            """
            self._vibiiiiiiiing = True
            self._register_vibe_route(prompt)
        else:
            self._vibiiiiiiiing = False

    def _register_vibe_route(self, prompt: str) -> None:
        route_definition = AgentRouteDefinition(
            path="/{path:path}",
            methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
            prompt=prompt,
            agent_options=self._default_agent_options,
            name=None,
        )
        self._register_agent_route(route_definition)

    def _register_agent_route(self, route_definition: AgentRouteDefinition) -> None:
        async def endpoint(request: Request, definition: AgentRouteDefinition = route_definition) -> Response:
            response, cost = await handle_request(request, definition)
            if cost:
                async with self._total_cost_lock:
                    self._total_cost_usd += cost
            return response

        self._starlette_app.router.routes.append(
            Route(
                route_definition.path,
                endpoint=endpoint,
                methods=list(route_definition.methods),
                name=route_definition.name,
            )
        )

    def middleware(
        self,
        middleware_type: str,
        *,
        prompt: str | None = None,
        agent_options: AgentOptions | None = None,
        name: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        if middleware_type.lower() != "http":
            raise ValueError(f"Unsupported middleware type '{middleware_type}'. Only 'http' is supported.")
        if not prompt:
            raise ValueError("middleware() requires a non-empty `prompt` for Agnette prompt-based middleware.")

        middleware_agent_options = agent_options or self._default_agent_options
        agnette = self

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            middleware_name = name or func.__name__
            definition = AgentMiddlewareDefinition(
                prompt=prompt,
                agent_options=middleware_agent_options,
                name=middleware_name,
            )
            class _PromptMiddleware(BaseHTTPMiddleware):
                async def dispatch(
                    self, request: Request, call_next: RequestResponseEndpoint
                ) -> Response:
                    decision, cost = await handle_middleware(definition, request)
                    if cost:
                        async with agnette._total_cost_lock:
                            agnette._total_cost_usd += cost
                    if decision.allow:
                        return await call_next(request)
                    return to_blocking_response(decision)

            self._starlette_app.add_middleware(_PromptMiddleware)
            return func

        return decorator

    @asynccontextmanager
    async def _lifespan(self, _app: Starlette):
        yield
        async with self._total_cost_lock:
            total = self._total_cost_usd
        logger.info("Total agent cost (all runs): $%.6f USD", total)

    def get(
        self,
        path: str,
        *,
        prompt: str,
        name: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self.route(path, prompt=prompt, methods=["GET"], name=name)

    def post(
        self,
        path: str,
        *,
        prompt: str,
        name: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self.route(path, prompt=prompt, methods=["POST"], name=name)

    def delete(
        self,
        path: str,
        *,
        prompt: str,
        name: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self.route(path, prompt=prompt, methods=["DELETE"], name=name)

    def put(
        self,
        path: str,
        *,
        prompt: str,
        name: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self.route(path, prompt=prompt, methods=["PUT"], name=name)

    def options(
        self,
        path: str,
        *,
        prompt: str,
        name: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self.route(path, prompt=prompt, methods=["OPTIONS"], name=name)

    def patch(
        self,
        path: str,
        *,
        prompt: str,
        name: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self.route(path, prompt=prompt, methods=["PATCH"], name=name)

    def head(
        self,
        path: str,
        *,
        prompt: str,
        name: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return self.route(path, prompt=prompt, methods=["HEAD"], name=name)

    def route(
        self,
        path: str,
        *,
        prompt: str,
        methods: list[str] | tuple[str, ...] | None = None,
        agent_options: AgentOptions | None = None,
        name: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        # if a prompt is defined on the app, it means we should not define routes and just
        # trust the vibes
        if self._vibiiiiiiiing:
            raise RuntimeError("You can't define routes on an app cool like this, sorry ;)")

        route_methods = tuple(method.upper() for method in (methods or ["GET"]))
        if not route_methods:
            raise ValueError("At least one HTTP method is required.")

        if agent_options is None:
            agent_options = self._default_agent_options

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            route_name = name or func.__name__

            route_definition = AgentRouteDefinition(
                path=path,
                methods=route_methods,
                prompt=prompt,
                agent_options=agent_options,
                name=route_name,
            )
            self._register_agent_route(route_definition)
            return func

        return decorator

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        await self._starlette_app(scope, receive, send)
