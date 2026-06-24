"""
pages/notes_page.py

Key Notes stage. Displays the key notes generated during video
processing (session_state.notes), with an optional regenerate action
that reuses the existing notes.generate_key_notes() backend unchanged.
"""

import streamlit as st

from notes import generate_key_notes
from session_utils import initialize_session_state
from ui_theme import render_section_label, render_no_video_notice, render_icon
from utils.exceptions import LLMGenerationError
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

initialize_session_state()

def create_notes_pdf(notes):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    content = [
        Paragraph(
            "Key Notes",
            styles["Title"]
        ),
        Spacer(1, 12)
    ]

    for note in notes:

        content.append(
            Paragraph(
                f"• {note}",
                styles["BodyText"]
            )
        )

        content.append(
            Spacer(1, 6)
        )

    doc.build(content)

    buffer.seek(0)

    return buffer

render_section_label("Key Notes", icon="sticky_note_2")

if not st.session_state.video_processed:
    render_no_video_notice("Key Notes")
else:
    col1, col2, col3 = st.columns(
        [5, 1, 0.6],
        vertical_alignment="center"
    )
    with col1:
        st.markdown(
            '<p style="color: var(--text-dim); margin-top:0;">'
            "Concise, exam-ready takeaways extracted from this video's transcript."
            "</p>",
            unsafe_allow_html=True,
        )
    with col2:
        regenerate_clicked = st.button(
            "Regenerate", use_container_width=True, icon=":material/refresh:"
        )
    with col3:

        if st.session_state.notes:

            pdf_file = create_notes_pdf(
                st.session_state.notes
            )

            st.download_button(
                label="",
                data=pdf_file,
                file_name="key_notes.pdf",
                mime="application/pdf",
                help="Download Notes PDF",
                use_container_width=True,
                key="notes_download",
                icon=":material/download:",
            )

    if regenerate_clicked:
        with st.spinner("Regenerating key notes..."):
            try:
                st.session_state.notes = generate_key_notes(st.session_state.current_video_id)
                st.session_state.notes_generated = True
            except LLMGenerationError as exc:
                st.error(str(exc), icon=":material/error:")

    if not st.session_state.notes:
        st.markdown(
            f"""
            <div class="ed-card">
                <p style="margin:0; color: var(--text-dim); display:flex; align-items:center; gap:0.6rem;">
                    {render_icon("info", "20px")}
                    No notes available yet for this video.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for note in st.session_state.notes:
            st.markdown(
                f'<div class="ed-note-card">{render_icon("task_alt", "17px")}<span>{note}</span></div>',
                unsafe_allow_html=True,
            )