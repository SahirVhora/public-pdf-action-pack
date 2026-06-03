from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import streamlit as st

from action_pack.analyser import analyse_with_ai_or_fallback
from action_pack.extractor import extract_text_from_upload
from action_pack.fallback_analyser import analyse_without_ai
from action_pack.presentation import action_label, source_is_duplicate
from action_pack.renderer import render_copy_message, render_markdown
from action_pack.validators import validate_action_pack

st.set_page_config(page_title="Public PDF Action Pack", page_icon="📄", layout="wide")
st.title("Public PDF Action Pack")
st.caption("Turn public-sector PDFs into plain-English actions, deadlines, and checklists.")

if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_error" not in st.session_state:
    st.session_state.last_error = None

with st.sidebar:
    st.header("Settings")
    use_ai = st.toggle("Use AI if OPENROUTER_API_KEY is available", value=True)
    st.info("MVP privacy mode: do not upload sensitive private documents. Public documents only.")
    if st.button("Clear current action pack"):
        st.session_state.last_result = None
        st.session_state.last_error = None

uploaded = st.file_uploader("Upload a public PDF, TXT, or Markdown file", type=["pdf", "txt", "md"])
text_input = st.text_area("Or paste document text", height=220, placeholder="Paste a school letter, council notice, NHS guidance, or public PDF text...")

if st.button("Create action pack", type="primary"):
    try:
        if uploaded is not None:
            text = extract_text_from_upload(uploaded.name, uploaded.getvalue())
        else:
            text = text_input.strip()
        if not text:
            st.session_state.last_error = "Upload a file or paste document text first."
            st.session_state.last_result = None
        else:
            with st.spinner("Analysing document..."):
                pack = analyse_with_ai_or_fallback(text) if use_ai else analyse_without_ai(text)
                validation = validate_action_pack(pack)
                markdown = render_markdown(pack)
            st.session_state.last_result = {
                "text": text,
                "pack": pack,
                "validation": validation,
                "markdown": markdown,
            }
            st.session_state.last_error = None
    except Exception as exc:
        st.session_state.last_error = str(exc)
        st.session_state.last_result = None

if st.session_state.last_error:
    st.error(st.session_state.last_error)

result = st.session_state.last_result
if result:
    pack = result["pack"]
    validation = result["validation"]
    markdown = result["markdown"]
    text = result["text"]

    st.success("Action pack ready. It will stay visible while you tick boxes, open sections, or download files.")
    if not validation.ok:
        st.warning("Validation found issues. Review the output before relying on it.")
        for issue in validation.issues:
            st.write(f"- {issue}")
    for warning in validation.warnings:
        st.info(warning)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Urgency", f"{pack.urgency_score}/5")
    col2.metric("Confidence", pack.confidence)
    col3.metric("Document type", pack.document_type.replace("_", " "))
    col4.metric("Pages detected", text.count("--- Page ") or "Text")

    st.subheader(pack.title)
    st.write(" ".join(pack.plain_english_summary))

    st.subheader("Required actions")
    if pack.required_actions:
        for index, action in enumerate(pack.required_actions):
            st.checkbox(action_label(action), value=False, key=f"action_{index}_{action.action}")
            if action.source_text and not source_is_duplicate(action):
                with st.expander(f"Evidence for action {index + 1}"):
                    st.write(action.source_text)
    else:
        st.write("No required actions found.")

    st.subheader("Key dates")
    if pack.key_dates:
        st.dataframe([item.model_dump() for item in pack.key_dates], use_container_width=True)
    else:
        st.write("No key dates found.")

    st.subheader("Costs and contacts")
    left, right = st.columns(2)
    with left:
        st.write([cost.model_dump() for cost in pack.costs] or "No costs found.")
    with right:
        st.write([contact.model_dump() for contact in pack.contacts] or "No contacts found.")

    st.subheader("Questions to ask")
    for question in pack.questions_to_ask:
        st.write(f"- {question}")

    st.subheader("Choices / decisions to make")
    if pack.decisions_to_make:
        st.dataframe([decision.model_dump() for decision in pack.decisions_to_make], use_container_width=True)
    else:
        st.write("No explicit decisions found.")

    st.subheader("Child checklist")
    if pack.child_checklist:
        for item in pack.child_checklist:
            st.markdown(f"- {item}")
    else:
        if pack.document_type == "school_letter":
            st.write("No child checklist items found.")
        elif pack.document_type == "nhs_guidance":
            st.write("No preparation items found.")
        else:
            st.write("No checklist items found.")

    st.subheader("Copy/share message")
    st.code(render_copy_message(pack), language="text")

    st.download_button("Download Markdown", markdown, file_name="action-pack.md", mime="text/markdown")
    st.download_button("Download JSON", pack.model_dump_json(indent=2), file_name="action-pack.json", mime="application/json")

    with st.expander("Full Markdown output"):
        st.markdown(markdown)
    with st.expander("Extracted source text"):
        st.text(text[:50000])
