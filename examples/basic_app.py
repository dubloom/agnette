from agnos import AgentOptions
from agnette import Agnette

app = Agnette(
    default_agent_options=AgentOptions(
        model="claude-sonnet-4-5",
        allowed_tools=["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch"],
    )
)

@app.post(
    "/summarize",
    prompt=(
        "Summarize the user input in 3 bullet points. "
        "If the payload includes a `tone`, adapt the writing style accordingly."
    ),
)
def summarize_route() -> None:
    """Decorator anchor; the framework route behavior is prompt-driven."""


@app.get(
    "/health",
    prompt="Return a short one-line health check response for this API route.",
)
def health_route() -> None:
    """Decorator anchor; the framework route behavior is prompt-driven."""