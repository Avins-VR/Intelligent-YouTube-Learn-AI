"""
pages/recommendations_page.py

Learning Path stage. Generates and displays 5-10 recommended next
topics (via recommendations.py) as a progression timeline, building on
the current video's summary and key notes.
"""

import streamlit as st

from recommendations import generate_recommendations
from session_utils import initialize_session_state
from ui_theme import render_section_label, render_no_video_notice, render_path_node, render_icon
from utils.exceptions import LLMGenerationError

initialize_session_state()

render_section_label("Learning Path", icon="route")

if not st.session_state.video_processed:
    render_no_video_notice("Learning Path")
else:
    header_col, action_col = st.columns([4, 1.4], vertical_alignment="center")

    with header_col:
        st.markdown(
            '<p style="color: var(--text-dim); margin-top:0;">'
            "Where to go next, based on what this video covered."
            "</p>",
            unsafe_allow_html=True,
        )

    with action_col:
        button_label = "Regenerate" if st.session_state.recommendations else "Generate Path"
        generate_clicked = st.button(
            button_label, use_container_width=True, icon=":material/auto_awesome:"
        )

    if generate_clicked:
        with st.spinner("Mapping out a learning path..."):
            try:
                st.session_state.recommendations = generate_recommendations(
                    st.session_state.summary, st.session_state.notes,st.session_state.video_duration
                )
                st.session_state.recommendations_generated = True
            except LLMGenerationError as exc:
                st.error(str(exc), icon=":material/error:")

    if not st.session_state.recommendations:
        st.markdown(
            f"""
            <div class="ed-card">
                <p style="margin:0; color: var(--text-dim); display:flex; align-items:flex-start; gap:0.6rem;">
                    {render_icon("info", "20px")}
                    <span>
                        No learning path generated yet. Click <strong style="color:var(--text);">Generate Path</strong>
                        above to get 5-10 recommended next topics based on this video.
                    </span>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="ed-card">', unsafe_allow_html=True)
        for i, rec in enumerate(st.session_state.recommendations, start=1):
            render_path_node(i, rec["topic"], rec["reason"])
        st.markdown("</div>", unsafe_allow_html=True)