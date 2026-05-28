import streamlit as st
import os
import tempfile
from pathlib import Path
from config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="POE Generator",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Background — warm white, not dark */
.stApp {
    background: #F7F4EF;
    min-height: 100vh;
}

/* Hide sidebar toggle */
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"]  { display: none !important; }

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, #1B1F3B 0%, #2D2260 55%, #1B1F3B 100%);
    border-radius: 20px;
    padding: 3rem 2.5rem 2.5rem;
    text-align: center;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 70% 30%, rgba(120,80,255,0.25) 0%, transparent 60%),
                radial-gradient(ellipse at 20% 80%, rgba(0,180,220,0.18) 0%, transparent 50%);
    pointer-events: none;
}
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    color: #B8A9FF;
    font-size: 0.68rem; font-weight: 600;
    letter-spacing: 2px; text-transform: uppercase;
    padding: 5px 16px; border-radius: 50px;
    margin-bottom: 1.3rem;
}
.hero h1 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2.5rem; font-weight: 700;
    color: #FFFFFF;
    margin: 0 0 0.7rem; line-height: 1.15;
    letter-spacing: -0.5px;
}
.hero h1 em { font-style: normal; color: #A78BFA; }
.hero-sub {
    color: rgba(255,255,255,0.5);
    font-size: 0.95rem; font-weight: 400; margin: 0;
}

/* ── Section label ── */
.section-label {
    font-size: 0.7rem; font-weight: 700;
    color: #6B5CE7; letter-spacing: 2px; text-transform: uppercase;
    margin: 1.8rem 0 1rem;
    display: flex; align-items: center; gap: 10px;
}
.section-label::after {
    content: ''; flex: 1; height: 1px; background: #E0D9F5;
}

/* ── Upload widgets ── */
[data-testid="stFileUploaderDropzone"] {
    background: #FFFFFF !important;
    border: 1.5px solid #EAE6F8 !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #A78BFA !important;
    box-shadow: 0 4px 20px rgba(107,92,231,0.08) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
    display: none !important;
}
[data-testid="stFileUploader"] label p {
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    color: #1B1F3B !important;
    margin-bottom: 0.4rem !important;
}

/* ── Status pills ── */
.status-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 1.2rem 0 1.6rem; }
.status-pill {
    background: #FFFFFF; border: 1.5px solid #EAE6F8;
    border-radius: 12px; padding: 0.75rem 1rem; text-align: center;
}
.status-pill.ready { border-color: #6EE7B7; background: #F0FDF9; }
.status-label { font-size: 0.68rem; font-weight: 600; color: #8B8BA7; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 4px; }
.status-val   { font-size: 0.88rem; font-weight: 600; color: #1B1F3B; }
.status-pill.ready .status-val { color: #059669; }

/* ── Divider ── */
.divider { height: 1px; background: #EAE6F8; margin: 1.5rem 0; }

/* ── Submit button ── */
div[data-testid="stButton"] > button {
    width: 100% !important;
    padding: 0.95rem 2rem !important;
    font-size: 1rem !important; font-weight: 600 !important;
    background: linear-gradient(135deg, #6B5CE7 0%, #4F46E5 100%) !important;
    color: white !important; border: none !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 20px rgba(107,92,231,0.35) !important;
    letter-spacing: 0.2px; margin-top: 0.5rem;
    transition: all 0.2s !important;
}
div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #7C6EF0 0%, #6058F0 100%) !important;
    box-shadow: 0 6px 28px rgba(107,92,231,0.5) !important;
    transform: translateY(-1px);
}

/* ── Download button ── */
div[data-testid="stDownloadButton"] > button {
    width: 100% !important; padding: 0.95rem 2rem !important;
    font-size: 1rem !important; font-weight: 600 !important;
    background: linear-gradient(135deg, #059669 0%, #0891B2 100%) !important;
    color: white !important; border: none !important; border-radius: 14px !important;
    box-shadow: 0 4px 20px rgba(5,150,105,0.3) !important; margin-top: 0.5rem;
}

/* ── Progress ── */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #6B5CE7, #4F46E5) !important;
    border-radius: 50px !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #FFFFFF !important; border: 1.5px solid #EAE6F8 !important;
    border-radius: 14px !important; padding: 1rem 1.2rem !important;
}
[data-testid="stMetricLabel"] p { color: #8B8BA7 !important; font-size: 0.75rem !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.5px !important; }
[data-testid="stMetricValue"]   { color: #6B5CE7 !important; font-size: 1.7rem !important; font-weight: 700 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF !important; border: 1px solid #EAE6F8 !important;
    border-radius: 12px !important; gap: 4px !important; padding: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important; color: #8B8BA7 !important;
    font-size: 0.82rem !important; font-weight: 600 !important; padding: 6px 14px !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6B5CE7, #4F46E5) !important; color: white !important;
}

/* ── Result items ── */
.result-item {
    background: #FFFFFF; border: 1px solid #EAE6F8;
    border-left: 3px solid #6B5CE7;
    border-radius: 8px; padding: 0.65rem 1rem;
    margin: 0.3rem 0; font-size: 0.83rem; color: #374151; line-height: 1.5;
}

/* ── Success banner ── */
.success-banner {
    background: linear-gradient(135deg, #F0FDF9, #EFF6FF);
    border: 1.5px solid #6EE7B7; border-radius: 16px;
    padding: 1.2rem 1.5rem; text-align: center;
    color: #065F46; font-weight: 600; font-size: 0.95rem; margin: 1rem 0;
}

/* ── Processing card ── */
.proc-card {
    background: #FFFFFF; border: 1.5px solid #EAE6F8;
    border-radius: 14px; padding: 1.2rem 1.5rem; margin: 0.5rem 0;
}

.stAlert { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">✦ &nbsp; Automated Report Builder</div>
    <h1>Marketing <em>PoE</em></h1>
    <p class="hero-sub">Upload your files · Click generate · Download your finished deck</p>
</div>
""", unsafe_allow_html=True)

# ── Upload section ────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Upload files</div>', unsafe_allow_html=True)

st.markdown('<p style="font-size:0.82rem;font-weight:700;color:#1B1F3B;margin:0 0 4px">📄 &nbsp;Content PDF Report</p><p style="font-size:0.75rem;color:#8B8BA7;margin:0 0 8px">Campaign evidence — URL, screenshot &amp; results extracted automatically</p>', unsafe_allow_html=True)
pdf_file = st.file_uploader("pdf_report", type=["pdf"], label_visibility="collapsed", key="k_pdf")

st.markdown('<p style="font-size:0.82rem;font-weight:700;color:#1B1F3B;margin:1rem 0 4px">📑 &nbsp;PowerPoint Template</p><p style="font-size:0.75rem;color:#8B8BA7;margin:0 0 8px">Your branded POE deck — slides 3, 4 &amp; 5 filled automatically</p>', unsafe_allow_html=True)
pptx_file = st.file_uploader("pptx_template", type=["pptx"], label_visibility="collapsed", key="k_pptx")

st.markdown('<p style="font-size:0.82rem;font-weight:700;color:#1B1F3B;margin:1rem 0 4px">🗂️ &nbsp;Advert / LinkedIn Images</p><p style="font-size:0.75rem;color:#8B8BA7;margin:0 0 8px">All images from your LinkedIn folder — placed in 2×2 grid on Slide 5</p>', unsafe_allow_html=True)
advert_files = st.file_uploader(
    "advert_images", type=["png","jpg","jpeg","gif","webp"],
    accept_multiple_files=True, label_visibility="collapsed", key="k_adv",
)

# ── Status indicators ─────────────────────────────────────────────────────────
def _pill(label, value, ready=False):
    cls = "status-pill ready" if ready else "status-pill"
    return f'<div class="{cls}"><div class="status-label">{label}</div><div class="status-val">{value}</div></div>'

st.markdown(f"""
<div class="status-row">
  {_pill("PDF Report",    "✓ Ready" if pdf_file   else "Waiting",     bool(pdf_file))}
  {_pill("PPT Template",  "✓ Ready" if pptx_file  else "Waiting",     bool(pptx_file))}
  {_pill("Advert Images", f"✓ {len(advert_files)} files" if advert_files else "Waiting", bool(advert_files))}
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Generate button ───────────────────────────────────────────────────────────
run_btn = st.button("✦  Generate Proof of Execution PPT", use_container_width=True)

# ── Processing ────────────────────────────────────────────────────────────────
if run_btn:
    errors = []
    if not pdf_file:     errors.append("📄 Please upload the Content PDF Report.")
    if not pptx_file:    errors.append("📑 Please upload the PowerPoint Template.")
    if not advert_files: errors.append("🗂️ Please upload at least one Advert / LinkedIn image.")
    if errors:
        for e in errors: st.error(e)
        st.stop()

    # Save uploads to temp dir
    tmp_dir   = tempfile.mkdtemp()
    pdf_path  = os.path.join(tmp_dir, "report.pdf")
    pptx_path = os.path.join(tmp_dir, "template.pptx")
    with open(pdf_path,  "wb") as f: f.write(pdf_file.read())
    with open(pptx_path, "wb") as f: f.write(pptx_file.read())

    advert_dir   = os.path.join(tmp_dir, "adverts")
    os.makedirs(advert_dir, exist_ok=True)
    advert_paths = []
    for af in advert_files:
        dest = os.path.join(advert_dir, af.name)
        with open(dest, "wb") as f: f.write(af.read())
        advert_paths.append(dest)

    progress_bar = st.progress(0)
    status       = st.empty()

    try:
        # Step 1 — Extract PDF
        status.markdown('<div class="proc-card">⏳ &nbsp;<b>Step 1 / 4</b> &nbsp; Extracting images &amp; text from PDF…</div>', unsafe_allow_html=True)
        progress_bar.progress(10)

        from extractor import extract_pdf_content
        extraction = extract_pdf_content(pdf_path, tmp_dir)
        extraction["advert_images"] = advert_paths

        progress_bar.progress(28)
        status.markdown(
            f'<div class="proc-card">✅ &nbsp;<b>Step 1 / 4</b> &nbsp; Found <b>{len(extraction["images"])}</b> images across <b>{len(extraction["text_pages"])}</b> pages</div>',
            unsafe_allow_html=True
        )

        # Step 2 — AI analysis
        status.markdown('<div class="proc-card">⏳ &nbsp;<b>Step 2 / 4</b> &nbsp; Analysing content with Azure OpenAI…</div>', unsafe_allow_html=True)
        progress_bar.progress(35)

        from ai_analyzer import analyze_with_azure
        analysis = analyze_with_azure(
            extraction=extraction,
            keywords=["URL","screenshot","results","syndication","LinkedIn",
                      "advert","impressions","clicks","engagement","campaign","CTR"],
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            azure_api_key=AZURE_OPENAI_KEY,
            azure_deployment=AZURE_OPENAI_DEPLOYMENT,
            azure_api_version=AZURE_OPENAI_API_VERSION,
        )
        if advert_paths:
            analysis["slide5_image_path"] = advert_paths[0]

        progress_bar.progress(65)
        status.markdown('<div class="proc-card">✅ &nbsp;<b>Step 2 / 4</b> &nbsp; AI analysis complete</div>', unsafe_allow_html=True)

        # Step 3 — Populate PPTX
        status.markdown('<div class="proc-card">⏳ &nbsp;<b>Step 3 / 4</b> &nbsp; Populating PowerPoint template…</div>', unsafe_allow_html=True)
        progress_bar.progress(70)

        from pptx_writer import populate_pptx
        output_pptx = os.path.join(tmp_dir, "proof_of_execution.pptx")
        populate_pptx(
            template_path=pptx_path,
            output_path=output_pptx,
            analysis=analysis,
            extraction=extraction,
        )

        progress_bar.progress(90)
        status.markdown('<div class="proc-card">✅ &nbsp;<b>Step 3 / 4</b> &nbsp; Slides populated — headers preserved</div>', unsafe_allow_html=True)

        # Step 4 — Package
        status.markdown('<div class="proc-card">⏳ &nbsp;<b>Step 4 / 4</b> &nbsp; Packaging output file…</div>', unsafe_allow_html=True)
        progress_bar.progress(96)
        with open(output_pptx, "rb") as f:
            pptx_bytes = f.read()
        progress_bar.progress(100)
        status.empty()

        # ── Success ───────────────────────────────────────────────────────────
        st.markdown("""
        <div class="success-banner">
            ✦ &nbsp; Proof of Execution deck generated successfully!
        </div>
        """, unsafe_allow_html=True)

        # Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("URLs",         len(analysis.get("urls", [])))
        m2.metric("PDF Images",   len(extraction.get("images", [])))
        m3.metric("Syndication",  len(analysis.get("syndication_results", [])))
        m4.metric("Advert Files", len(advert_paths))

        # Preview tabs
        t1, t2, t3, t4 = st.tabs(["🔗 URLs", "📸 PDF Screenshots", "📢 Syndication", "💼 LinkedIn"])

        with t1:
            urls = analysis.get("urls", [])
            for i, u in enumerate(urls, 1):
                st.markdown(f'<div class="result-item"><b style="color:#6B5CE7">#{i}</b> &nbsp;{u}</div>', unsafe_allow_html=True)
            if not urls:
                st.info("No URLs extracted.")

        with t2:
            imgs = extraction.get("images", [])
            if imgs:
                for row_start in range(0, min(9, len(imgs)), 3):
                    cols = st.columns(3)
                    for j, col in enumerate(cols):
                        idx = row_start + j
                        if idx < len(imgs):
                            with col:
                                try: st.image(imgs[idx], use_container_width=True)
                                except: st.caption(Path(imgs[idx]).name)
            else:
                st.info("No embedded images found.")

        with t3:
            for item in analysis.get("syndication_results", []):
                st.markdown(f'<div class="result-item">{item}</div>', unsafe_allow_html=True)
            if not analysis.get("syndication_results"):
                st.info("No syndication data found.")

        with t4:
            for item in analysis.get("linkedin_results", []):
                st.markdown(f'<div class="result-item">{item}</div>', unsafe_allow_html=True)
            if advert_paths:
                st.markdown("**Uploaded advert images:**")
                for row_start in range(0, min(6, len(advert_paths)), 3):
                    cols = st.columns(3)
                    for j, col in enumerate(cols):
                        idx = row_start + j
                        if idx < len(advert_paths):
                            with col:
                                try: st.image(advert_paths[idx], use_container_width=True)
                                except: st.caption(Path(advert_paths[idx]).name)

        # Download
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.download_button(
            label="⬇️  Download  proof_of_execution.pptx",
            data=pptx_bytes,
            file_name="proof_of_execution.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True,
        )

        with st.expander("🔍 Raw AI Analysis JSON"):
            st.json(analysis)

    except Exception as e:
        st.error(f"❌ {e}")
        import traceback
        with st.expander("Stack trace"):
            st.code(traceback.format_exc())
