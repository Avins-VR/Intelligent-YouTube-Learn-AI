"""
concept_map.py

Concept Map Generation (Phase 4)

Flow:
1. Take the already-generated summary + key notes (and transcript as a
   fallback) for a processed video.
2. Ask Groq to extract a hierarchical knowledge structure: one main
   topic -> major concepts -> sub concepts (as a JSON tree).
3. Validate & sanitize the returned tree.
4. Deterministically render the tree into Mermaid flowchart syntax
   (more reliable than asking the LLM to hand-write Mermaid directly,
   since a single malformed edge would break rendering entirely).
5. Compute simple statistics (main topic, # major concepts, # sub
   concepts, depth) for display in the UI.

This module is purely additive: it does not import or modify
transcript.py, embeddings.py, rag.py, summary.py, notes.py, mcq.py or
recommendations.py. It only reuses config.py and utils/exceptions.py,
mirroring the existing Groq-based pattern used elsewhere in the app.
"""

import json
import re
from typing import Dict, List, Optional

from groq import Groq

import config
from utils.exceptions import LLMGenerationError


# --------------------------------------------------
# Configure Groq
# --------------------------------------------------

client = Groq(api_key=config.GROQ_API_KEY)


# --------------------------------------------------
# Tunables
# --------------------------------------------------

MAX_TREE_DEPTH = 3          # 0=main topic, 1=major concept, 2=sub concept, 3=sub-sub concept
MAX_CHILDREN_PER_NODE = 8
MAX_LABEL_LENGTH = 60
MAX_TRANSCRIPT_FALLBACK_CHARS = 12000  # only used if no summary is available yet


# --------------------------------------------------
# Prompt
# --------------------------------------------------

CONCEPT_MAP_PROMPT = """
You are an expert educational content analyst who builds concept maps
(hierarchical knowledge structures) from lecture content.

Analyze the educational content below and identify:

1. The single Main Topic of the video.
2. Major Concepts - the primary topics that sit directly under the main topic.
3. Sub Concepts - more specific ideas, techniques, or components under each major concept.
4. Parent-child relationships between all of the above.

Rules:

1. Identify exactly ONE main topic.
2. Identify between 2 and 8 major concepts.
3. Give each major concept between 0 and 6 sub concepts, only where the
   content clearly supports it.
4. A sub concept may have its own children (one further level) only when
   clearly justified by the content - otherwise leave it as a leaf with
   an empty children list.
5. Use short, clear concept names (2-6 words each).
6. Do NOT invent concepts that are not present in the provided content.
7. Do NOT include timestamps, speaker names, or filler content.
8. Return ONLY valid JSON. No markdown code fences. No commentary.

Output JSON shape (exact keys, this is a recursive tree):

{{
  "name": "Main Topic Name",
  "children": [
    {{
      "name": "Major Concept Name",
      "children": [
        {{
          "name": "Sub Concept Name",
          "children": []
        }}
      ]
    }}
  ]
}}

Video Summary:

{summary}

Key Notes:

{key_notes}
{transcript_section}
"""


# --------------------------------------------------
# JSON Extraction / Parsing
# --------------------------------------------------

def _extract_json_object(raw_text: str) -> str:
    """Best-effort extraction of a JSON object from a model response."""
    cleaned = raw_text.strip()

    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or end < start:
        return cleaned

    return cleaned[start:end + 1]


def _validate_node(node, depth: int = 0) -> bool:
    """Recursively validate the shape of one concept-tree node."""
    if not isinstance(node, dict):
        return False

    name = node.get("name")
    if not isinstance(name, str) or not name.strip():
        return False

    children = node.get("children", [])
    if children is None:
        children = []
        node["children"] = children

    if not isinstance(children, list):
        return False

    for child in children:
        if not _validate_node(child, depth + 1):
            return False

    return True


def parse_concept_tree(raw_text: str) -> Optional[Dict]:
    """Parse + validate the model's JSON response into a concept tree dict."""
    json_str = _extract_json_object(raw_text)

    try:
        parsed = json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None

    if not _validate_node(parsed):
        return None

    return parsed


# --------------------------------------------------
# Sanitization (defensive - caps size/depth before rendering)
# --------------------------------------------------

def _clean_label(text: str) -> str:
    label = " ".join(text.strip().split())
    label = label.replace('"', "'")
    if len(label) > MAX_LABEL_LENGTH:
        label = label[:MAX_LABEL_LENGTH - 1].rstrip() + "…"
    return label or "Untitled"


def sanitize_tree(node: Dict, depth: int = 0) -> Dict:
    """Trim labels, cap fan-out, and cap depth so the rendered map stays
    readable regardless of exactly what the model returned."""
    clean = {
        "name": _clean_label(node.get("name", "Untitled")),
        "children": [],
    }

    if depth < MAX_TREE_DEPTH:
        children = node.get("children", []) or []
        for child in children[:MAX_CHILDREN_PER_NODE]:
            if isinstance(child, dict):
                clean["children"].append(sanitize_tree(child, depth + 1))

    return clean


# --------------------------------------------------
# Mermaid Rendering (deterministic - built from the validated tree,
# never generated freeform by the LLM, so it always renders cleanly)
# --------------------------------------------------

_SHAPES = {
    0: ('(["', '"])'),   # main topic - stadium
    1: ('["', '"]'),      # major concept - rectangle
    2: ('("', '")'),      # sub concept - rounded rectangle
    3: ('("', '")'),      # sub-sub concept - rounded rectangle
}

_CLASS_NAMES = {
    0: "mainTopic",
    1: "majorConcept",
    2: "subConcept",
    3: "subConcept",
}


def build_mermaid(tree: Dict) -> str:
    """Deterministically render a sanitized concept tree into Mermaid
    flowchart syntax, styled to match the app's dark biopunk palette."""
    lines: List[str] = ["graph TD"]
    nodes_by_class: Dict[str, List[str]] = {}
    counter = {"i": 0}

    def add_node(node: Dict, parent_id: Optional[str], depth: int) -> None:
        node_id = f"N{counter['i']}"
        counter["i"] += 1

        open_tok, close_tok = _SHAPES.get(depth, _SHAPES[3])
        lines.append(f'    {node_id}{open_tok}{node["name"]}{close_tok}')

        class_name = _CLASS_NAMES.get(depth, "subConcept")
        nodes_by_class.setdefault(class_name, []).append(node_id)

        if parent_id is not None:
            lines.append(f"    {parent_id} --> {node_id}")

        for child in node.get("children", []):
            add_node(child, node_id, depth + 1)

    add_node(tree, None, 0)

    lines.append("")
    lines.append("    classDef mainTopic fill:#7c6cf0,stroke:#7c6cf0,color:#11141c,font-weight:bold;")
    lines.append("    classDef majorConcept fill:#1f2433,stroke:#ff8a4c,stroke-width:1.5px,color:#e9e7df;")
    lines.append("    classDef subConcept fill:#181c27,stroke:#2b3142,color:#9aa0b4;")

    for class_name, ids in nodes_by_class.items():
        lines.append(f"    class {','.join(ids)} {class_name};")

    return "\n".join(lines)


# --------------------------------------------------
# Statistics
# --------------------------------------------------

def compute_stats(tree: Dict) -> Dict:
    """Compute simple counts used by the Concept Map page."""
    major_concepts = tree.get("children", [])
    major_concept_count = len(major_concepts)

    subtopic_count = 0
    max_depth = 0

    def walk(node: Dict, depth: int) -> None:
        nonlocal subtopic_count, max_depth
        max_depth = max(max_depth, depth)
        for child in node.get("children", []):
            if depth >= 1:
                subtopic_count += 1
            walk(child, depth + 1)

    walk(tree, 0)

    return {
        "main_topic": tree.get("name", "Untitled"),
        "major_concept_count": major_concept_count,
        "subtopic_count": subtopic_count,
        "total_concepts": 1 + major_concept_count + subtopic_count,
        "max_depth": max_depth,
    }


# --------------------------------------------------
# Main Pipeline
# --------------------------------------------------

def generate_concept_map(
    transcript: Optional[str],
    summary: Optional[str],
    notes: Optional[List[str]],
) -> Optional[Dict]:
    """
    Generate a concept map for a processed video.

    Args:
        transcript: Full cleaned transcript (used only as a fallback if
            no summary is available yet).
        summary: Generated study summary for the video.
        notes: Generated key notes (list of bullet strings) for the video.

    Returns:
        A dict: {"tree": <validated tree>, "mermaid": <mermaid string>,
        "stats": <stats dict>}, or None if there is not enough source
        content to work with yet.

    Raises:
        LLMGenerationError: if the Groq API call fails or the model's
            response could not be parsed into a valid concept tree.
    """
    if not config.GROQ_API_KEY:
        raise LLMGenerationError("GROQ_API_KEY is not set.")

    if not summary and not notes and not transcript:
        return None

    key_concepts_text = "\n".join(f"- {note}" for note in notes) if notes else "Not available."

    transcript_section = ""
    if not summary and transcript:
        # Fall back to a truncated transcript only when no summary exists yet.
        truncated = transcript[:MAX_TRANSCRIPT_FALLBACK_CHARS]
        transcript_section = f"\nTranscript Excerpt:\n\n{truncated}\n"

    prompt = CONCEPT_MAP_PROMPT.format(
        summary=summary or "Not available.",
        key_notes=key_concepts_text,
        transcript_section=transcript_section,
    )

    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_completion_tokens=2000,
        )
        raw_text = response.choices[0].message.content.strip()
    except Exception as exc:
        raise LLMGenerationError(f"Groq API Error while generating concept map: {str(exc)}")

    tree = parse_concept_tree(raw_text)

    if not tree:
        raise LLMGenerationError(
            "The AI response could not be parsed into a valid concept map. Please try again."
        )

    tree = sanitize_tree(tree)
    mermaid = build_mermaid(tree)
    stats = compute_stats(tree)

    return {
        "tree": tree,
        "mermaid": mermaid,
        "stats": stats,
    }