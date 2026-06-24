"""
pages/chat_page.py

Doubt Clarification Page
"""

import re
import streamlit as st

from embeddings import query_video_chunks
from rag import answer_doubt
from session_utils import initialize_session_state
from ui_theme import (
    inject_global_css,
    render_top_navbar,
    render_section_label,
    render_no_video_notice,
    render_icon,
)
from utils.exceptions import (
    EmptyQuestionError,
    EmbeddingGenerationError,
    VectorStoreError,
    LLMGenerationError,
)

st.set_page_config(
    page_title="Doubt Clarification",
    page_icon=":material/forum:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def clean_answer(answer: str) -> str:

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
                question=question
            )

        with st.spinner("Thinking..."):

            answer = answer_doubt(
                retrieved_chunks,
                question
            )

            answer = clean_answer(answer)

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

        st.session_state.last_question = question
        st.session_state.last_answer = answer
        st.session_state.last_retrieved_chunks = retrieved_chunks

    except EmptyQuestionError as exc:
        st.warning(str(exc), icon=":material/warning:")

    except EmbeddingGenerationError as exc:
        st.error(str(exc), icon=":material/error:")

    except VectorStoreError as exc:
        st.error(str(exc), icon=":material/error:")

    except LLMGenerationError as exc:
        st.error(str(exc), icon=":material/error:")

    except Exception as exc:
        st.error(
            f"An unexpected error occurred: {str(exc)}", icon=":material/error:"
        )


def render_chat_history() -> None:

    if not st.session_state.chat_history:

        st.markdown(
            f"""
            <div class="ed-card">
                <p style="margin:0; display:flex; align-items:center; gap:0.6rem;">
                    {render_icon("forum", "20px")}
                    No questions yet — ask your first one below.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return

    st.markdown(
        '<div class="ed-chat-scroll">',
        unsafe_allow_html=True
    )

    current_user = None

    for message in st.session_state.chat_history:

        if message["role"] == "user":

            current_user = message["content"]

        elif message["role"] == "assistant":

            answer = message["content"]

            st.markdown(
                f"""
                <div class="ed-bubble-row user">
                    <div class="ed-bubble user">
                        <span class="ed-bubble-label">
                            {render_icon("person", "13px")}You
                        </span>
                        {current_user}
                    </div>
                </div>

                <div class="ed-bubble-row assistant">
                    <div class="ed-bubble assistant">
                        <span class="ed-bubble-label">
                            {render_icon("smart_toy", "13px")}Tutor
                        </span>
                        {answer}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


def main():

    inject_global_css()

    initialize_session_state()


    if (
        not st.session_state.video_processed
        or not st.session_state.current_video_id
    ):
        render_no_video_notice(
            "Doubt Clarification"
        )
        return

    if st.button("Clear Chat", icon=":material/delete:"):

        st.session_state.chat_history = []
        st.rerun()

    render_section_label(
        f"Chat · {len(st.session_state.chat_history)//2} question(s) asked",
        icon="forum",
    )

    render_chat_history()

    with st.form(
        key="doubt_chat_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(
            [5, 1],
            vertical_alignment="bottom"
        )

        with col1:

            user_question = st.text_input(
                "Ask a question",
                placeholder="e.g. Can you explain that last concept again?",
                label_visibility="collapsed"
            )

        with col2:

            submitted = st.form_submit_button(
                "Send",
                use_container_width=True,
                icon=":material/send:",
            )

    if submitted:

        if not user_question.strip():

            st.warning(
                "Please enter a question before submitting.", icon=":material/warning:"
            )

        else:

            handle_user_question(
                user_question.strip()
            )

            st.rerun()


if __name__ == "__main__":
    main()