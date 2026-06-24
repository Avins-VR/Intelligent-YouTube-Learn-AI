"""
ui_theme.py

Shared visual identity for the AI-Powered Educational Video Learning
Assistant: CSS injection and the top "Stage Rail" navigation bar used
on every page, plus small reusable HTML component helpers.

Design direction — "Orbital SaaS": a premium, glassmorphic dark
dashboard inspired by Linear / Stripe Dashboard / Notion AI. Frosted
glass surfaces, a sticky glass navbar, soft elevation shadows, an
indigo→cyan accent gradient, and Material Symbols icons throughout
(no emoji anywhere in the UI).

Palette:
    --bg            #0a0c12  near-black base
    --bg-grid       subtle radial accent washes
    --glass         rgba(255,255,255,0.04)  glass panel fill
    --glass-strong  rgba(255,255,255,0.07)  raised glass (navbar, inputs)
    --border        rgba(255,255,255,0.09)  hairline borders
    --border-strong rgba(255,255,255,0.16)
    --text          #eef0f6  primary text
    --text-dim      #9aa1b5  secondary text
    --text-faint    #6b7184  tertiary text
    --indigo        #6e6bff  primary accent
    --cyan          #4fd1ff  secondary accent
    --grad          linear-gradient(135deg, var(--indigo), var(--cyan))
    --sage          #3ddc97  success
    --amber         #ffb454  warning / highlight
    --rose          #ff6b81  error / incorrect

Typography: Space Grotesk (display), Inter (body), JetBrains Mono
(data / labels), Material Symbols Outlined (icons).
"""

from typing import Dict, List, Optional

import streamlit as st


FONT_IMPORT = (
    "https://fonts.googleapis.com/css2?"
    "family=Space+Grotesk:wght@500;600;700&"
    "family=Inter:wght@400;500;600;700&"
    "family=JetBrains+Mono:wght@400;500;600&"
    "family=Material+Symbols+Outlined:opsz,wght,fill,GRAD@20,400,0,0&display=swap"
)

# ---------------------------------------------------------------------------
# The six learning stages, in order. Numbered markers are justified here
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


def render_icon(name: str, size: str = "20px") -> str:
    """Return a Material Symbols icon span for use inside raw HTML blocks."""
    return f'<span class="msi" style="font-size:{size};">{name}</span>'


def inject_global_css() -> None:
    """Inject the shared premium glassmorphic design system CSS. Safe to call once per run."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');

        :root {{
            --bg: #0a0c12;
            --glass: rgba(255,255,255,0.04);
            --glass-strong: rgba(255,255,255,0.07);
            --glass-hover: rgba(255,255,255,0.10);
            --border: rgba(255,255,255,0.09);
            --border-strong: rgba(255,255,255,0.18);
            --text: #eef0f6;
            --text-dim: #9aa1b5;
            --text-faint: #6b7184;
            --indigo: #6e6bff;
            --indigo-dim: #4a47b8;
            --cyan: #4fd1ff;
            --sage: #3ddc97;
            --sage-soft: rgba(61,220,151,0.12);
            --amber: #ffb454;
            --amber-soft: rgba(255,180,84,0.12);
            --rose: #ff6b81;
            --rose-soft: rgba(255,107,129,0.12);
            --indigo-soft: rgba(110,107,255,0.14);
            --grad: linear-gradient(135deg, var(--indigo), var(--cyan));
            --shadow-sm: 0 2px 10px rgba(0,0,0,0.25);
            --shadow-md: 0 10px 30px rgba(0,0,0,0.35);
            --shadow-glow: 0 0 0 1px rgba(110,107,255,0.25), 0 8px 24px rgba(110,107,255,0.18);
            --radius: 16px;
            --radius-sm: 10px;
        }}

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: var(--text);
        }}

        .msi {{
            font-family: 'Material Symbols Outlined';
            font-weight: normal;
            font-style: normal;
            line-height: 1;
            letter-spacing: normal;
            text-transform: none;
            display: inline-block;
            white-space: nowrap;
            direction: ltr;
            -webkit-font-feature-settings: 'liga';
            vertical-align: middle;
        }}

        .stApp {{
            background-color: var(--bg);
            background-image:
                radial-gradient(circle at 10% -5%, rgba(110,107,255,0.16), transparent 40%),
                radial-gradient(circle at 90% 0%, rgba(79,209,255,0.10), transparent 35%),
                radial-gradient(circle at 50% 100%, rgba(110,107,255,0.06), transparent 45%);
            background-attachment: fixed;
        }}

        header[data-testid="stHeader"] {{
            display: none !important;
        }}
        [data-testid="stToolbar"] {{ right: 1rem; }}
        [data-testid="stSidebarNav"],
        section[data-testid="stSidebar"],
        [data-testid="collapsedControl"] {{
            display: none !important;
        }}
        footer {{ visibility: hidden; }}

        .block-container {{
            max-width: 1600px;
            padding-top: 0rem !important;
            padding-bottom: 3.2rem;
        }}

        h1, h2, h3, h4 {{
            font-family: 'Space Grotesk', sans-serif;
            color: var(--text);
            letter-spacing: -0.01em;
        }}
        p, span, li, label {{ color: var(--text); }}
        .stMarkdown p {{ color: var(--text-dim); }}

        /* ---------------- Sticky glass navbar shell ---------------- */
        .ed-navbar-shell {{
            position: relative;
            margin: -0.6rem -0.2rem 1.4rem -0.2rem;
            padding: 0.8rem 1.3rem 0.9rem 1.3rem;
            background: transparent;
            border: none;
            border-radius: 0;
            box-shadow: none;
        }}

        .ed-brand-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 1.85rem;
        }}
        .ed-brand {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 1.25rem;
            color: var(--text);
            letter-spacing: -0.01em;
        }}
        .ed-brand-icon {{
            display: flex;
            position: relative;
            top: 12px;
            right: 6px;
            align-items: center;
            justify-content: center;
            width: 42px; height: 42px;
            border-radius: 9px;
            background: var(--grad);
            box-shadow: var(--shadow-glow);
        }}
        .ed-brand-icon .msi {{ color: #0a0c12; font-size: 19px; }}
        .ed-brand-tagline {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.66rem;
            letter-spacing: 0.09em;
            text-transform: uppercase;
            color: var(--text-faint);
            margin-top: 0.15rem;
            margin-left: 3rem;
        }}
        .ed-status-pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            letter-spacing: 0.04em;
            padding: 0.4rem 0.85rem;
            border-radius: 999px;
            border: 1px solid var(--border);
            background: var(--glass);
            color: var(--text-dim);
        }}
        .ed-status-pill.ready {{
            border-color: rgba(61,220,151,0.35);
            color: var(--sage);
            background: var(--sage-soft);
        }}
        .ed-status-pill .msi {{ font-size: 15px; }}

        /* ---------------- Stage rail ---------------- */
        .ed-rail {{
            display: flex;
            align-items: center;
            margin-bottom: 0.5rem;
        }}
        .ed-rail-connector {{
            flex: 1;
            height: 2px;
            background: var(--border);
            border-radius: 2px;
        }}
        .ed-rail-connector.filled {{ background: var(--grad); }}
        .ed-rail-connector.spacer {{ background: var(--border); opacity: 0.4; }}
        .ed-rail-node {{
            width: 32px; height: 32px;
            min-width: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.74rem;
            font-weight: 600;
            border: 1.5px solid var(--border);
            background: var(--glass);
            color: var(--text-faint);
            transition: all 0.2s ease;
        }}
        .ed-rail-node.done {{
            border-color: var(--cyan);
            color: var(--cyan);
            background: rgba(79,209,255,0.10);
        }}
        .ed-rail-node.active {{
            border-color: transparent;
            color: #0a0c12;
            background: var(--grad);
            box-shadow: var(--shadow-glow);
        }}

        .ed-rail-labels {{ margin-bottom: 0.1rem; }}
        div[data-testid="stPageLink"] {{ display: flex; justify-content: center; }}
        div[data-testid="stPageLink"] a {{
            font-family: 'Inter', sans-serif;
            font-size: 0.8rem;
            font-weight: 500;
            color: var(--text-faint) !important;
            text-decoration: none !important;
            padding: 0.2rem 0.3rem;
            border-radius: 7px;
            border-bottom: 2px solid transparent;
            transition: color 0.15s ease, background 0.15s ease;
        }}
        div[data-testid="stPageLink"] a:hover {{
            color: var(--text) !important;
            background: var(--glass-hover);
            border-color: var(--cyan);
        }}
        div[data-testid="stPageLink"] a p {{ color: inherit !important; font-size: 0.8rem; }}
        .ed-rail-label-active {{
            display: block;
            text-align: center;
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text);
            padding: 0.2rem 0.3rem;
            border-bottom: 2px solid var(--indigo);
        }}

        /* ---------------- Section label ---------------- */
        .ed-section-label {{
            display: flex;
            align-items: center;
            gap: 0.45rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--cyan);
            margin: 1.5rem 0 0.8rem 0;
            font-weight: 600;
        }}
        .ed-section-label .msi {{ font-size: 16px; }}

        /* ---------------- Glass cards ---------------- */
        .ed-card {{
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1.4rem 1.6rem;
            backdrop-filter: blur(8px);
            box-shadow: var(--shadow-sm);
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }}
        .ed-card:hover {{ border-color: var(--border-strong); }}
        .ed-card + .ed-card {{ margin-top: 0.9rem; }}

        /* ---------------- Stat / KPI tiles ---------------- */
        .ed-stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
            gap: 1rem;
        }}
        .ed-stat-tile {{
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1.2rem 1.3rem;
            display: flex;
            align-items: flex-start;
            gap: 0.9rem;
            transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
        }}
        .ed-stat-tile:hover {{
            transform: translateY(-2px);
            border-color: var(--border-strong);
            box-shadow: var(--shadow-md);
        }}
        .ed-stat-icon-wrap {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 38px; height: 38px;
            min-width: 38px;
            border-radius: 10px;
            background: var(--indigo-soft);
        }}
        .ed-stat-icon-wrap .msi {{ font-size: 20px; color: var(--indigo); }}
        .ed-stat-value {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 1.45rem;
            color: var(--text);
            display: block;
            line-height: 1.1;
        }}
        .ed-stat-label {{
            font-size: 0.74rem;
            color: var(--text-faint);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 0.2rem;
        }}

        /* ---------------- Notes ---------------- */
        .ed-note-card {{
            background: var(--glass);
            border: 1px solid var(--border);
            border-left: 3px solid var(--cyan);
            border-radius: var(--radius-sm);
            padding: 0.85rem 1.2rem;
            margin-bottom: 0.65rem;
            font-size: 0.97rem;
            line-height: 1.55;
            color: var(--text);
            display: flex;
            gap: 0.6rem;
        }}
        .ed-note-card .msi {{ font-size: 17px; color: var(--cyan); margin-top: 0.15rem; }}

        /* ---------------- Summary text ---------------- */
        .ed-summary-text {{ font-size: 1.0rem; line-height: 1.85; color: var(--text-dim); }}
        .ed-summary-text h1, .ed-summary-text h2, .ed-summary-text h3 {{ color: var(--text); margin-top: 1.3rem; }}

        /* ---------------- Chat bubbles ---------------- */
        .ed-chat-scroll {{ max-height: 58vh; overflow-y: auto; padding: 0.4rem 0.2rem; }}
        .ed-bubble-row {{ display: flex; margin-bottom: 0.8rem; }}
        .ed-bubble-row.user {{ justify-content: flex-end; }}
        .ed-bubble {{
            max-width: 78%;
            padding: 0.8rem 1.05rem;
            border-radius: 14px;
            font-size: 0.96rem;
            line-height: 1.55;
            box-shadow: var(--shadow-sm);
        }}
        .ed-bubble.user {{
            background: var(--grad);
            color: #0a0c12 !important;
            border-bottom-right-radius: 4px;
        }}
        .ed-bubble.user * {{ color: #0a0c12 !important; }}
        .ed-bubble.assistant {{
            background: var(--glass-strong);
            border: 1px solid var(--border);
            color: var(--text);
            border-bottom-left-radius: 4px;
        }}
        .ed-bubble-label {{
            display: flex;
            align-items: center;
            gap: 0.3rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.64rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            opacity: 0.65;
            margin-bottom: 0.3rem;
        }}
        .ed-bubble-label .msi {{ font-size: 13px; }}

        /* ---------------- MCQ cards ---------------- */
        .ed-mcq-card {{
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1.3rem 1.5rem;
            margin-bottom: 1.05rem;
            box-shadow: var(--shadow-sm);
        }}
        .ed-mcq-qnum {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            color: var(--cyan);
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }}
        .ed-mcq-question {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.08rem;
            font-weight: 600;
            color: var(--text);
            margin: 0.3rem 0 0.9rem 0;
        }}
        .ed-mcq-option {{
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 0.6rem 0.95rem;
            margin-bottom: 0.5rem;
            font-size: 0.93rem;
            color: var(--text-dim);
            background: rgba(255,255,255,0.015);
            transition: border-color 0.15s ease;
        }}
        .ed-mcq-option.correct {{ border-color: var(--sage); background: var(--sage-soft); color: var(--sage); }}
        .ed-mcq-option.incorrect {{ border-color: var(--rose); background: var(--rose-soft); color: var(--rose); }}
        .ed-mcq-explanation {{
            font-size: 0.9rem;
            color: var(--text-dim);
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 0.75rem 0.95rem;
            margin-top: 0.6rem;
        }}
        .ed-difficulty-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            padding: 0.25rem 0.65rem;
            border-radius: 999px;
            border: 1px solid var(--border);
            color: var(--text-dim);
            margin-bottom: 0.4rem;
        }}
        .ed-diff-dot {{ width: 7px; height: 7px; border-radius: 50%; background: currentColor; }}
        .ed-difficulty-badge.easy {{ color: var(--sage); border-color: rgba(61,220,151,0.3); background: var(--sage-soft); }}
        .ed-difficulty-badge.medium {{ color: var(--amber); border-color: rgba(255,180,84,0.3); background: var(--amber-soft); }}
        .ed-difficulty-badge.hard {{ color: var(--rose); border-color: rgba(255,107,129,0.3); background: var(--rose-soft); }}

        .ed-group-header {{
            display: flex;
            align-items: center;
            gap: 0.55rem;
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600;
            font-size: 1.05rem;
            color: var(--text);
            margin: 1.4rem 0 0.9rem 0;
        }}
        .ed-group-header .ed-diff-dot {{ width: 9px; height: 9px; }}
        .ed-group-header.easy .ed-diff-dot {{ background: var(--sage); }}
        .ed-group-header.medium .ed-diff-dot {{ background: var(--amber); }}
        .ed-group-header.hard .ed-diff-dot {{ background: var(--rose); }}

        /* ---------------- Learning path timeline ---------------- */
        .ed-path-node {{ display: flex; gap: 2rem; padding-bottom: 1.7rem; position: relative; }}
        .ed-path-node:not(:last-child)::before {{
            content: "";
            position: absolute;
            left: 18px; top: 38px; bottom: 0;
            width: 2px;
            background: linear-gradient(180deg, var(--indigo), transparent);
        }}
        .ed-path-content {{
            margin-top: 2rem;
        }}
        .ed-path-num {{
            min-width: 38px; height: 38px;
            border-radius: 50%;
            margin-top: 2rem;
            background: var(--glass-strong);
            border: 1.5px solid var(--indigo);
            color: var(--indigo);
            display: flex; align-items: center; justify-content: center;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            font-size: 0.85rem;
            z-index: 1;
            box-shadow: 0 0 0 4px rgba(110,107,255,0.08);
        }}
        .ed-path-topic {{ font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 1.05rem; color: var(--text)}}
        .ed-path-reason {{ font-size: 0.93rem; color: var(--text-dim); margin-top: 0.3rem; line-height: 1.55; }}

        /* ---------------- Buttons ---------------- */
        .stButton > button {{
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            background: var(--grad);
            color: #0a0c12;
            border-radius: var(--radius-sm);
            border: none;
            padding: 0.6rem 1.3rem;
            box-shadow: var(--shadow-sm);
            transition: filter 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .stButton > button:hover {{
            filter: brightness(1.08);
            transform: translateY(-1px);
            box-shadow: var(--shadow-glow);
            color: #0a0c12;
        }}
        .stButton > button p {{ color: #0a0c12 !important; font-weight: 600; }}
        .stButton > button span[data-testid="stIconMaterial"] {{ color: #0a0c12 !important; }}

        .stDownloadButton > button {{
            background: var(--glass-strong) !important;
            color: var(--text) !important;
            border: 1px solid var(--border-strong) !important;
            border-radius: var(--radius-sm) !important;
            font-weight: 600;
            box-shadow: var(--shadow-sm);
        }}
        .stDownloadButton > button:hover {{ border-color: var(--cyan) !important; }}
        .stDownloadButton > button p {{ color: var(--text) !important; }}

        /* ---------------- Inputs ---------------- */
        .stTextInput input, .stTextArea textarea, .stNumberInput input {{
            background: var(--glass-strong) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-sm) !important;
            color: var(--text) !important;
            font-family: 'Inter', sans-serif;
        }}
        .stTextInput input::placeholder, .stTextArea textarea::placeholder {{ color: var(--text-faint) !important; }}
        .stTextInput input:focus, .stTextArea textarea:focus {{
            border-color: var(--cyan) !important;
            box-shadow: 0 0 0 1px var(--cyan) !important;
        }}

        div[data-baseweb="select"] > div {{
            background: var(--glass-strong) !important;
            border-color: var(--border) !important;
            color: var(--text) !important;
            border-radius: var(--radius-sm) !important;
        }}
        div[data-baseweb="popover"] [role="listbox"], ul[data-baseweb="menu"] {{
            background: #11141d !important;
            border: 1px solid var(--border) !important;
        }}
        li[role="option"] {{ color: var(--text) !important; }}
        li[role="option"]:hover, li[aria-selected="true"] {{ background: var(--indigo-soft) !important; }}

        input[type="radio"], input[type="checkbox"] {{ accent-color: var(--indigo); }}
        .stRadio label, .stCheckbox label {{ color: var(--text) !important; }}
        .stToggle label {{ color: var(--text) !important; }}

        /* ---------------- Status / expander / alerts ---------------- */
        div[data-testid="stStatusWidget"], [data-testid="stExpander"] {{
            background: var(--glass) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius) !important;
        }}
        [data-testid="stExpander"] summary {{ color: var(--text) !important; }}

        div[data-testid="stAlert"] {{
            border-radius: var(--radius-sm) !important;
            background: var(--glass) !important;
            border: 1px solid var(--border) !important;
            color: var(--text) !important;
            backdrop-filter: blur(6px);
        }}
        div[data-testid="stAlertContentSuccess"] {{ color: var(--sage) !important; }}
        div[data-testid="stAlertContentError"] {{ color: var(--rose) !important; }}
        div[data-testid="stAlertContentWarning"] {{ color: var(--amber) !important; }}
        div[data-testid="stAlertContentInfo"] {{ color: var(--cyan) !important; }}

        .stCaption, [data-testid="stCaptionContainer"] {{ color: var(--text-faint) !important; }}

        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: var(--bg); }}
        ::-webkit-scrollbar-thumb {{ background: var(--border-strong); border-radius: 8px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--indigo-dim); }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_top_navbar(active_key: str, nav_pages: Dict[str, "st.Page"]) -> None:
    """
    Render the shared sticky glass "Stage Rail" top navigation: a brand
    strip, a decorative numbered progress line, and a row of real
    clickable page links beneath it (the active stage shown as static
    text).

    Args:
        active_key: key of the currently active stage (matches STAGES[i]["key"]).
        nav_pages: mapping of stage key -> st.Page object, used to build
            real st.page_link navigation for the non-active stages.
    """
    active_index = next((i for i, s in enumerate(STAGES) if s["key"] == active_key), 0)

    video_ready = bool(st.session_state.get("video_processed"))
    pill_class = "ed-status-pill ready" if video_ready else "ed-status-pill"
    pill_icon = "check_circle" if video_ready else "radio_button_unchecked"
    pill_text = "Video ready" if video_ready else "No video processed yet"

    st.markdown('<div class="ed-navbar-shell">', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="ed-brand-row">
            <div>
                <div class="ed-brand">
                    <span class="ed-brand-icon">{render_icon("auto_awesome", "20px")}</span>
                    Intelligent YouTube Learn AI
                </div>
                <div class="ed-brand-tagline">AI-Powered Educational Video Learning Assistant</div>
            </div>
            <div class="{pill_class}">{render_icon(pill_icon, "15px")}{pill_text}</div>
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
    st.markdown("</div>", unsafe_allow_html=True)  # close ed-navbar-shell


def render_section_label(label: str, icon: str = "bolt") -> None:
    """Render a small uppercase mono section label with a Material icon."""
    st.markdown(
        f'<div class="ed-section-label">{render_icon(icon, "15px")}{label}</div>',
        unsafe_allow_html=True,
    )


def render_no_video_notice(page_name: str) -> None:
    """Render a friendly empty-state notice when no video has been processed yet."""
    st.markdown(
        f"""
        <div class="ed-card">
            <p style="margin:0; color: var(--text-dim); display:flex; align-items:center; gap:0.6rem;">
                {render_icon("info", "20px")}
                No video has been processed yet. Head to <strong style="color:var(--text);">Learn</strong>,
                paste a YouTube URL, and come back to {page_name} once it's done.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_grid(stats) -> None:
    """
    Render a responsive grid of KPI tiles.

    Each stat dict expects: {"icon": <material icon name>, "value": str, "label": str}
    """
    cols = st.columns(len(stats))

    for col, stat in zip(cols, stats):
        with col:
            st.markdown(
                f"""
                <div class="ed-stat-tile">
                    <div class="ed-stat-icon-wrap">{render_icon(stat['icon'], "20px")}</div>
                    <div>
                        <div class="ed-stat-value">{stat['value']}</div>
                        <div class="ed-stat-label">{stat['label']}</div>
                    </div>
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


def render_difficulty_badge(difficulty: str) -> None:
    """Render a small colored badge for an MCQ's difficulty level."""
    css_class = (difficulty or "").strip().lower()
    if css_class not in ("easy", "medium", "hard"):
        css_class = ""
    st.markdown(
        f'<span class="ed-difficulty-badge {css_class}"><span class="ed-diff-dot"></span>{difficulty}</span>',
        unsafe_allow_html=True,
    )


def render_difficulty_group_header(title: str, css_class: str) -> None:
    """Render a section header for a grouped block of MCQs (Easy/Medium/Hard)."""
    st.markdown(
        f'<div class="ed-group-header {css_class}"><span class="ed-diff-dot"></span>{title}</div>',
        unsafe_allow_html=True,
    )


def render_path_node(num: int, topic: str, reason: str) -> None:
    """Render one node of the learning-path timeline."""
    st.markdown(
        f"""
        <div class="ed-path-node">
            <div class="ed-path-num">{num:02d}</div>
            <div class="ed-path-content">
                <div class="ed-path-topic">{topic}</div>
                <div class="ed-path-reason">{reason}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )