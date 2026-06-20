"""
pages/chat_page.py
"""

import re
import streamlit as st

from embeddings import query_video_chunks
from rag import answer_doubt
from session_utils import initialize_session_state
from ui_theme import (
    inject_global_css,
    render_header,
    render_section_label,
    render_no_video_notice
)
from utils.exceptions import (
    EmptyQuestionError,
    EmbeddingGenerationError,
    VectorStoreError,
    LLMGenerationError,
)


st.set_page_config(
    page_title="Doubt Clarification · Video Learning Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_sidebar_nav() -> None:
    with st.sidebar:
        st.markdown("### 🎓 Navigation")
        st.page_link("app.py", label="Process Video", icon="🏠")
        st.page_link("pages/summary_page.py", label="Summary", icon="📄")
        st.page_link("pages/notes_page.py", label="Key Notes", icon="🗒️")
        st.page_link("pages/chat_page.py", label="Doubt Clarification", icon="💬")


def clean_answer(answer: str) -> str:
    """
    Remove accidental HTML tags from model responses.
    """

    if not answer:
        return ""

    answer = re.sub(
        r"<[^>]*>",
        "",
        answer
    )

    return answer.strip()


def handle_user_question(question: str) -> None:

    try:

        with st.spinner(
            "Retrieving relevant transcript sections..."
        ):
            retrieved_chunks = query_video_chunks(
                video_id=st.session_state.current_video_id,
                question=question,
            )

        with st.spinner("Thinking..."):

            answer = answer_doubt(
                retrieved_chunks,
                question
            )

            answer = clean_answer(
                answer
            )

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": question
            }
        )

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

    except EmptyQuestionError as exc:
        st.warning(f"⚠️ {str(exc)}")

    except EmbeddingGenerationError as exc:
        st.error(f"⚠️ {str(exc)}")

    except VectorStoreError as exc:
        st.error(f"⚠️ {str(exc)}")

    except LLMGenerationError as exc:
        st.error(f"⚠️ {str(exc)}")

    except Exception as exc:
        st.error(
            f"⚠️ An unexpected error occurred: {str(exc)}"
        )


def render_chat_history() -> None:

    if not st.session_state.chat_history:

        st.markdown(
            """
            <div class="ed-card">
                <p style="margin:0;">
                    Ask anything about the video —
                    definitions, clarifications,
                    or explain a concept again.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return

    bubbles_html = '<div class="ed-chat-scroll">'

    for message in st.session_state.chat_history:

        role = message["role"]

        content = (
            message["content"]
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
        )

        label = (
            "You"
            if role == "user"
            else "Tutor"
        )

        bubbles_html += f"""
        <div class="ed-bubble-row {role}">
            <div class="ed-bubble {role}">
                <span class="ed-bubble-label">
                    {label}
                </span>
                {content}
            </div>
        </div>
        """

    bubbles_html += "</div>"

    st.markdown(
        bubbles_html,
        unsafe_allow_html=True
    )


def render_chat_input() -> None:

    col1, col2 = st.columns(
        [4, 1],
        vertical_alignment="bottom"
    )

    with col1:

        question = st.text_input(
            "Ask a question about the video",
            placeholder=(
                "e.g. Can you explain "
                "that last concept again?"
            ),
            label_visibility="collapsed",
            key="chat_question_input",
        )

    with col2:

        ask_clicked = st.button(
            "Send",
            use_container_width=True
        )

    if ask_clicked:

        if not question.strip():

            st.warning(
                "⚠️ Please enter a question before sending."
            )

        else:

            handle_user_question(
                question.strip()
            )

            st.rerun()


def main() -> None:

    inject_global_css()

    initialize_session_state()

    render_sidebar_nav()

    render_header(
        "Doubt Clarification",
        "Chat with the video. Answers are grounded in its transcript."
    )

    if (
        not st.session_state.video_processed
        or not st.session_state.current_video_id
    ):

        render_no_video_notice(
            "Doubt Clarification"
        )

        return

    if st.button("🗑️ Clear Chat"):

        st.session_state.chat_history = []

        st.rerun()

    render_section_label(
        f"Chat · {len(st.session_state.chat_history) // 2} question(s) asked"
    )

    render_chat_history()

    render_chat_input()


if __name__ == "__main__":
    main()