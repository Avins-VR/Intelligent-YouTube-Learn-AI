"""
pages/mcq_page.py

MCQ Assessment stage. Generates and displays MCQs for the processed
video (via mcq.py), with a review mode (answers + explanations shown
directly) and an optional quiz mode (pick answers first, then reveal).
"""

import streamlit as st

from mcq import generate_mcqs
from session_utils import initialize_session_state
from ui_theme import render_section_label, render_no_video_notice, render_question_card_header
from utils.exceptions import LLMGenerationError

initialize_session_state()

render_section_label("MCQ Assessment")

if not st.session_state.video_processed:
    render_no_video_notice("MCQ Assessment")
else:
    header_col, toggle_col, action_col = st.columns([3, 1.4, 1.4], vertical_alignment="center")

    with header_col:
        st.markdown(
            '<p style="color: var(--text-dim); margin-top:0;">'
            "Exam-style questions generated from this video's transcript."
            "</p>",
            unsafe_allow_html=True,
        )

    with toggle_col:
        if st.session_state.mcqs:
            st.session_state.mcq_quiz_mode = st.toggle(
                "Quiz mode", value=st.session_state.mcq_quiz_mode
            )

    with action_col:
        button_label = "Regenerate MCQs" if st.session_state.mcqs else "Generate MCQs"
        generate_clicked = st.button(button_label, use_container_width=True)

    if generate_clicked:
        with st.spinner("Generating MCQs from the transcript..."):
            try:
                st.session_state.mcqs = generate_mcqs(st.session_state.current_video_id,st.session_state.video_duration)
                st.session_state.mcqs_generated = True
                st.session_state.mcq_user_answers = {}
                st.session_state.mcq_submitted = False
            except LLMGenerationError as exc:
                st.error(f"⚠️ {str(exc)}")

    if not st.session_state.mcqs:
        st.markdown(
            """
            <div class="ed-card">
                <p style="margin:0; color: var(--text-dim);">
                    No MCQs generated yet. Click <strong style="color:var(--text);">Generate MCQs</strong>
                    above to create a question assessment from this video.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    elif st.session_state.mcq_quiz_mode:
        # --------------------- Quiz mode ---------------------
        with st.form(key="mcq_quiz_form"):
            for i, mcq_item in enumerate(st.session_state.mcqs, start=1):
                st.markdown('<div class="ed-mcq-card">', unsafe_allow_html=True)
                render_question_card_header(i, mcq_item["question"])

                option_labels = [f"{k}. {v}" for k, v in mcq_item["options"].items()]
                option_keys = list(mcq_item["options"].keys())

                previous_choice = st.session_state.mcq_user_answers.get(str(i))
                default_index = option_keys.index(previous_choice) if previous_choice in option_keys else None

                choice = st.radio(
                    f"mcq_choice_{i}",
                    options=option_keys,
                    format_func=lambda k, opts=mcq_item["options"]: f"{k}. {opts[k]}",
                    index=default_index,
                    key=f"mcq_radio_{i}",
                    label_visibility="collapsed",
                )
                st.session_state.mcq_user_answers[str(i)] = choice

                st.markdown("</div>", unsafe_allow_html=True)

            submit_quiz = st.form_submit_button("Submit Quiz", use_container_width=True)

        if submit_quiz:
            st.session_state.mcq_submitted = True

        if st.session_state.mcq_submitted:
            score = sum(
                1
                for i, mcq_item in enumerate(st.session_state.mcqs, start=1)
                if st.session_state.mcq_user_answers.get(str(i)) == mcq_item["correct_answer"]
            )
            render_section_label(f"Results — {score} / {len(st.session_state.mcqs)}")

            for i, mcq_item in enumerate(st.session_state.mcqs, start=1):
                user_choice = st.session_state.mcq_user_answers.get(str(i))
                correct_choice = mcq_item["correct_answer"]

                st.markdown('<div class="ed-mcq-card">', unsafe_allow_html=True)
                render_question_card_header(i, mcq_item["question"])

                for key, text in mcq_item["options"].items():
                    state_class = ""
                    if key == correct_choice:
                        state_class = "correct"
                    elif key == user_choice and key != correct_choice:
                        state_class = "incorrect"
                    st.markdown(
                        f'<div class="ed-mcq-option {state_class}">{key}. {text}</div>',
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    f'<div class="ed-mcq-explanation"><strong>Explanation:</strong> {mcq_item["explanation"]}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)

    else:
        # --------------------- Review mode (default) ---------------------
        for i, mcq_item in enumerate(st.session_state.mcqs, start=1):
            st.markdown('<div class="ed-mcq-card">', unsafe_allow_html=True)
            render_question_card_header(i, mcq_item["question"])

            correct_choice = mcq_item["correct_answer"]
            for key, text in mcq_item["options"].items():
                state_class = "correct" if key == correct_choice else ""
                st.markdown(
                    f'<div class="ed-mcq-option {state_class}">{key}. {text}</div>',
                    unsafe_allow_html=True,
                )

            st.markdown(
                f'<div class="ed-mcq-explanation"><strong>Explanation:</strong> {mcq_item["explanation"]}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)