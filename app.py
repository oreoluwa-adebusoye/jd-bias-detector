import streamlit as st
from ingest.read_text import read_any
from detector.detect import analyze_text, HAS_ML

st.set_page_config(page_title="Bias Detector for Job Descriptions", layout="wide")

st.title("Bias Detector for Job Descriptions")
st.caption("Flags potentially biased language and suggests inclusive alternatives.")

col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.subheader("Input")

    jd_text = st.text_area(
        "Paste a job description:",
        height=300,
        placeholder="Paste here...",
        key="jd_text"
    )

    uploaded = st.file_uploader(
        "...or upload a JD (PDF/DOCX/TXT)",
        type=["pdf", "docx", "txt"],
        key="jd_upload"
    )
    if uploaded:
        jd_text = read_any(uploaded)

    use_ml = st.checkbox(
        "Use ML (zero-shot) detection",
        value=HAS_ML,
        disabled=not HAS_ML,
        key="use_ml_checkbox"
    )

    if st.button("Analyze", type="primary", key="analyze_btn"):
        if jd_text and jd_text.strip():
            try:
                out = analyze_text(jd_text, use_ml=use_ml)
                st.session_state["results"] = out if isinstance(out, dict) else None
                if not isinstance(out, dict):
                    st.error("Analyzer returned an unexpected value.")
            except Exception as e:
                st.session_state["results"] = None
                st.exception(e)
        else:
            st.warning("Please paste or upload a job description first.")

# Read results safely
results = st.session_state.get("results")

with col2:
    if isinstance(results, dict):
        st.subheader("Summary")
        st.metric("Bias Score (0=high bias, 100=cleaner)", f'{results["score"]:.0f}')
        st.write(results["summary"])

        st.write("By category:")
        for cat, n in results["counts"].items():
            st.write(f"- **{cat}**: {n}")

        st.divider()
        st.subheader("Suggestions")
        if results["suggestions"]:
            for s in results["suggestions"]:
                note = f' — {s.get("note","")}' if s.get("note") else ""
                st.write(f'**“{s["found"]}”** → *{s["suggest"]}*{note}')
        else:
            st.write("No specific rewrite suggestions.")
    elif results is None and "results" in st.session_state:
        st.error("No results to display. See error above if any.")

st.divider()

# --- Inject CSS + Legend ---
if isinstance(results, dict):
    st.markdown(results.get("css", ""), unsafe_allow_html=True)
    legend = results.get("legend", [])
    if legend:
        chips = "".join([f'<span class="chip"><span class="dot" style="background:{c}"></span>{label}</span>'
                         for (label, c) in legend])
        st.markdown(f'<div class="legend">{chips}</div>', unsafe_allow_html=True)

st.subheader("Highlights")
if isinstance(results, dict):
    st.markdown(results["rendered_html"], unsafe_allow_html=True)
else:
    st.caption("Run an analysis to see highlighted text here.")

st.divider()

# --- Inject CSS + Legend ---
if isinstance(results, dict):
    st.markdown(results.get("css", ""), unsafe_allow_html=True)
    legend = results.get("legend", [])
    if legend:
        chips = "".join([f'<span class="chip"><span class="dot" style="background:{c}"></span>{label}</span>'
                         for (label, c) in legend])
        st.markdown(f'<div class="legend">{chips}</div>', unsafe_allow_html=True)

# --- Side-by-side: Original vs Inclusive Rewrite ---
if isinstance(results, dict):
    st.subheader("Before vs. Inclusive Rewrite")

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("**Original (highlighted)**")
        st.markdown(results["rendered_html"], unsafe_allow_html=True)

    with c2:
        st.markdown("**Inclusive rewrite (auto-applied suggestions)**")
        st.markdown(results["rewritten_html"], unsafe_allow_html=True)

    # Downloads
    st.download_button(
        "Download inclusive rewrite (.txt)",
        data=results["rewritten_text"],
        file_name="inclusive_rewrite.txt",
        mime="text/plain",
        key="dl_rewrite_txt"
    )

    # Show applied changes
    with st.expander("See applied replacements"):
        if results["changes"]:
            for ch in results["changes"]:
                note = f' — {ch["note"]}' if ch.get("note") else ""
                st.write(f'**{ch["category"]}**: “{ch["before"]}” → *{ch["after"]}*{note}')
        else:
            st.write("No automatic replacements were applied (no rule suggestions found).")
