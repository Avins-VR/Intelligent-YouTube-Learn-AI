"""
app.py

Main Streamlit application for the AI-Powered Educational Video Learning
Assistant. Provides the UI for submitting a YouTube URL, processing its
transcript into a RAG pipeline, and asking grounded questions about the
video content.
"""

import streamlit as st

import config
from transcript import get_processed_transcript
from embeddings import chunk_transcript, create_and_store_embeddings, query_video_chunks, video_already_processed
from rag import answer_question
from utils.exceptions import (
    InvalidYouTubeURLError,
    TranscriptNotFoundError,
    TranscriptFetchError,
    EmbeddingGenerationError,
    VectorStoreError,
    LLMGenerationError,
    EmptyQuestionError,
)
from summary import generate_summary

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Video Learning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------------------------
# Custom Styling
# ---------------------------------------------------------------------------
def inject_custom_css() -> None:
    """Inject custom CSS for a distinctive, scholarly visual identity."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,500&family=Source+Sans+3:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

        :root {
            --ink: #1c1a17;
            --paper: #faf6ee;
            --paper-raised: #ffffff;
            --rule: #ded3bb;
            --accent: #a8431e;
            --accent-soft: #f0dcc9;
            --accent-deep: #7a2f13;
            --muted: #6b6357;
        }

        html, body, [class*="css"] {
            font-family: 'Source Sans 3', sans-serif;
            color: var(--ink);
        }

        .stApp {
            background-color: var(--paper);
            background-image:
                linear-gradient(var(--rule) 1px, transparent 1px);
            background-size: 100% 2.1em;
            background-position: 0 7.2em;
        }

        /* Masthead */
        .va-masthead {
            border-bottom: 3px solid var(--ink);
            padding-bottom: 0.6rem;
            margin-bottom: 0.3rem;
        }
        .va-eyebrow {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: var(--accent-deep);
            margin-bottom: 0.2rem;
        }
        .va-title {
            font-family: 'Fraunces', serif;
            font-weight: 700;
            font-size: 2.6rem;
            line-height: 1.05;
            margin: 0;
            color: var(--ink);
        }
        .va-title em {
            font-style: italic;
            color: var(--accent);
            font-weight: 500;
        }
        .va-subtitle {
            font-size: 1.0rem;
            color: var(--muted);
            margin-top: 0.5rem;
            max-width: 640px;
        }

        /* Section labels styled like footnote markers */
        .va-section-label {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.75rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--accent-deep);
            border-left: 3px solid var(--accent);
            padding-left: 0.6rem;
            margin: 1.6rem 0 0.6rem 0;
        }

        /* Cards */
        .va-card {
            background: var(--paper-raised);
            border: 1px solid var(--rule);
            border-radius: 2px;
            padding: 1.4rem 1.6rem;
            box-shadow: 3px 3px 0 var(--rule);
        }

        .va-stat-row {
            display: flex;
            gap: 2.2rem;
            flex-wrap: wrap;
        }
        .va-stat {
            font-family: 'IBM Plex Mono', monospace;
        }
        .va-stat-num {
            font-family: 'Fraunces', serif;
            font-size: 1.9rem;
            font-weight: 600;
            color: var(--accent-deep);
            display: block;
        }
        .va-stat-label {
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--muted);
        }

        .va-answer-box {
            background: var(--paper-raised);
            border-left: 4px solid var(--accent);
            border-radius: 2px;
            padding: 1.2rem 1.5rem;
            font-size: 1.05rem;
            line-height: 1.6;
        }

        .va-divider {
            border: none;
            border-top: 1px dashed var(--rule);
            margin: 1.8rem 0;
        }

        /* Buttons */
        .stButton > button {
            font-family: 'IBM Plex Mono', monospace;
            background-color: var(--ink);
            color: var(--paper);
            border-radius: 2px;
            border: none;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            font-size: 0.8rem;
            padding: 0.55rem 1.3rem;
            transition: background-color 0.15s ease;
        }
        .stButton > button:hover {
            background-color: var(--accent-deep);
            color: var(--paper);
        }

        /* Inputs */
        .stTextInput > div > div > input {
            border-radius: 2px;
            border: 1px solid var(--rule);
            font-family: 'Source Sans 3', sans-serif;
        }
        .stTextInput > div > div > input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 1px var(--accent);
        }

        footer, header {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_masthead() -> None:
    """Render the application header in a newspaper-masthead style."""
    st.markdown(
        """
        <div class="va-masthead">
            <div class="va-eyebrow">VOL. 1 · A RETRIEVAL-AUGMENTED STUDY TOOL</div>
            <p class="va-title">The Lecture <em>Annotator</em></p>
            <p class="va-subtitle">
                Paste a YouTube lecture or talk below. We transcribe it, read it closely,
                and answer your questions strictly from what was actually said on screen.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------
def initialize_session_state() -> None:
    """Ensure all required keys exist in Streamlit's session state."""
    defaults = {
        "current_video_id": None,
        "current_video_url": None,
        "current_transcript": None,
        "video_summary": None,
        "num_chunks": 0,
        "transcript_length": 0,
        "video_processed": False,
        "last_answer": None,
        "last_question": None,
        "last_retrieved_chunks": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------------------------
# Core Processing Logic
# ---------------------------------------------------------------------------
def process_video(youtube_url: str) -> None:
    """
    Run the full ingestion pipeline for a YouTube video: extract transcript,
    clean it, chunk it, embed it, and store it in ChromaDB. Updates session
    state with the results.

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

            if already_done:
                st.write("This video was already processed previously. Reusing existing data.")
                num_chunks_created = 0
                # We still need a chunk count to display; recompute chunks
                # locally (cheap, no re-embedding) for the stats display.
                chunks = chunk_transcript(cleaned_transcript)
                num_chunks = len(chunks)
            else:
                st.write("Splitting transcript into semantic chunks...")
                chunks = chunk_transcript(cleaned_transcript)
                num_chunks = len(chunks)

                st.write(f"Generating embeddings for {num_chunks} chunks...")
                create_and_store_embeddings(
                    video_id,
                    chunks
                )
                st.write("Generating AI summary...")

                st.write("Storing embeddings in ChromaDB...")
            if st.session_state.current_video_id != video_id:
                summary = generate_summary(
                    video_id,
                    result["duration"]
                )
            else:
                summary = st.session_state.video_summary

            # Update session state
            st.session_state.current_video_id = video_id
            st.session_state.current_video_url = youtube_url
            st.session_state.current_transcript = cleaned_transcript
            st.session_state.num_chunks = num_chunks
            st.session_state.video_summary = summary
            st.session_state.transcript_length = len(cleaned_transcript)
            st.session_state.video_processed = True
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
        except Exception as exc:  # noqa: BLE001 - final safety net for unexpected errors
            status.update(label="Unexpected error", state="error", expanded=True)
            st.error(f"⚠️ An unexpected error occurred: {str(exc)}")
            st.session_state.video_processed = False

def render_summary_section():

    if not st.session_state.video_processed:
        return

    if not st.session_state.video_summary:
        return

    st.markdown(
        '<div class="va-section-label">§3 — Video Summary</div>',
        unsafe_allow_html=True
    )

    with st.container():
        st.markdown(
            '<div class="va-card style="color:black; white-space: pre-wrap;">',
            unsafe_allow_html=True
        )

        st.markdown(
            st.session_state.video_summary
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )
def handle_question(question: str) -> None:
    """
    Run the retrieval + generation pipeline for a user's question about
    the currently processed video, updating session state with the answer.

    Args:
        question: The user's natural-language question.
    """
    try:
        if not st.session_state.video_processed or not st.session_state.current_video_id:
            st.warning("⚠️ Please process a video before asking questions.")
            return

        with st.spinner("Retrieving relevant transcript sections..."):
            retrieved_chunks = query_video_chunks(
                video_id=st.session_state.current_video_id,
                question=question,
            )

        with st.spinner("Generating answer..."):
            answer = answer_question(retrieved_chunks, question)

        st.session_state.last_question = question
        st.session_state.last_answer = answer
        st.session_state.last_retrieved_chunks = retrieved_chunks

    except EmptyQuestionError as exc:
        st.warning(f"⚠️ {str(exc)}")
    except EmbeddingGenerationError as exc:
        st.error(f"⚠️ {str(exc)}")
    except VectorStoreError as exc:
        st.error(f"⚠️ {str(exc)}")
    except LLMGenerationError as exc:
        st.error(f"⚠️ {str(exc)}")
    except Exception as exc:  # noqa: BLE001 - final safety net for unexpected errors
        st.error(f"⚠️ An unexpected error occurred: {str(exc)}")


# ---------------------------------------------------------------------------
# UI Sections
# ---------------------------------------------------------------------------
def render_video_input_section() -> None:
    """Render the YouTube URL input and processing trigger."""
    st.markdown('<div class="va-section-label">§1 — Submit a Lecture</div>', unsafe_allow_html=True)

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


def render_status_section() -> None:
    """Render processing stats once a video has been successfully processed."""
    if not st.session_state.video_processed:
        return

    st.markdown('<div class="va-section-label">§2 — Transcript Digest</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="va-card">
            <div class="va-stat-row">
                <div class="va-stat">
                    <span class="va-stat-num">{st.session_state.num_chunks}</span>
                    <span class="va-stat-label">Chunks Indexed</span>
                </div>
                <div class="va-stat">
                    <span class="va-stat-num">{st.session_state.transcript_length:,}</span>
                    <span class="va-stat-label">Characters Transcribed</span>
                </div>
                <div class="va-stat">
                    <span class="va-stat-num">{st.session_state.current_video_id}</span>
                    <span class="va-stat-label">Video ID</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.success("✅ Transcript processed and indexed. Ready for questions.")


def render_question_section() -> None:
    """Render the question input, ask button, and answer display."""
    if not st.session_state.video_processed:
        return

    st.markdown('<hr class="va-divider" />', unsafe_allow_html=True)
    st.markdown('<div class="va-section-label">§3 — Ask the Transcript</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
    with col1:
        question = st.text_input(
            "Your question",
            placeholder="What does the speaker say about...?",
            label_visibility="collapsed",
            key="question_input",
        )
    with col2:
        ask_clicked = st.button("Ask", use_container_width=True)

    if ask_clicked:
        handle_question(question)

    if st.session_state.last_answer:
        st.markdown(
            f"""
            <div class="va-answer-box">
                <strong>Q:</strong> {st.session_state.last_question}<br><br>
                {st.session_state.last_answer}
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("View retrieved transcript excerpts"):
            for i, chunk in enumerate(st.session_state.last_retrieved_chunks, start=1):
                st.markdown(f"**Excerpt {i}:**")
                st.write(chunk)
                st.markdown("---")


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------
def main() -> None:
    """Application entry point."""
    inject_custom_css()
    initialize_session_state()
    render_masthead()

    st.write("")  # spacing
    render_video_input_section()
    render_status_section()
    render_summary_section()
    render_question_section()


if __name__ == "__main__":
    main()