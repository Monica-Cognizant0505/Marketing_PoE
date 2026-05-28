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

st.set_page_config(
    page_title="Marketing PoE",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.stApp { background: #F5F3EF; }

[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* Hero */
.hero {
    background: linear-gradient(135deg, #1a1740 0%, #2e1f6e 50%, #1a1740 100%);
    border-radius: 18px;
    padding: 2.8rem 2rem 2.4rem;
    text-align: center;
    margin-bottom: 2rem;
}
.hero-tag {
    display: inline-block;
    border: 1px solid rgba(255,255,255,0.2);
    color: #c4b5fd;
    font-size: 0.65rem; font-weight: 700;
    letter-spacing: 2.5px; text-transform: uppercase;
    padding: 4px 16px; border-radius: 50px;
    margin-bottom: 1.2rem;
}
.hero h1 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2.4rem; font-weight: 800;
    color: #fff; margin: 0 0 0.6rem; line-height: 1.15;
}
.hero h1 span { color: #a78bfa; }
.hero p { color: rgba(255,255,255,0.45); font-size: 0.92rem; margin: 0; }

/* Section title */
.sec-title {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; color: #7c3aed;
    display: flex; align-items: center; gap: 10px;
    margin: 0 0 1.2rem;
}
.sec-title::after { content:''; flex:1; height:1px; background:#e5e0f8; }

/* Status cards */
.status-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 1.4rem 0; }
.scard { background:#fff; border:1.5px solid #ece8f8; border-radius:12px; padding:0.8rem 1rem; text-align:center; }
.scard.ok { border-color:#86efac; background:#f0fdf4; }
.scard-label { font-size:0.65rem; font-weight:700; color:#9ca3af; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:3px; }
.scard-val { font-size:0.85rem; font-weight:600; color:#374151; }
.scard.ok .scard-val { color:#16a34a; }

/* Divider */
.div { height:1px; background:#ece8f8; margin:1.4rem 0; }

/* Proc card */
.proc { background:#fff; border:1.5px solid #ece8f8; border-radius:12px; padding:1rem 1.3rem; margin:0.4rem 0; font-size:0.88rem; color:#374151; }

/* Success */
.ok-banner { background:#f0fdf4; border:1.5px solid #86efac; border-radius:14px; padding:1.1rem; text-align:center; color:#15803d; font-weight:600; font-size:0.92rem; margin:1rem 0; }

/* Result item */
.ritem { background:#fff; border-left:3px solid #7c3aed; border-radius:0 8px 8px 0; padding:0.6rem 1rem; margin:0.3rem 0; font-size:0.82rem; color:#374151; }

/* Streamlit overrides */
div[data-testid="stButton"] > button {
    width:100% !important; padding:0.9rem !important;
    font-size:0.98rem !important; font-weight:700 !important;
    background: linear-gradient(135deg,#7c3aed,#4f46e5) !important;
    color:#fff !important; border:none !important; border-radius:12px !important;
    box-shadow: 0 4px 18px rgba(124,58,237,0.35) !important;
    margin-top:0.6rem;
}
div[data-testid="stDownloadButton"] > button {
    width:100% !important; padding:0.9rem !important;
    font-size:0.98rem !important; font-weight:700 !important;
    background: linear-gradient(135deg,#059669,#0891b2) !important;
    color:#fff !important; border:none !important; border-radius:12px !important;
    box-shadow: 0 4px 18px rgba(5,150,105,0.3) !important;
}
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg,#7c3aed,#4f46e5) !important;
    border-radius:50px !important;
}
[data-testid="stMetric"] {
    background:#fff !important; border:1.5px solid #ece8f8 !important;
    border-radius:12px !important; padding:1rem !important;
}
[data-testid="stMetricValue"] { color:#7c3aed !important; font-size:1.6rem !important; font-weight:700 !important; }
[data-testid="stMetricLabel"] p { color:#9ca3af !important; font-size:0.72rem !important; font-weight:600 !important; text-transform:uppercase !important; }
.stTabs [data-baseweb="tab-list"] { background:#fff !important; border:1px solid #ece8f8 !important; border-radius:10px !important; padding:3px !important; }
.stTabs [data-baseweb="tab"] { border-radius:8px !important; color:#9ca3af !important; font-size:0.8rem !important; font-weight:600 !important; }
.stTabs [aria-selected="true"] { background:linear-gradient(135deg,#7c3aed,#4f46e5) !important; color:#fff !important; }
.stAlert { border-radius:10px !important; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-tag">✦ Automated Report Builder</div>
    <h1>Marketing <span>PoE</span></h1>
    <p>Upload your files · Click generate · Download your finished deck</p>
</div>
""", unsafe_allow_html=True)

# ── Uploads ───────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Upload files</div>', unsafe_allow_html=True)

pdf_file     = st.file_uploader("📄  Content PDF Report",              type=["pdf"],                                  key="k_pdf")
pptx_file    = st.file_uploader("📑  PowerPoint Template",             type=["pptx"],                                 key="k_pptx")
advert_files = st.file_uploader("🗂️  Advert / LinkedIn Images",        type=["png","jpg","jpeg","gif","webp"],
                                 accept_multiple_files=True,                                                           key="k_adv")

# ── Status ────────────────────────────────────────────────────────────────────
def _sc(label, val, ok):
    cls = "scard ok" if ok else "scard"
    return f'<div class="{cls}"><div class="scard-label">{label}</div><div class="scard-val">{val}</div></div>'

st.markdown(f"""
<div class="status-grid">
  {_sc("PDF Report",    "✓ Ready" if pdf_file        else "Waiting", bool(pdf_file))}
  {_sc("PPT Template",  "✓ Ready" if pptx_file       else "Waiting", bool(pptx_file))}
  {_sc("Advert Images", f"✓ {len(advert_files)} files" if advert_files else "Waiting", bool(advert_files))}
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="div"></div>', unsafe_allow_html=True)

# ── Generate ──────────────────────────────────────────────────────────────────
run_btn = st.button("✦  Generate Proof of Execution PPT", use_container_width=True)

if run_btn:
    errors = []
    if not pdf_file:     errors.append("📄 Please upload the Content PDF Report.")
    if not pptx_file:    errors.append("📑 Please upload the PowerPoint Template.")
    if not advert_files: errors.append("🗂️ Please upload at least one Advert / LinkedIn image.")
    if errors:
        for e in errors: st.error(e)
        st.stop()

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

    bar    = st.progress(0)
    status = st.empty()

    try:
        status.markdown('<div class="proc">⏳ <b>Step 1/4</b> — Extracting images & text from PDF…</div>', unsafe_allow_html=True)
        bar.progress(10)
        from extractor import extract_pdf_content
        extraction = extract_pdf_content(pdf_path, tmp_dir)
        extraction["advert_images"] = advert_paths
        bar.progress(28)
        status.markdown(f'<div class="proc">✅ <b>Step 1/4</b> — Found <b>{len(extraction["images"])}</b> images across <b>{len(extraction["text_pages"])}</b> pages</div>', unsafe_allow_html=True)

        status.markdown('<div class="proc">⏳ <b>Step 2/4</b> — Analysing with Azure OpenAI…</div>', unsafe_allow_html=True)
        bar.progress(35)
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
        bar.progress(65)
        status.markdown('<div class="proc">✅ <b>Step 2/4</b> — AI analysis complete</div>', unsafe_allow_html=True)

        status.markdown('<div class="proc">⏳ <b>Step 3/4</b> — Populating PowerPoint…</div>', unsafe_allow_html=True)
        bar.progress(70)
        from pptx_writer import populate_pptx
        output_pptx = os.path.join(tmp_dir, "proof_of_execution.pptx")
        populate_pptx(template_path=pptx_path, output_path=output_pptx, analysis=analysis, extraction=extraction)
        bar.progress(90)
        status.markdown('<div class="proc">✅ <b>Step 3/4</b> — Slides populated</div>', unsafe_allow_html=True)

        status.markdown('<div class="proc">⏳ <b>Step 4/4</b> — Packaging output…</div>', unsafe_allow_html=True)
        bar.progress(96)
        with open(output_pptx, "rb") as f: pptx_bytes = f.read()
        bar.progress(100)
        status.empty()

        st.markdown('<div class="ok-banner">✦ Proof of Execution deck generated successfully!</div>', unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("URLs",         len(analysis.get("urls", [])))
        m2.metric("PDF Images",   len(extraction.get("images", [])))
        m3.metric("Syndication",  len(analysis.get("syndication_results", [])))
        m4.metric("Advert Files", len(advert_paths))

        t1, t2, t3, t4 = st.tabs(["🔗 URLs", "📸 Screenshots", "📢 Syndication", "💼 LinkedIn"])
        with t1:
            for i, u in enumerate(analysis.get("urls", []), 1):
                st.markdown(f'<div class="ritem"><b style="color:#7c3aed">#{i}</b> &nbsp;{u}</div>', unsafe_allow_html=True)
            if not analysis.get("urls"): st.info("No URLs found.")
        with t2:
            imgs = extraction.get("images", [])
            if imgs:
                for r in range(0, min(9, len(imgs)), 3):
                    cols = st.columns(3)
                    for j, c in enumerate(cols):
                        if r+j < len(imgs):
                            with c:
                                try: st.image(imgs[r+j], use_container_width=True)
                                except: st.caption(Path(imgs[r+j]).name)
            else: st.info("No images found.")
        with t3:
            for item in analysis.get("syndication_results", []):
                st.markdown(f'<div class="ritem">{item}</div>', unsafe_allow_html=True)
            if not analysis.get("syndication_results"): st.info("No syndication data.")
        with t4:
            for item in analysis.get("linkedin_results", []):
                st.markdown(f'<div class="ritem">{item}</div>', unsafe_allow_html=True)
            if advert_paths:
                st.markdown("**Uploaded advert images:**")
                for r in range(0, min(6, len(advert_paths)), 3):
                    cols = st.columns(3)
                    for j, c in enumerate(cols):
                        if r+j < len(advert_paths):
                            with c:
                                try: st.image(advert_paths[r+j], use_container_width=True)
                                except: st.caption(Path(advert_paths[r+j]).name)

        st.markdown('<div class="div"></div>', unsafe_allow_html=True)
        st.download_button(
            label="⬇️  Download proof_of_execution.pptx",
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
