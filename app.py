"""
app.py

Main Streamlit entry point for the AI-Powered Educational Video Learning
Assistant.
"""

import streamlit as st

import config
from transcript import get_processed_transcript
from embeddings import (
    chunk_transcript,
    create_and_store_embeddings,
    video_already_processed,
    get_collection_name,
)

from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from summary import generate_summary
from notes import generate_key_notes
from session_utils import initialize_session_state
from ui_theme import inject_global_css, render_top_navbar, render_section_label, render_stat_grid, render_icon
from utils.exceptions import (
    InvalidYouTubeURLError,
    TranscriptNotFoundError,
    TranscriptFetchError,
    EmbeddingGenerationError,
    VectorStoreError,
    LLMGenerationError,
)


# ---------------------------------------------------------------------------
# Page Configuration (must be called exactly once, here, before anything else)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Intelligent YouTube Learn AI",
    page_icon=":material/auto_awesome:",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------------------------
# Core Processing Logic (UNCHANGED business logic)
# ---------------------------------------------------------------------------
def process_video(youtube_url: str) -> None:
    """
    Run the full ingestion pipeline for a YouTube video: extract transcript,
    clean it, chunk it, embed it, store it in ChromaDB, and generate a
    study summary and key notes. Updates session state with the results.

    Args:
        youtube_url: The YouTube URL entered by the user.
    """
    with st.status("Processing video...", expanded=True) as status:
        try:
            st.write("Extracting video ID and fetching transcript...")
            result = get_processed_transcript(youtube_url)
            video_id = result["video_id"]
            cleaned_transcript = result["cleaned_transcript"]

            st.write("Cleaning and preparing transcript text...")

            already_done = video_already_processed(video_id)
            same_video_as_before = st.session_state.current_video_id == video_id

            if already_done:
                st.write("This video was already processed previously. Reusing existing data.")
                chunks = chunk_transcript(cleaned_transcript)
                num_chunks = len(chunks)
            else:
                st.write("Splitting transcript into semantic chunks...")
                chunks = chunk_transcript(cleaned_transcript)
                num_chunks = len(chunks)

                st.write(f"Generating embeddings for {num_chunks} chunks...")
                create_and_store_embeddings(video_id, chunks)
                st.write("Storing embeddings in ChromaDB...")

            # Reuse summary/notes if it's the same video already in session;
            # otherwise (re)generate for the newly processed video.
            if same_video_as_before and st.session_state.summary:
                summary = st.session_state.summary
            else:
                st.write("Generating AI summary...")
                duration = result.get("duration", 0)
                st.session_state.video_duration = duration
                summary = generate_summary(video_id, duration)

            if same_video_as_before and st.session_state.notes:
                key_notes = st.session_state.notes
            else:
                st.write("Extracting key notes...")
                key_notes = generate_key_notes(video_id)

            # Update session state
            st.session_state.current_video_id = video_id
            st.session_state.video_url = youtube_url
            st.session_state.video_duration = duration
            st.session_state.transcript = cleaned_transcript
            st.session_state.num_chunks = num_chunks
            st.session_state.transcript_length = len(cleaned_transcript)
            st.session_state.video_processed = True
            st.session_state.collection_name = get_collection_name(video_id)
            st.session_state.summary = summary
            st.session_state.notes = key_notes

            if not same_video_as_before:
                # Fresh video: clear out any leftover state from a previous video.
                st.session_state.chat_history = []
                st.session_state.last_answer = None
                st.session_state.last_question = None
                st.session_state.last_retrieved_chunks = []
                st.session_state.mcqs = []
                st.session_state.mcqs_generated = False
                st.session_state.mcq_user_answers = {}
                st.session_state.mcq_submitted = False
                st.session_state.recommendations = []
                st.session_state.recommendations_generated = False
                st.session_state.concept_map = None
                st.session_state.concept_map_generated = False

            status.update(label="Video processed successfully!", state="complete", expanded=False)

        except InvalidYouTubeURLError as exc:
            status.update(label="Invalid URL", state="error", expanded=True)
            st.error(str(exc), icon=":material/error:")
            st.session_state.video_processed = False
        except TranscriptNotFoundError as exc:
            status.update(label="Transcript unavailable", state="error", expanded=True)
            st.error(str(exc), icon=":material/error:")
            st.session_state.video_processed = False
        except TranscriptFetchError as exc:
            status.update(label="Transcript fetch failed", state="error", expanded=True)
            st.error(str(exc), icon=":material/error:")
            st.session_state.video_processed = False
        except EmbeddingGenerationError as exc:
            status.update(label="Embedding generation failed", state="error", expanded=True)
            st.error(str(exc), icon=":material/error:")
            st.session_state.video_processed = False
        except VectorStoreError as exc:
            status.update(label="Database error", state="error", expanded=True)
            st.error(str(exc), icon=":material/error:")
            st.session_state.video_processed = False
        except LLMGenerationError as exc:
            status.update(label="AI generation failed", state="error", expanded=True)
            st.error(str(exc), icon=":material/error:")
            st.session_state.video_processed = False
        except Exception as exc:  # noqa: BLE001 - final safety net for unexpected errors
            status.update(label="Unexpected error", state="error", expanded=True)
            st.error(f"An unexpected error occurred: {str(exc)}", icon=":material/error:")
            st.session_state.video_processed = False


# ---------------------------------------------------------------------------
# Learn Page UI (video processing + summary, kept together on one page)
# ---------------------------------------------------------------------------
def render_video_input_section() -> None:
    """Render the YouTube URL input and processing trigger."""
    render_section_label("Process Video", icon="link")

    col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
    with col1:
        youtube_url = st.text_input(
            "YouTube video URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
            key="youtube_url_input",
        )
    with col2:
        process_clicked = st.button(
            "Process Video", use_container_width=True, icon=":material/play_arrow:"
        )

    if process_clicked:
        if not youtube_url or not youtube_url.strip():
            st.warning("Please enter a YouTube URL before processing.", icon=":material/warning:")
        else:
            process_video(youtube_url.strip())


def render_transcript_stats() -> None:
    """Render transcript/processing stats once a video has been processed."""
    if not st.session_state.video_processed:
        st.markdown(
            f"""
            <div class="ed-card">
                <p style="margin:0; color: var(--text-dim); display:flex; align-items:flex-start; gap:0.6rem;">
                    {render_icon("info", "20px")}
                    <span>
                        Paste a YouTube lecture or talk URL above and click
                        <strong style="color:var(--text);">Process Video</strong> to get started.
                        Once processed, a summary appears below, and you can move through
                        Key Notes, Doubt Clarification, MCQ Assessment, Learning Path, and
                        Concept Map using the rail above.
                    </span>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    render_section_label("Transcript Overview", icon="analytics")

    db_status = "Connected" if st.session_state.collection_name else "Not Connected"

    render_stat_grid(
        [
            {"icon": "description", "value": f"{st.session_state.transcript_length:,}", "label": "Transcript Length"},
            {"icon": "view_module", "value": str(st.session_state.num_chunks), "label": "Chunks Created"},
            {"icon": "check_circle", "value": "Yes", "label": "Video Processed"},
            {"icon": "database", "value": db_status, "label": "Database Status"},
        ]
    )


def create_summary_pdf(summary_text):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    content = [
        Paragraph("Video Summary", styles["Title"]),
        Spacer(1, 12),
        Paragraph(
            summary_text.replace("\n", "<br/>"),
            styles["BodyText"]
        )
    ]

    doc.build(content)

    buffer.seek(0)

    return buffer


def render_summary_section() -> None:

    if not st.session_state.video_processed or not st.session_state.summary:
        return

    render_section_label("Summary", icon="article")

    summary = st.session_state.summary

    col1, col2 = st.columns([20, 1])

    with col2:

        pdf_file = create_summary_pdf(summary)

        st.download_button(
            label="",
            data=pdf_file,
            file_name="video_summary.pdf",
            mime="application/pdf",
            help="Download Summary PDF",
            key="summary_download",
            icon=":material/download:",
        )

    st.markdown(
        '<div class="ed-card">',
        unsafe_allow_html=True
    )

    st.markdown(summary)

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

def render_learn_page() -> None:
    """Full content of the 'Learn' stage: processing + summary together."""
    render_video_input_section()
    render_transcript_stats()
    render_summary_section()


# ---------------------------------------------------------------------------
# Router: register all six stages and render the shared top navbar
# ---------------------------------------------------------------------------
def main() -> None:
    inject_global_css()
    initialize_session_state()

    learn_page = st.Page(
        render_learn_page, title="Learn", icon=":material/play_circle:",
        default=True, url_path="learn",
    )
    notes_page = st.Page(
        "pages/notes_page.py", title="Key Notes", icon=":material/sticky_note_2:",
        url_path="notes",
    )
    doubt_page = st.Page(
        "pages/chat_page.py", title="Doubt Clarification", icon=":material/forum:",
        url_path="doubt",
    )
    mcq_page = st.Page(
        "pages/mcq_page.py", title="MCQ Assessment", icon=":material/quiz:",
        url_path="mcq",
    )
    path_page = st.Page(
        "pages/recommendations_page.py", title="Learning Path", icon=":material/route:",
        url_path="path",
    )
    concept_map_page = st.Page(
        "pages/concept_map_page.py", title="Concept Map", icon=":material/account_tree:",
        url_path="concept_map",
    )

    nav_pages = {
        "learn": learn_page,
        "notes": notes_page,
        "doubt": doubt_page,
        "mcq": mcq_page,
        "path": path_page,
        "concept_map": concept_map_page,
    }

    try:
        pg = st.navigation(list(nav_pages.values()), position="hidden")
    except TypeError:
        # Older Streamlit versions without the `position` kwarg: the global
        # CSS in ui_theme.py force-hides the sidebar nav as a fallback.
        pg = st.navigation(list(nav_pages.values()))

    active_key = next((k for k, p in nav_pages.items() if p == pg), "learn")
    render_top_navbar(active_key, nav_pages)

    pg.run()


if __name__ == "__main__":
    main()