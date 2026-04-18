import logging

from agnos import AgentOptions, AgentQueryCompleted, query

# Same logger uvicorn configures (handlers + colors). Starlette does not attach log handlers.
logger = logging.getLogger("uvicorn.error")


class AgentExecutionError(RuntimeError):
    pass


class AgentRunner:
    @staticmethod
    async def run(prompt: str, options: AgentOptions) -> tuple[str, float]:
        try:
            async for message in query(prompt, options=options):
                if isinstance(message, AgentQueryCompleted):
                    # Get and log cost
                    cost = message.total_cost_usd
                    logger.info("Agent query cost: $%.6f USD", cost)
                    if message.is_error:
                        raise AgentExecutionError(message.message)
                    return message.message, cost
        except Exception as exc:  # pragma: no cover - depends on external API/runtime
            raise AgentExecutionError(f"Claude agent execution failed: {exc}") from exc

        raise AgentExecutionError("Claude agent returned no text output.")
