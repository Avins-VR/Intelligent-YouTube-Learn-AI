"""
pages/concept_map_page.py

Phase 4: Concept Map stage. Lets the user generate a hierarchical
concept map (Main Topic -> Major Concepts -> Sub Concepts) for the
currently processed video, rendered as an interactive Mermaid.js
diagram, plus simple concept statistics.

Reuses st.session_state.transcript / .summary / .notes that are
already populated by the existing Learn-stage pipeline in app.py -
no changes were made to that pipeline.
"""

import streamlit as st
import streamlit.components.v1 as components

from concept_map import generate_concept_map
from ui_theme import render_section_label, render_no_video_notice, render_stat_grid
from utils.exceptions import LLMGenerationError


def render_mermaid(mermaid_code: str, height: int = 1900) -> None:
    """Render Mermaid flowchart syntax as an interactive, scrollable
    diagram styled to match the app's dark theme."""
    html = f"""
    <div id="concept-map-wrapper">
      <div class="mermaid">
{mermaid_code}
      </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
    <script>
      mermaid.initialize({{
        startOnLoad: true,
        securityLevel: 'strict',
        theme: 'base',
        themeVariables: {{
          background: '#181c27',
          primaryColor: '#1f2433',
          primaryTextColor: '#e9e7df',
          primaryBorderColor: '#7c6cf0',
          lineColor: '#ff8a4c',
          secondaryColor: '#181c27',
          tertiaryColor: '#11141c',
          fontFamily: 'Inter, sans-serif',
          fontSize: '14px'
        }},
        flowchart: {{
          useMaxWidth: true,
          htmlLabels: false,
          curve: 'basis',
          nodeSpacing: 90,
          rankSpacing: 150
        }}
      }});
    </script>
    <style>
      html, body {{
        background: transparent;
        margin: 0;
        padding: 0;
      }}
      #concept-map-wrapper {{
        width: 100%;
        overflow: auto;
        background: #181c27;
        border: 1px solid #2b3142;
        border-radius: 14px;
        padding: 1.3rem;
        box-sizing: border-box;
      }}
      .mermaid {{
        display: flex;
        justify-content: center;
      }}
      .mermaid svg {{
        max-width: 100%;
        height: auto;
      }}
    </style>
    """
    components.html(html, height=height, scrolling=True)


def render_concept_map_page() -> None:
    if not st.session_state.video_processed:
        render_no_video_notice("Concept Map")
        return

    render_section_label("Concept Map")

    col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
    with col1:
        st.markdown(
            """
            <div class="ed-card" style="padding:1rem 1.3rem;">
                <p style="margin:0; color: var(--text-dim);">
                    Generate a hierarchical knowledge map of this video -
                    main topic, major concepts, and sub concepts - built
                    from its summary and key notes.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        button_label = "Regenerate" if st.session_state.concept_map_generated else "Generate Map"
        generate_clicked = st.button(button_label, use_container_width=True)

    if generate_clicked:
        with st.spinner("Building concept map..."):
            try:
                result = generate_concept_map(
                    transcript=st.session_state.transcript,
                    summary=st.session_state.summary,
                    notes=st.session_state.notes,
                )
                if result is None:
                    st.warning(
                        "⚠️ Not enough processed content yet to build a concept map. "
                        "Process a video on the Learn stage first."
                    )
                else:
                    st.session_state.concept_map = result
                    st.session_state.concept_map_generated = True
            except LLMGenerationError as exc:
                st.error(f"⚠️ {str(exc)}")
            except Exception as exc:  # noqa: BLE001
                st.error(f"⚠️ An unexpected error occurred: {str(exc)}")

    if not st.session_state.concept_map_generated or not st.session_state.concept_map:
        st.markdown(
            """
            <div class="ed-card">
                <p style="margin:0; color: var(--text-dim);">
                    No concept map generated yet. Click
                    <strong style="color:var(--text);">Generate Map</strong> above to build one.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    concept_map = st.session_state.concept_map
    stats = concept_map["stats"]

    render_section_label("Concept Statistics")
    render_stat_grid(
        [
            {"icon": "🎯", "value": "1", "label": "Main Topic"},
            {"icon": "🧠", "value": str(stats["major_concept_count"]), "label": "Major Concepts"},
            {"icon": "🔗", "value": str(stats["subtopic_count"]), "label": "Subtopics"},
            {"icon": "📊", "value": str(stats["total_concepts"]), "label": "Total Concepts"},
        ]
    )

    st.markdown(
        f"""
        <div class="ed-section-label" style="margin-top:1.6rem;">Main Topic</div>
        <div class="ed-card" style="padding:0.9rem 1.3rem;">
            <span style="font-family:'Space Grotesk', sans-serif; font-weight:600; font-size:1.05rem; color:var(--text);">
                {stats["main_topic"]}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_section_label("Hierarchical Concept Map")
    render_mermaid(concept_map["mermaid"])


render_concept_map_page()