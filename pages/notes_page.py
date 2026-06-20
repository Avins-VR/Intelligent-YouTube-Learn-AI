"""
pages/notes_page.py

Displays the AI-generated key notes for the currently processed video,
each rendered as a clean, scannable bullet card.
"""

import streamlit as st

from session_utils import initialize_session_state
from ui_theme import inject_global_css, render_header, render_section_label, render_no_video_notice


st.set_page_config(
    page_title="Key Notes · Video Learning Assistant",
    page_icon="🗒️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_sidebar_nav() -> None:
    """Render the shared sidebar navigation."""
    with st.sidebar:
        st.markdown("### 🎓 Navigation")
        st.page_link("app.py", label="Process Video", icon="🏠")
        st.page_link("pages/summary_page.py", label="Summary", icon="📄")
        st.page_link("pages/notes_page.py", label="Key Notes", icon="🗒️")
        st.page_link("pages/chat_page.py", label="Doubt Clarification", icon="💬")


def render_notes_list() -> None:
    """Render each key note inside its own bullet card."""
    render_section_label(f"Key Notes ({len(st.session_state.notes)})")

    for note in st.session_state.notes:
        st.markdown(
            f'<div class="ed-note-card" style="color: black;">• {note}</div>',
            unsafe_allow_html=True,
        )

def main() -> None:
    """Page entry point."""
    inject_global_css()
    initialize_session_state()
    render_sidebar_nav()

    render_header("Key Notes", "The most important concepts, terms, and takeaways — at a glance.")

    if not st.session_state.video_processed or not st.session_state.notes:
        render_no_video_notice("the Key Notes page")
        return

    render_notes_list()


if __name__ == "__main__":
    main()