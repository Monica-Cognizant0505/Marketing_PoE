"""
extractor.py  —  Extract content from the Content Syndication PDF.

Page 1 : URL (text after "URL:" label) + largest embedded image = screenshot
Page 2+: Rendered as a high-res PNG = results table image for Slide 4
"""

import os
import re
import fitz   # PyMuPDF


def extract_pdf_content(pdf_path: str, output_dir: str) -> dict:
    images_dir = os.path.join(output_dir, "extracted_images")
    os.makedirs(images_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    text_pages:       list[str] = []
    all_image_paths:  list[str] = []
    slide3_url        = ""
    slide3_screenshot = None
    slide4_table_img  = None

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        text_pages.append(text.strip())

        # ── Page 1: URL + screenshot ──────────────────────────────────────────
        if page_num == 0:
            # Try "URL:" label first
            url_match = re.search(r'URL\s*[:\-]\s*(.+)', text, re.I)
            if url_match:
                slide3_url = url_match.group(1).strip()
            else:
                # Fallback: first line that looks like a URL
                for line in text.splitlines():
                    line = line.strip()
                    if re.match(r'https?://', line) or (
                        '.' in line and len(line) > 12
                        and not any(c in line for c in [' ', '\t'])
                        and not line.lower().startswith(('screenshot','content','url','the ','a '))
                    ):
                        slide3_url = line
                        break

            # Largest embedded image on page 1 = screenshot
            best_img, best_size = None, 0
            for img_info in page.get_images(full=True):
                xref = img_info[0]
                try:
                    bi = doc.extract_image(xref)
                    if len(bi["image"]) > best_size:
                        best_size, best_img = len(bi["image"]), bi
                except Exception:
                    continue
            if best_img and best_size > 5_000:
                ext  = best_img.get("ext", "png")
                path = os.path.join(images_dir, f"slide3_screenshot.{ext}")
                with open(path, "wb") as f:
                    f.write(best_img["image"])
                slide3_screenshot = path
                all_image_paths.append(path)

        # ── Page 2+: Render whole page → results table ────────────────────────
        else:
            mat  = fitz.Matrix(2.5, 2.5)   # 180 dpi — crisp table text
            pix  = page.get_pixmap(matrix=mat, alpha=False)
            path = os.path.join(images_dir, f"slide4_results_p{page_num+1}.png")
            pix.save(path)
            if slide4_table_img is None:
                slide4_table_img = path   # use page 2 as the table image
            all_image_paths.append(path)

    doc.close()

    return {
        "text_pages":        text_pages,
        "full_text":         "\n\n--- PAGE BREAK ---\n\n".join(text_pages),
        "images":            all_image_paths,
        "slide3_url":        slide3_url,
        "slide3_screenshot": slide3_screenshot,
        "slide4_table_img":  slide4_table_img,
        "advert_images":     [],    # filled by app.py
    }
