"""Run the HealthPilot agent from Streamlit. Uses ADK Runner + InMemorySessionService."""

import asyncio
import uuid

_runner = None
_session_service = None


def _get_runner():
    """Lazy init Runner and InMemorySessionService so the same session persists in Streamlit."""
    global _runner, _session_service
    if _runner is None:
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from agent.agent import root_agent
        session_svc = InMemorySessionService()
        _session_service = session_svc
        _runner = Runner(
            agent=root_agent,
            app_name="healthpilot",
            session_service=session_svc,
        )
    return _runner, _session_service


async def _run_agent_async(
    user_id: str,
    session_id: str,
    user_message: str,
    *,
    create_session: bool = False,
) -> str:
    """Run the agent asynchronously and return the final assistant text."""
    runner, session_service = _get_runner()
    if create_session:
        await session_service.create_session(
            app_name="healthpilot",
            user_id=user_id,
            session_id=session_id,
        )
    from google.genai.types import Content, Part
    content = Content(role="user", parts=[Part.from_text(text=user_message)])
    events = runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    )
    final_parts: list[str] = []
    async for event in events:
        if getattr(event, "content", None) and getattr(event.content, "parts", None):
            for part in event.content.parts:
                if getattr(part, "text", None):
                    final_parts.append(part.text)
    return "\n".join(final_parts) if final_parts else "I couldn't generate a response. Please try again."


def run_agent(user_id: str, session_id: str, user_message: str, create_session: bool = False) -> str:
    """Sync wrapper: run the agent and return the final assistant text."""
    return asyncio.run(
        _run_agent_async(user_id, session_id, user_message, create_session=create_session)
    )


def new_session_id() -> str:
    """Return a new session ID for a new chat."""
    return str(uuid.uuid4())
