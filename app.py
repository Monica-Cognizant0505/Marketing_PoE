import streamlit as st
import os
import tempfile
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="POE Generator",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding:20px'>
<h4>✦ Automated Report Builder</h4>
<h1>Marketing PoE</h1>
<p>Click generate · Download your finished deck</p>
</div>
""", unsafe_allow_html=True)

# ── Section header (no upload UI now) ─────────────────────────────────────────
st.markdown("### 🚀 Generate Report")

# ── Generate button ───────────────────────────────────────────────────────────
run_btn = st.button("✦ Generate Proof of Execution PPT", use_container_width=True)

# ── Processing ────────────────────────────────────────────────────────────────
if run_btn:

    # 👉 Hardcoded / placeholder paths (replace later with SharePoint or backend)
    pdf_path = "sample_data/report.pdf"
    pptx_path = "sample_data/template.pptx"
    advert_paths = ["sample_data/ad1.png", "sample_data/ad2.png"]

    progress_bar = st.progress(0)
    status = st.empty()

    try:
        # Step 1 — Extract PDF
        status.markdown("⏳ **Step 1 / 4** Extracting images & text from PDF…")
        progress_bar.progress(10)

        from extractor import extract_pdf_content
        extraction = extract_pdf_content(pdf_path, tempfile.gettempdir())
        extraction["advert_images"] = advert_paths

        progress_bar.progress(28)
        status.markdown(
            f"✅ **Step 1 / 4** Found {len(extraction['images'])} images across {len(extraction['text_pages'])} pages"
        )

        # Step 2 — AI analysis
        status.markdown("⏳ **Step 2 / 4** Analysing content…")
        progress_bar.progress(35)

        from ai_analyzer import analyze_with_azure
        analysis = analyze_with_azure(
            extraction=extraction,
            keywords=["URL","screenshot","results","LinkedIn"],
        )

        if advert_paths:
            analysis["slide5_image_path"] = advert_paths[0]

        progress_bar.progress(65)
        status.markdown("✅ **Step 2 / 4** AI analysis complete")

        # Step 3 — Populate PPTX
        status.markdown("⏳ **Step 3 / 4** Populating PowerPoint template…")
        progress_bar.progress(70)

        from pptx_writer import populate_pptx
        output_pptx = os.path.join(tempfile.gettempdir(), "proof_of_execution.pptx")

        populate_pptx(
            template_path=pptx_path,
            output_path=output_pptx,
            analysis=analysis,
            extraction=extraction,
        )

        progress_bar.progress(90)
        status.markdown("✅ **Step 3 / 4** Slides populated")

        # Step 4 — Package
        status.markdown("⏳ **Step 4 / 4** Packaging output file…")
        progress_bar.progress(96)

        with open(output_pptx, "rb") as f:
            pptx_bytes = f.read()

        progress_bar.progress(100)
        status.empty()

        # ── Success ───────────────────────────────────────────────────────────
        st.success("✦ Proof of Execution deck generated successfully!")

        st.download_button(
            label="⬇️ Download proof_of_execution.pptx",
            data=pptx_bytes,
            file_name="proof_of_execution.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True,
        )

    except Exception as e:
        st.error(f"❌ {e}")
