"""
ui_theme.py

Shared visual identity for the AI-Powered Educational Video Learning
Assistant: CSS injection and small reusable HTML component helpers used
by app.py and every page in pages/.

Design direction: a calm "study desk" dashboard — warm off-white surface,
deep indigo for structure, and a single amber accent reserved for the
one signature element (the active nav state / primary actions). Cards
are softly rounded with a hairline border rather than heavy shadows, so
dense study content (notes, chat, summaries) stays easy to scan.
"""

import streamlit as st


PRIMARY_FONT_IMPORT = (
    "https://fonts.googleapis.com/css2?"
    "family=Sora:wght@500;600;700&"
    "family=Inter:wght@400;500;600&"
    "family=JetBrains+Mono:wght@400;500&display=swap"
)


def inject_global_css() -> None:
    """Inject the shared design system CSS. Safe to call on every page."""
    st.markdown(
        f"""
        <style>
        @import url('{PRIMARY_FONT_IMPORT}');

        :root {{
            --ink: #1c2333;
            --surface: #f6f4ee;
            --card: #ffffff;
            --rule: #e4dfd2;
            --indigo: #2f3b63;
            --indigo-soft: #eef0f7;
            --amber: #d98e2b;
            --amber-soft: #fbeed9;
            --muted: #6b7280;
            --success: #2f7a4f;
        }}

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: var(--ink);
        }}

        .stApp {{
            background-color: var(--surface);
        }}

        section[data-testid="stSidebar"] {{
            background-color: var(--indigo);
        }}
        section[data-testid="stSidebar"] * {{
            color: #eef0f7 !important;
        }}
        section[data-testid="stSidebar"] .stRadio label {{
            font-family: 'Inter', sans-serif;
            font-size: 0.95rem;
        }}

        /* Header */
        .ed-header {{
            padding: 1.4rem 0 1.1rem 0;
            border-bottom: 1px solid var(--rule);
            margin-bottom: 1.4rem;
        }}
        .ed-header-title {{
            font-family: 'Sora', sans-serif;
            font-weight: 700;
            font-size: 2.0rem;
            margin: 0;
            color: var(--indigo);
            letter-spacing: -0.01em;
        }}
        .ed-header-subtitle {{
            font-size: 1.0rem;
            color: var(--muted);
            margin-top: 0.3rem;
        }}

        /* Section label */
        .ed-section-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--amber);
            margin: 1.2rem 0 0.7rem 0;
            font-weight: 500;
        }}

        /* Cards */
        .ed-card {{
            background: var(--card);
            border: 1px solid var(--rule);
            border-radius: 14px;
            padding: 1.3rem 1.5rem;
        }}
        .ed-card + .ed-card {{
            margin-top: 0.9rem;
        }}

        /* Stat tiles */
        .ed-stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 0.9rem;
        }}
        .ed-stat-tile {{
            background: var(--card);
            border: 1px solid var(--rule);
            border-radius: 14px;
            padding: 1.1rem 1.2rem;
        }}
        .ed-stat-icon {{
            font-size: 1.3rem;
        }}
        .ed-stat-value {{
            font-family: 'Sora', sans-serif;
            font-weight: 700;
            font-size: 1.5rem;
            color: var(--indigo);
            display: block;
            margin-top: 0.35rem;
        }}
        .ed-stat-label {{
            font-size: 0.78rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        /* Notes */
        .ed-note-card {{
            background: var(--amber-soft);
            border: 1px solid #efd9ad;
            border-radius: 12px;
            padding: 0.75rem 1.1rem;
            margin-bottom: 0.6rem;
            font-size: 0.97rem;
            line-height: 1.5;
        }}

        /* Summary text */
        .ed-summary-text {{
            font-size: 1.0rem;
            line-height: 1.85;
            color: var(--ink);
        }}
        .ed-summary-text p {{
            margin-bottom: 1rem;
        }}

        /* Chat bubbles */
        .ed-chat-scroll {{
            max-height: 55vh;
            overflow-y: auto;
            padding: 0.4rem 0.2rem;
        }}
        .ed-bubble-row {{
            display: flex;
            margin-bottom: 0.7rem;
        }}
        .ed-bubble-row.user {{
            justify-content: flex-end;
        }}
        .ed-bubble {{
            max-width: 78%;
            padding: 0.7rem 1.0rem;
            border-radius: 14px;
            font-size: 0.96rem;
            line-height: 1.5;
        }}
        .ed-bubble.user {{
            background: var(--indigo);
            color: #ffffff !important;
            border-bottom-right-radius: 4px;
        }}
        .ed-bubble.assistant {{
            background: var(--card);
            border: 1px solid var(--rule);
            color: var(--ink);
            border-bottom-left-radius: 4px;
        }}
        .ed-bubble-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            opacity: 0.65;
            margin-bottom: 0.25rem;
            display: block;
        }}

        /* Buttons */
        .stButton > button {{
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            background-color: var(--indigo);
            color: #ffffff;
            border-radius: 10px;
            border: none;
            padding: 0.55rem 1.3rem;
            transition: background-color 0.15s ease;
        }}
        .stButton > button:hover {{
            background-color: var(--amber);
            color: #1c2333;
        }}

        /* Inputs */
        .stTextInput > div > div > input,
        .stTextArea textarea {{
            border-radius: 10px;
            border: 1px solid var(--rule);
            font-family: 'Inter', sans-serif;
        }}
        .stTextInput > div > div > input:focus,
        .stTextArea textarea:focus {{
            border-color: var(--amber);
            box-shadow: 0 0 0 1px var(--amber);
        }}

        footer {{visibility: hidden;}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(title: str, subtitle: str) -> None:
    """Render the shared dashboard header used at the top of every page."""
    st.markdown(
        f"""
        <div class="ed-header">
            <p class="ed-header-title">{title}</p>
            <p class="ed-header-subtitle">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_label(label: str) -> None:
    """Render a small uppercase section label (mono, amber accent)."""
    st.markdown(f'<div class="ed-section-label">{label}</div>', unsafe_allow_html=True)


def render_no_video_notice(page_name: str) -> None:
    """Render a friendly empty-state notice when no video has been processed yet."""
    st.markdown(
        f"""
        <div class="ed-card">
            <p style="margin:0; color: var(--muted);">
                No video has been processed yet. Head to <strong>Process Video</strong>
                in the sidebar, paste a YouTube URL, and come back to {page_name}.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )