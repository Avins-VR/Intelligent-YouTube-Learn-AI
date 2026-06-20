"""
session_utils.py

Centralized Streamlit session state initialization, shared by app.py and
every page under pages/, so all parts of the app agree on the same keys.
"""

import streamlit as st


def initialize_session_state() -> None:
    """Ensure all required keys exist in Streamlit's session state."""
    defaults = {
        "current_video_id": None,
        "video_url": None,
        "transcript": None,
        "num_chunks": 0,
        "transcript_length": 0,
        "video_processed": False,
        "collection_name": None,

        "summary": None,
        "summary_generated": False,

        "notes": [],
        "notes_generated": False,

        "chat_history": [],

        "last_answer": None,
        "last_question": None,
        "last_retrieved_chunks": [],

        # Optional debugging
        "last_summary_chunks": [],
        "last_notes_chunks": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value