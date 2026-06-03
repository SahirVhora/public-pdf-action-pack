from __future__ import annotations

import json
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
from action_pack.renderer import render_copy_message, render_markdown
from action_pack.validators import validate_action_pack

st.set_page_config(page_title="Public PDF Action Pack", page_icon="📄", layout="wide")
st.title("Public PDF Action Pack")
st.caption("Turn public-sector PDFs into plain-English actions, deadlines, and checklists.")

with st.sidebar:
    st.header("Settings")
    use_ai = st.toggle("Use AI if OPENROUTER_API_KEY is available", value=True)
    st.info("MVP privacy mode: do not upload sensitive private documents. Public documents only.")

uploaded = st.file_uploader("Upload a public PDF, TXT, or Markdown file", type=["pdf", "txt", "md"])
text_input = st.text_area("Or paste document text", height=220, placeholder="Paste a school letter, council notice, NHS guidance, or public PDF text...")

if st.button("Create action pack", type="primary"):
    try:
        if uploaded is not None:
            text = extract_text_from_upload(uploaded.name, uploaded.getvalue())
        else:
            text = text_input.strip()
        if not text:
            st.error("Upload a file or paste document text first.")
            st.stop()

        with st.spinner("Analysing document..."):
            pack = analyse_with_ai_or_fallback(text) if use_ai else analyse_without_ai(text)
            validation = validate_action_pack(pack)
            markdown = render_markdown(pack)

        st.success("Action pack created")
        if not validation.ok:
            st.warning("Validation found issues. Review the output before relying on it.")
            for issue in validation.issues:
                st.write(f"- {issue}")
        for warning in validation.warnings:
            st.info(warning)

        col1, col2, col3 = st.columns(3)
        col1.metric("Urgency", f"{pack.urgency_score}/5")
        col2.metric("Confidence", pack.confidence)
        col3.metric("Document type", pack.document_type.replace("_", " "))

        st.subheader(pack.title)
        st.write(" ".join(pack.plain_english_summary))

        st.subheader("Required actions")
        if pack.required_actions:
            for action in pack.required_actions:
                st.checkbox(f"{action.action} ({action.priority})", value=False)
                st.caption(action.source_text)
        else:
            st.write("No required actions found.")

        st.subheader("Key dates")
        st.dataframe([item.model_dump() for item in pack.key_dates], use_container_width=True)

        st.subheader("Costs and contacts")
        left, right = st.columns(2)
        with left:
            st.write([cost.model_dump() for cost in pack.costs] or "No costs found.")
        with right:
            st.write([contact.model_dump() for contact in pack.contacts] or "No contacts found.")

        st.subheader("Questions to ask")
        for question in pack.questions_to_ask:
            st.write(f"- {question}")

        st.subheader("Copy/share message")
        st.code(render_copy_message(pack), language="text")

        st.download_button("Download Markdown", markdown, file_name="action-pack.md", mime="text/markdown")
        st.download_button("Download JSON", pack.model_dump_json(indent=2), file_name="action-pack.json", mime="application/json")

        with st.expander("Full Markdown output"):
            st.markdown(markdown)
        with st.expander("Extracted source text"):
            st.text(text[:20000])
    except Exception as exc:
        st.error(str(exc))
