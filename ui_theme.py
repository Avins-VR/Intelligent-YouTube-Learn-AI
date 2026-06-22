"""
ui_theme.py

Shared visual identity for the AI-Powered Educational Video Learning
Assistant: CSS injection and the top "Stage Rail" navigation bar used
on every page, plus small reusable HTML component helpers.

Design direction — "Night Study, Stage Rail":
A premium, fully dark study console (no white surfaces anywhere). The
five learning stages — Learn, Key Notes, Doubt Clarification, MCQ
Assessment, Learning Path — are a genuine sequence a student moves
through for a single video, so the navbar is built as a literal
numbered rail/pipeline rather than a generic pill-tab bar: a thin
progress line runs beneath five numbered nodes, lit up as you advance.

Palette:
    --bg          #11141c  deep graphite-blue base
    --panel       #181c27  card / panel surface
    --panel-raised#1f2433  inputs, hover states, navbar
    --hairline    #2b3142  borders / dividers
    --text        #e9e7df  warm off-white body text (never pure white)
    --text-dim    #9aa0b4  muted secondary text
    --violet      #7c6cf0  primary accent (active state, primary actions)
    --ember       #ff8a4c  secondary accent (progress / highlights)
    --sage        #6fcf97  success / correct
    --rose        #ef6f6f  error / incorrect

Typography: Space Grotesk (display), Inter (body), JetBrains Mono
(stage numbers, labels, data).
"""

from typing import Dict, List, Optional

import streamlit as st


FONT_IMPORT = (
    "https://fonts.googleapis.com/css2?"
    "family=Space+Grotesk:wght@500;600;700&"
    "family=Inter:wght@400;500;600;700&"
    "family=JetBrains+Mono:wght@400;500;600&display=swap"
)

# ---------------------------------------------------------------------------
# The five learning stages, in order. Numbered markers are justified here
# because the content genuinely is a sequence a student progresses through.
# ---------------------------------------------------------------------------

STAGES: List[Dict[str, str]] = [
    {"key": "learn", "num": "01", "label": "Learn", "icon": ":material/play_circle:"},
    {"key": "notes", "num": "02", "label": "Key Notes", "icon": ":material/sticky_note_2:"},
    {"key": "doubt", "num": "03", "label": "Doubt Clarification", "icon": ":material/forum:"},
    {"key": "mcq", "num": "04", "label": "MCQ Assessment", "icon": ":material/quiz:"},
    {"key": "path", "num": "05", "label": "Learning Path", "icon": ":material/route:"},
    {"key": "concept_map", "num": "06", "label": "Concept Map", "icon": ":material/account_tree:"},
]

def inject_global_css() -> None:
    """Inject the shared dark design system CSS. Safe to call once per run."""
    st.markdown(
        f"""
        <style>
        @import url('{FONT_IMPORT}');

        :root {{
            --bg: #11141c;
            --panel: #181c27;
            --panel-raised: #1f2433;
            --hairline: #2b3142;
            --hairline-soft: #232838;
            --text: #e9e7df;
            --text-dim: #9aa0b4;
            --violet: #7c6cf0;
            --violet-dim: #4d44a0;
            --ember: #ff8a4c;
            --ember-soft: rgba(255, 138, 76, 0.14);
            --sage: #6fcf97;
            --sage-soft: rgba(111, 207, 151, 0.12);
            --rose: #ef6f6f;
            --rose-soft: rgba(239, 111, 111, 0.12);
            --violet-soft: rgba(124, 108, 240, 0.14);
        }}

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: var(--text);
        }}

        .stApp {{
            background-color: var(--bg);
            background-image:
                radial-gradient(circle at 12% 0%, rgba(124,108,240,0.10), transparent 38%),
                radial-gradient(circle at 88% 8%, rgba(255,138,76,0.06), transparent 32%);
        }}

        header[data-testid="stHeader"] {{
            background: var(--bg);
        }}
        [data-testid="stToolbar"] {{ right: 1rem; }}
        [data-testid="stSidebarNav"],
        section[data-testid="stSidebar"],
        [data-testid="collapsedControl"] {{
            display: none !important;
        }}
        footer {{ visibility: hidden; }}

        .block-container {{
            max-width: 1180px;
            padding-top: 1.1rem;
            padding-bottom: 3rem;
        }}

        h1, h2, h3, h4 {{
            font-family: 'Space Grotesk', sans-serif;
            color: var(--text);
            letter-spacing: -0.01em;
        }}
        p, span, li, label {{ color: var(--text); }}
        .stMarkdown p {{ color: var(--text-dim); }}

        /* ---------------- Brand strip ---------------- */
        .ed-brand-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.2rem 0.1rem 0.9rem 0.1rem;
        }}
        .ed-brand {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 1.3rem;
            color: var(--text);
            letter-spacing: -0.01em;
        }}
        .ed-brand-mark {{
            color: var(--ember);
        }}
        .ed-brand-tagline {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--text-dim);
            margin-top: 0.1rem;
        }}
        .ed-status-pill {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.04em;
            padding: 0.32rem 0.75rem;
            border-radius: 999px;
            border: 1px solid var(--hairline);
            background: var(--panel);
            color: var(--text-dim);
        }}
        .ed-status-pill.ready {{
            border-color: rgba(111,207,151,0.35);
            color: var(--sage);
            background: var(--sage-soft);
        }}
        .ed-status-dot {{
            display: inline-block;
            width: 7px; height: 7px;
            border-radius: 50%;
            margin-right: 0.4rem;
            background: currentColor;
        }}

        /* ---------------- Stage rail (decorative line + nodes) ---------------- */
        .ed-rail {{
            display: flex;
            align-items: center;
            margin-bottom: 0.35rem;
        }}
        .ed-rail-step {{
            flex: 1;
            display: flex;
            align-items: center;
        }}
        .ed-rail-connector {{
            flex: 1;
            height: 2px;
            background: var(--hairline);
        }}
        .ed-rail-connector.filled {{
            background: linear-gradient(90deg, var(--ember), var(--violet));
        }}
        .ed-rail-connector.spacer {{
            background: transparent;
        }}
        .ed-rail-node {{
            width: 34px; height: 34px;
            min-width: 34px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
            font-weight: 600;
            border: 1.5px solid var(--hairline);
            background: var(--panel);
            color: var(--text-dim);
        }}
        .ed-rail-node.done {{
            border-color: var(--ember);
            color: var(--ember);
            background: var(--ember-soft);
        }}
        .ed-rail-node.active {{
            border-color: var(--violet);
            color: var(--text);
            background: var(--violet);
            box-shadow: 0 0 0 4px var(--violet-soft);
        }}

        /* labels row beneath the rail (built from real st.page_link / markdown) */
        .ed-rail-labels {{ margin-bottom: 1.4rem; }}
        div[data-testid="stPageLink"] {{
            display: flex;
            justify-content: center;
        }}
        div[data-testid="stPageLink"] a {{
            font-family: 'Inter', sans-serif;
            font-size: 0.82rem;
            font-weight: 500;
            color: var(--text-dim) !important;
            text-decoration: none !important;
            padding: 0.15rem 0;
            border-bottom: 2px solid transparent;
            transition: color 0.15s ease, border-color 0.15s ease;
        }}
        div[data-testid="stPageLink"] a:hover {{
            color: var(--text) !important;
            border-color: var(--ember);
        }}
        div[data-testid="stPageLink"] a p {{ color: inherit !important; font-size: 0.82rem; }}
        .ed-rail-label-active {{
            display: block;
            text-align: center;
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--text);
            border-bottom: 2px solid var(--violet);
            padding-bottom: 0.15rem;
        }}

        /* ---------------- Section label ---------------- */
        .ed-section-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--ember);
            margin: 1.4rem 0 0.7rem 0;
            font-weight: 600;
        }}

        /* ---------------- Cards ---------------- */
        .ed-card {{
            background: var(--panel);
            border: 1px solid var(--hairline);
            border-radius: 14px;
            padding: 1.3rem 1.5rem;
        }}
        .ed-card + .ed-card {{ margin-top: 0.9rem; }}

        /* ---------------- Stat tiles ---------------- */
        .ed-stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 0.9rem;
        }}
        .ed-stat-tile {{
            background: var(--panel);
            border: 1px solid var(--hairline);
            border-radius: 14px;
            padding: 1.1rem 1.2rem;
        }}
        .ed-stat-icon {{ font-size: 1.25rem; }}
        .ed-stat-value {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 1.5rem;
            color: var(--text);
            display: block;
            margin-top: 0.35rem;
        }}
        .ed-stat-label {{
            font-size: 0.76rem;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        /* ---------------- Notes ---------------- */
        .ed-note-card {{
            background: var(--panel);
            border: 1px solid var(--hairline);
            border-left: 3px solid var(--ember);
            border-radius: 10px;
            padding: 0.75rem 1.1rem;
            margin-bottom: 0.6rem;
            font-size: 0.97rem;
            line-height: 1.5;
            color: var(--text);
        }}

        /* ---------------- Summary text ---------------- */
        .ed-summary-text {{
            font-size: 1.0rem;
            line-height: 1.85;
            color: var(--text-dim);
        }}
        .ed-summary-text h1, .ed-summary-text h2, .ed-summary-text h3 {{
            color: var(--text);
            margin-top: 1.3rem;
        }}

        /* ---------------- Chat bubbles ---------------- */
        .ed-chat-scroll {{
            max-height: 58vh;
            overflow-y: auto;
            padding: 0.4rem 0.2rem;
        }}
        .ed-bubble-row {{ display: flex; margin-bottom: 0.7rem; }}
        .ed-bubble-row.user {{ justify-content: flex-end; }}
        .ed-bubble {{
            max-width: 78%;
            padding: 0.7rem 1.0rem;
            border-radius: 14px;
            font-size: 0.96rem;
            line-height: 1.5;
        }}
        .ed-bubble.user {{
            background: var(--violet);
            color: #11141c !important;
            border-bottom-right-radius: 4px;
        }}
        .ed-bubble.user * {{ color: #11141c !important; }}
        .ed-bubble.assistant {{
            background: var(--panel);
            border: 1px solid var(--hairline);
            color: var(--text);
            border-bottom-left-radius: 4px;
        }}
        .ed-bubble-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.66rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            opacity: 0.6;
            margin-bottom: 0.25rem;
            display: block;
        }}

        /* ---------------- MCQ cards ---------------- */
        .ed-mcq-card {{
            background: var(--panel);
            border: 1px solid var(--hairline);
            border-radius: 14px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 1rem;
        }}
        .ed-mcq-qnum {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            color: var(--ember);
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }}
        .ed-mcq-question {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.08rem;
            font-weight: 600;
            color: var(--text);
            margin: 0.3rem 0 0.8rem 0;
        }}
        .ed-mcq-option {{
            border: 1px solid var(--hairline);
            border-radius: 9px;
            padding: 0.55rem 0.9rem;
            margin-bottom: 0.5rem;
            font-size: 0.93rem;
            color: var(--text-dim);
        }}
        .ed-mcq-option.correct {{
            border-color: var(--sage);
            background: var(--sage-soft);
            color: var(--sage);
        }}
        .ed-mcq-option.incorrect {{
            border-color: var(--rose);
            background: var(--rose-soft);
            color: var(--rose);
        }}
        .ed-mcq-explanation {{
            font-size: 0.9rem;
            color: var(--text-dim);
            background: var(--panel-raised);
            border-radius: 9px;
            padding: 0.7rem 0.9rem;
            margin-top: 0.5rem;
        }}

        /* ---------------- Learning path timeline ---------------- */
        .ed-path-node {{
            display: flex;
            gap: 1rem;
            padding-bottom: 1.6rem;
            position: relative;
        }}
        .ed-path-node:not(:last-child)::before {{
            content: "";
            position: absolute;
            left: 17px;
            top: 36px;
            bottom: 0;
            width: 2px;
            background: linear-gradient(180deg, var(--ember), var(--hairline));
        }}
        .ed-path-num {{
            min-width: 36px; height: 36px;
            border-radius: 50%;
            background: var(--panel);
            border: 1.5px solid var(--ember);
            color: var(--ember);
            display: flex; align-items: center; justify-content: center;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            font-size: 0.85rem;
            z-index: 1;
        }}
        .ed-path-topic {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600;
            font-size: 1.05rem;
            color: var(--text);
        }}
        .ed-path-reason {{
            font-size: 0.93rem;
            color: var(--text-dim);
            margin-top: 0.25rem;
            line-height: 1.55;
        }}

        /* ---------------- Buttons ---------------- */
        .stButton > button {{
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            background: linear-gradient(135deg, var(--violet), var(--violet-dim));
            color: #0d0f16;
            border-radius: 10px;
            border: none;
            padding: 0.55rem 1.3rem;
            transition: filter 0.15s ease;
        }}
        .stButton > button:hover {{
            filter: brightness(1.12);
            background: linear-gradient(135deg, var(--ember), var(--violet));
            color: #0d0f16;
        }}
        .stButton > button p {{ color: #0d0f16 !important; font-weight: 600; }}

        /* ---------------- Inputs ---------------- */
        .stTextInput input, .stTextArea textarea,
        .stNumberInput input {{
            background: var(--panel-raised) !important;
            border: 1px solid var(--hairline) !important;
            border-radius: 10px !important;
            color: var(--text) !important;
            font-family: 'Inter', sans-serif;
        }}
        .stTextInput input::placeholder, .stTextArea textarea::placeholder {{
            color: var(--text-dim) !important;
        }}
        .stTextInput input:focus, .stTextArea textarea:focus {{
            border-color: var(--ember) !important;
            box-shadow: 0 0 0 1px var(--ember) !important;
        }}

        div[data-baseweb="select"] > div {{
            background: var(--panel-raised) !important;
            border-color: var(--hairline) !important;
            color: var(--text) !important;
            border-radius: 10px !important;
        }}
        div[data-baseweb="popover"] [role="listbox"],
        ul[data-baseweb="menu"] {{
            background: var(--panel-raised) !important;
            border: 1px solid var(--hairline) !important;
        }}
        li[role="option"] {{ color: var(--text) !important; }}
        li[role="option"]:hover, li[aria-selected="true"] {{
            background: var(--violet-soft) !important;
        }}

        input[type="radio"], input[type="checkbox"] {{ accent-color: var(--violet); }}
        .stRadio label, .stCheckbox label {{ color: var(--text) !important; }}

        /* ---------------- Status / expander / alerts ---------------- */
        div[data-testid="stStatusWidget"], [data-testid="stExpander"] {{
            background: var(--panel) !important;
            border: 1px solid var(--hairline) !important;
            border-radius: 12px !important;
        }}
        [data-testid="stExpander"] summary {{ color: var(--text) !important; }}

        div[data-testid="stAlert"] {{
            border-radius: 10px !important;
            background: var(--panel) !important;
            border: 1px solid var(--hairline) !important;
            color: var(--text) !important;
        }}
        div[data-testid="stAlertContentSuccess"] {{ color: var(--sage) !important; }}
        div[data-testid="stAlertContentError"] {{ color: var(--rose) !important; }}
        div[data-testid="stAlertContentWarning"] {{ color: var(--ember) !important; }}
        div[data-testid="stAlertContentInfo"] {{ color: var(--violet) !important; }}

        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: var(--bg); }}
        ::-webkit-scrollbar-thumb {{ background: var(--hairline); border-radius: 8px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--violet-dim); }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_top_navbar(active_key: str, nav_pages: Dict[str, "st.Page"]) -> None:
    """
    Render the shared "Stage Rail" top navigation: a brand strip, a
    decorative numbered progress line, and a row of real clickable
    page links beneath it (the active stage is shown as static text).

    Args:
        active_key: key of the currently active stage (matches STAGES[i]["key"]).
        nav_pages: mapping of stage key -> st.Page object, used to build
            real st.page_link navigation for the non-active stages.
    """
    active_index = next((i for i, s in enumerate(STAGES) if s["key"] == active_key), 0)

    video_ready = bool(st.session_state.get("video_processed"))
    pill_class = "ed-status-pill ready" if video_ready else "ed-status-pill"
    pill_text = "Video ready" if video_ready else "No video processed yet"

    st.markdown(
        f"""
        <div class="ed-brand-row">
            <div>
                <div class="ed-brand">Lumen<span class="ed-brand-mark">.</span>Learn</div>
                <div class="ed-brand-tagline">AI Video Learning Assistant</div>
            </div>
            <div class="{pill_class}"><span class="ed-status-dot"></span>{pill_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Decorative progress rail (line + numbered nodes)
    rail_html = ['<div class="ed-rail">']
    for i, stage in enumerate(STAGES):
        if i > 0:
            connector_state = "filled" if i <= active_index else "spacer"
            rail_html.append(f'<div class="ed-rail-connector {connector_state}"></div>')
        node_state = "active" if i == active_index else ("done" if i < active_index else "")
        rail_html.append(f'<div class="ed-rail-node {node_state}">{stage["num"]}</div>')
    rail_html.append("</div>")
    st.markdown("".join(rail_html), unsafe_allow_html=True)

    # Real clickable labels beneath the rail
    cols = st.columns(len(STAGES))
    for i, (col, stage) in enumerate(zip(cols, STAGES)):
        with col:
            if stage["key"] == active_key:
                st.markdown(
                    f'<span class="ed-rail-label-active">{stage["label"]}</span>',
                    unsafe_allow_html=True,
                )
            else:
                page = nav_pages.get(stage["key"])
                if page is not None:
                    st.page_link(page, label=stage["label"])

    st.markdown('<div class="ed-rail-labels"></div>', unsafe_allow_html=True)


def render_section_label(label: str) -> None:
    """Render a small uppercase mono section label (ember accent)."""
    st.markdown(f'<div class="ed-section-label">{label}</div>', unsafe_allow_html=True)


def render_no_video_notice(page_name: str) -> None:
    """Render a friendly empty-state notice when no video has been processed yet."""
    st.markdown(
        f"""
        <div class="ed-card">
            <p style="margin:0; color: var(--text-dim);">
                No video has been processed yet. Head to <strong style="color:var(--text);">Learn</strong>,
                paste a YouTube URL, and come back to {page_name} once it's done.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_grid(stats):
    cols = st.columns(len(stats))

    for col, stat in zip(cols, stats):
        with col:
            st.markdown(
                f"""
                <div class="ed-stat-tile">
                    <div class="ed-stat-icon">{stat['icon']}</div>
                    <div class="ed-stat-value">{stat['value']}</div>
                    <div class="ed-stat-label">{stat['label']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_question_card_header(qnum: int, question: str) -> None:
    """Render the question number + question text header for an MCQ card."""
    st.markdown(
        f"""
        <div class="ed-mcq-qnum">Question {qnum}</div>
        <div class="ed-mcq-question">{question}</div>
        """,
        unsafe_allow_html=True,
    )


def render_path_node(num: int, topic: str, reason: str) -> None:
    """Render one node of the learning-path timeline."""
    st.markdown(
        f"""
        <div class="ed-path-node">
            <div class="ed-path-num">{num:02d}</div>
            <div>
                <div class="ed-path-topic">{topic}</div>
                <div class="ed-path-reason">{reason}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )