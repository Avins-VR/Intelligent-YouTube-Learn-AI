"""
app.py

Main Streamlit entry point for the AI-Powered Educational Video Learning
Assistant. This page handles YouTube video ingestion (transcript fetch,
cleaning, chunking, embedding, ChromaDB storage, and summary generation)
and shows the main processing dashboard. Use the sidebar to navigate to
the Summary, Key Notes, and Doubt Clarification pages.
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
from summary import generate_summary
from notes import generate_key_notes
from session_utils import initialize_session_state
from ui_theme import inject_global_css, render_header, render_section_label
from utils.exceptions import (
    InvalidYouTubeURLError,
    TranscriptNotFoundError,
    TranscriptFetchError,
    EmbeddingGenerationError,
    VectorStoreError,
    LLMGenerationError,
)


# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Video Learning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Core Processing Logic
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
                summary = generate_summary(video_id, duration)

            if same_video_as_before and st.session_state.notes:
                key_notes = st.session_state.notes
            else:
                st.write("Extracting key notes...")
                key_notes = generate_key_notes(video_id)

            # Update session state
            st.session_state.current_video_id = video_id
            st.session_state.video_url = youtube_url
            st.session_state.transcript = cleaned_transcript
            st.session_state.num_chunks = num_chunks
            st.session_state.transcript_length = len(cleaned_transcript)
            st.session_state.video_processed = True
            st.session_state.collection_name = get_collection_name(video_id)
            st.session_state.summary = summary
            st.session_state.notes = key_notes

            if not same_video_as_before:
                # Fresh video: clear out any leftover chat from a previous video.
                st.session_state.chat_history = []
                st.session_state.last_answer = None
                st.session_state.last_question = None
                st.session_state.last_retrieved_chunks = []

            status.update(label="Video processed successfully!", state="complete", expanded=False)

        except InvalidYouTubeURLError as exc:
            status.update(label="Invalid URL", state="error", expanded=True)
            st.error(f"⚠️ {str(exc)}")
            st.session_state.video_processed = False
        except TranscriptNotFoundError as exc:
            status.update(label="Transcript unavailable", state="error", expanded=True)
            st.error(f"⚠️ {str(exc)}")
            st.session_state.video_processed = False
        except TranscriptFetchError as exc:
            status.update(label="Transcript fetch failed", state="error", expanded=True)
            st.error(f"⚠️ {str(exc)}")
            st.session_state.video_processed = False
        except EmbeddingGenerationError as exc:
            status.update(label="Embedding generation failed", state="error", expanded=True)
            st.error(f"⚠️ {str(exc)}")
            st.session_state.video_processed = False
        except VectorStoreError as exc:
            status.update(label="Database error", state="error", expanded=True)
            st.error(f"⚠️ {str(exc)}")
            st.session_state.video_processed = False
        except LLMGenerationError as exc:
            status.update(label="AI generation failed", state="error", expanded=True)
            st.error(f"⚠️ {str(exc)}")
            st.session_state.video_processed = False
        except Exception as exc:  # noqa: BLE001 - final safety net for unexpected errors
            status.update(label="Unexpected error", state="error", expanded=True)
            st.error(f"⚠️ An unexpected error occurred: {str(exc)}")
            st.session_state.video_processed = False


# ---------------------------------------------------------------------------
# UI Sections
# ---------------------------------------------------------------------------
def render_video_input_section() -> None:
    """Render the YouTube URL input and processing trigger."""
    render_section_label("Process Video")

    col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
    with col1:
        youtube_url = st.text_input(
            "YouTube video URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
            key="youtube_url_input",
        )
    with col2:
        process_clicked = st.button("Process Video", use_container_width=True)

    if process_clicked:
        if not youtube_url or not youtube_url.strip():
            st.warning("⚠️ Please enter a YouTube URL before processing.")
        else:
            process_video(youtube_url.strip())


def render_dashboard_cards() -> None:
    """Render the main dashboard stat cards once a video has been processed."""
    if not st.session_state.video_processed:
        st.markdown(
            """
            <div class="ed-card">
                <p style="margin:0; color: var(--muted);">
                    Paste a YouTube lecture or talk URL above and click
                    <strong>Process Video</strong> to get started. Once processed,
                    you'll be able to view an AI summary, key notes, and chat with
                    the video using the sidebar.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    render_section_label("Dashboard")

    db_status = "Connected" if st.session_state.collection_name else "Not Connected"

    st.markdown(
        f"""
        <div class="ed-stat-grid">
            <div class="ed-stat-tile">
                <span class="ed-stat-icon">📝</span>
                <span class="ed-stat-value">{st.session_state.transcript_length:,}</span>
                <span class="ed-stat-label">Transcript Length</span>
            </div>
            <div class="ed-stat-tile">
                <span class="ed-stat-icon">🧩</span>
                <span class="ed-stat-value">{st.session_state.num_chunks}</span>
                <span class="ed-stat-label">Chunks Created</span>
            </div>
            <div class="ed-stat-tile">
                <span class="ed-stat-icon">✅</span>
                <span class="ed-stat-value">Yes</span>
                <span class="ed-stat-label">Video Processed</span>
            </div>
            <div class="ed-stat-tile">
                <span class="ed-stat-icon">🗄️</span>
                <span class="ed-stat-value" style="font-size:1.05rem;">{db_status}</span>
                <span class="ed-stat-label">Database Status</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.success("✅ Ready — use the sidebar to view the Summary, Key Notes, or ask a question.")


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------
def main() -> None:
    """Application entry point."""
    inject_global_css()
    initialize_session_state()

    render_header(
        "AI-Powered Educational Video Learning Assistant",
        "Learn Faster from Educational Videos",
    )

    with st.sidebar:
        st.markdown("### 🎓 Navigation")
        st.page_link("app.py", label="Process Video", icon="🏠")
        st.page_link("pages/summary_page.py", label="Summary", icon="📄")
        st.page_link("pages/notes_page.py", label="Key Notes", icon="🗒️")
        st.page_link("pages/chat_page.py", label="Doubt Clarification", icon="💬")

    render_video_input_section()
    render_dashboard_cards()


if __name__ == "__main__":
    main()