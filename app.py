"""
HealthPilot — Chat UI (Streamlit).
Health cost reduction advisor for India. Requires GOOGLE_API_KEY in .env.
"""

from pathlib import Path
import streamlit as st

# Load .env from project root so GOOGLE_API_KEY is available to the agent
_env = Path(__file__).resolve().parent / ".env"
if _env.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env)
    except ImportError:
        pass

APP_TITLE = "HealthPilot"
APP_DESC = "Your health cost reduction advisor for India. Ask about tips, medicines, or how to save on healthcare."


def init_chat_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        try:
            from agent.runner_helper import new_session_id
            st.session_state.session_id = new_session_id()
        except ImportError:
            st.session_state.session_id = "default"
    if "user_id" not in st.session_state:
        st.session_state.user_id = "streamlit_user"


def handle_new_chat() -> None:
    try:
        from agent.runner_helper import new_session_id
        st.session_state.session_id = new_session_id()
    except ImportError:
        st.session_state.session_id = "default"
    st.session_state.messages = []


def handle_new_message(user_content: str) -> None:
    init_chat_state()
    st.session_state.messages.append({"role": "user", "content": user_content})

    try:
        from agent.runner_helper import run_agent
    except ImportError as e:
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "HealthPilot agent isn't loaded. Install dependencies and set your API key:\n\n"
                "```bash\npip install -r requirements.txt\n```\n\n"
                "Create a `.env` in the project root with:\n`GOOGLE_API_KEY=your_key`\n\n"
                f"Import error: {e!s}"
            ),
        })
        return

    create_session = len(st.session_state.messages) == 1
    try:
        reply = run_agent(
            user_id=st.session_state.user_id,
            session_id=st.session_state.session_id,
            user_message=user_content,
            create_session=create_session,
        )
    except Exception as e:
        reply = (
            "Sorry, the agent isn't available right now. "
            "Make sure you've run: pip install google-adk and set GOOGLE_API_KEY in .env. "
            f"Error: {e!s}"
        )

    st.session_state.messages.append({"role": "assistant", "content": reply})


def render_chat() -> None:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="🩺", layout="centered")
    st.title(f"🩺 {APP_TITLE}")
    st.caption(APP_DESC)
    st.divider()

    init_chat_state()
    if st.button("New chat", type="secondary", use_container_width=False):
        handle_new_chat()
        st.rerun()
    render_chat()

    if prompt := st.chat_input("Ask about health tips, medicines, or cost-saving..."):
        handle_new_message(prompt)
        st.rerun()


if __name__ == "__main__":
    main()
