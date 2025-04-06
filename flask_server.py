from flask import Flask, request, jsonify
from flask_cors import CORS

import fitz  # PyMuPDF
import re
import os

app = Flask(__name__)
CORS(app)
def refined_author_blur(pdf_path, output_pdf_path):
    doc = fitz.open(pdf_path)
    exclusion_areas = []

    abstract_page_y = None
    references_page_y = None

    for page_num, page in enumerate(doc):
        text = page.get_text("text")
        page_rect = page.rect

        abs_instances = page.search_for("Abstract", quads=False) or page.search_for("ABSTRACT", quads=False)
        if abs_instances and abstract_page_y is None:
            abstract_page_y = (page_num, abs_instances[0].y0)

        ref_instances = page.search_for("References", quads=False) or page.search_for("REFERENCES", quads=False)
        if ref_instances:
            references_page_y = (page_num, ref_instances[-1].y1)

    if abstract_page_y and references_page_y:
        p1, y1 = abstract_page_y
        p2, y2 = references_page_y
        for pnum in range(p1, p2 + 1):
            page = doc[pnum]
            if p1 == p2:
                exclusion_areas.append((pnum, fitz.Rect(0, y1, page.rect.x1, y2)))
            elif pnum == p1:
                exclusion_areas.append((pnum, fitz.Rect(0, y1, page.rect.x1, page.rect.y1)))
            elif pnum == p2:
                exclusion_areas.append((pnum, fitz.Rect(0, 0, page.rect.x1, y2)))
            else:
                exclusion_areas.append((pnum, page.rect))

    for page_num, page in enumerate(doc):
        text = page.get_text("text")

        def is_in_exclusion(r):
            return any(pnum == page_num and r.intersects(rect) for pnum, rect in exclusion_areas)

        author_pattern = r"\b([A-ZÇĞİÖŞÜ][a-zçğıöşü]{1,20}(?: [A-ZÇĞİÖŞÜ][a-zçğıöşü]{1,20})?|[A-ZÇĞİÖŞÜ]{2,20}(?: [A-ZÇĞİÖŞÜ]{2,20})+)\b"
        for match in re.findall(author_pattern, text):
            for inst in page.search_for(match, quads=False):
                if not is_in_exclusion(inst):
                    page.add_redact_annot(inst, fill=(0.6, 0.6, 0.6))

        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        for match in re.findall(email_pattern, text):
            for inst in page.search_for(match, quads=False):
                if not is_in_exclusion(inst):
                    page.add_redact_annot(inst, fill=(0.6, 0.6, 0.6))

        institution_keywords = ["University", "Institute", "Faculty", "Department", "Technology"]
        for keyword in institution_keywords:
            for inst in page.search_for(keyword, quads=False):
                if not is_in_exclusion(inst):
                    page.add_redact_annot(inst, fill=(0.6, 0.6, 0.6))

        page.apply_redactions()

    doc.save(output_pdf_path)
    print(f"✅ Anonimleştirildi: {output_pdf_path}")

@app.route("/anonimize-et", methods=["POST"])
def anonymize_pdf():
    data = request.get_json()
    input_path = data.get("input_path")
    output_path = data.get("output_path")

    if not os.path.exists(input_path):
        return jsonify({"error": "Girdi dosyası bulunamadı."}), 404

    try:
        refined_author_blur(input_path, output_path)
        return jsonify({"message": "✅ Anonimleştirme tamamlandı!", "output_path": output_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5001)
