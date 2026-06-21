"""
pages/notes_page.py

Key Notes stage. Displays the key notes generated during video
processing (session_state.notes), with an optional regenerate action
that reuses the existing notes.generate_key_notes() backend unchanged.

Note: the original content of this page wasn't available when this
redesign was generated, so this file was rebuilt from scratch against
the documented session-state contract (session_state.notes is a list
of strings, populated by notes.generate_key_notes() in app.py). If your
previous version did anything beyond displaying that list, let me know
and I'll fold it back in.
"""

import streamlit as st

from notes import generate_key_notes
from session_utils import initialize_session_state
from ui_theme import render_section_label, render_no_video_notice
from utils.exceptions import LLMGenerationError

initialize_session_state()

render_section_label("Key Notes")

if not st.session_state.video_processed:
    render_no_video_notice("Key Notes")
else:
    col1, col2 = st.columns([5, 1], vertical_alignment="center")
    with col1:
        st.markdown(
            '<p style="color: var(--text-dim); margin-top:0;">'
            "Concise, exam-ready takeaways extracted from this video's transcript."
            "</p>",
            unsafe_allow_html=True,
        )
    with col2:
        regenerate_clicked = st.button("Regenerate", use_container_width=True)

    if regenerate_clicked:
        with st.spinner("Regenerating key notes..."):
            try:
                st.session_state.notes = generate_key_notes(st.session_state.current_video_id)
                st.session_state.notes_generated = True
            except LLMGenerationError as exc:
                st.error(f"⚠️ {str(exc)}")

    if not st.session_state.notes:
        st.markdown(
            """
            <div class="ed-card">
                <p style="margin:0; color: var(--text-dim);">
                    No notes available yet for this video.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for note in st.session_state.notes:
            st.markdown(f'<div class="ed-note-card">• {note}</div>', unsafe_allow_html=True)