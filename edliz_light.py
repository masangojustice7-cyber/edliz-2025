"""
EDLIZ 2025 - LIGHT VERSION FOR TERMUX - pypdf version
No PyMuPDF. No Streamlit. Only pypdf + Python built-in.
Run: python edliz_light.py
Open Chrome: http://localhost:8000
"""
import sqlite3, os, html
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

PDF_FILE = "EDLIZ-2025.pdf"
DB_FILE = "edliz.db"
import os
PORT = int(os.environ.get("PORT", 8000))

CHAPTERS = [
    (1, "Antimicrobial", 26), (2, "Infection Prevention", 33),
    (3, "Paediatric", 41), (4, "Immunisation", 93),
    (5, "Obstetric & Gynae", 100), (6, "STIs", 127),
    (7, "Hepatitis B & C", 144), (8, "HIV Related", 155),
    (9, "ART", 182), (10, "Paediatric HIV", 207),
    (11, "PMTCT", 216), (12, "Tuberculosis", 219),
    (13, "Tropical Diseases", 235), (14, "Malaria", 254),
    (15, "Respiratory", 272), (16, "Cardiovascular", 291),
    (17, "Gastrointestinal", 314), (18, "Renal", 329),
    (19, "Rheumatological", 345), (20, "Diabetes & Endocrine", 352),
    (21, "Neurological", 372), (22, "Mental Health", 400),
    (23, "Eye", 433), (24, "Oral", 448), (25, "ENT", 454),
    (26, "Skin", 466), (27, "Burns", 478),
    (28, "Pain & Palliative", 490), (29, "Elderly", 502),
    (30, "Haematology", 520), (31, "IV Fluids", 537),
    (32, "Anaphylaxis", 545), (33, "Poisoning", 549),
    (34, "Anaesthesia", 568), (35, "Surgical", 591),
    (36, "Cancer", 601), (37, "ADRs", 610),
]

def build_index():
    from pypdf import PdfReader
    print("Building index from 673 pages... wait ~30 sec")
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("CREATE TABLE pages (chapter TEXT, book_page INTEGER, pdf_page INTEGER, text TEXT)")
    reader = PdfReader(PDF_FILE)
    print(f"Total pages: {len(reader.pages)}")
    for i, page in enumerate(reader.pages):
        pdf_page = i + 1
        book_page = pdf_page - 2
        ch = "Front Matter"
        for no, name, start in CHAPTERS:
            if book_page >= start:
                ch = f"{no}. {name}"
        txt = (page.extract_text() or "").strip()
        if txt:
            cur.execute("INSERT INTO pages VALUES (?,?,?,?)", (ch, book_page, pdf_page, txt))
        if i % 100 == 0:
            print(f"  ... {i} pages done")
    conn.commit(); conn.close()
    print("Done!")

def search(q, chapter="All"):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    if chapter != "All":
        cur.execute("SELECT chapter, book_page, pdf_page, text FROM pages WHERE chapter=? AND text LIKE ? LIMIT 20", (chapter, f"%{q}%"))
    else:
        cur.execute("SELECT chapter, book_page, pdf_page, text FROM pages WHERE text LIKE ? LIMIT 20", (f"%{q}%",))
    rows = cur.fetchall(); conn.close()
    return rows

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        # --- PWA files ---
        if parsed.path == "/manifest.json":
            self.send_response(200)
            self.send_header("Content-Type", "application/manifest+json")
            self.end_headers()
            self.wflile.write(open("manifest.json", "rb").read())
            return
if parsed.path == "/sw.js":
    self.send_response(200)
    self.send_header("Content-Type", "application/javascript")
    self.end_headers()
    self.wfile.write(open("sw.js", "rb").read())
        return
if parsed.path in ("/icon-192.png", "/icon-512.png"):
    self.send_response(200)
    self.send_header("Content-Type", "image/png")
    self.end_headers()
    self.wfile.write(open(parsed.path[1:], "rb").read())
        return
        # --- end PWA ---
    params = parse_qs(parsed.query)
    q = params.get("q", [""])[0]
    chapter = params.get("chapter", ["All"])[0]
    weight = params.get("weight", [""])[0]
    mgkg = params.get("mgkg", [""])[0]
    calc_result = ""
    if weight and mgkg:
        try:
            calc_result = f"<div style='background:#E8F5E9;padding:10px;border-radius:8px'><b>Result: {round(float(weight)*float(mgkg),1)} mg per dose</b></div>"
        except:
            calc_result = "<b>Enter valid numbers</b>"
        results_html = ""
        if len(q) >= 2:
            rows = search(q, chapter)
            results_html = f"<h3>Found {len(rows)} results for '{html.escape(q)}'</h3>"
            for ch, bp, pp, txt in rows:
                safe = html.escape(txt[:2500])
                results_html += f"<div style='background:white;padding:12px;margin:10px 0;border-radius:10px;border-left:4px solid #1B5E20'><b>{html.escape(ch)}</b> | Book p{bp} | PDF p{pp}<br><br>{safe}</div>"
        else:
            results_html = "<h3> Chapters</h3>" + "".join([f"<div>{no}. {name} - Book p{start}</div>" for no, name, start in CHAPTERS])
        chapter_options = "<option>All</option>" + "".join([f"<option {'selected' if chapter==f'{n}. {name}' else ''}>{n}. {name}</option>" for n, name, _ in CHAPTERS])
        page = f"""<!DOCTYPE html><html><head><meta charset=utf-8><meta name='viewport' content='width=device-width, initial-scale=1'>
        <title>EDLIZ 2025</title><link rel="manifest"...></script><style>
        input,select{{padding:10px;width:100%;margin:5px 0;border-radius:8px;border:1px solid #ccc;font-size:16px}}
        button{{background:#1B5E20;color:white;padding:12px;width:100%;border:none;border-radius:8px;font-size:16px}}
        .card{{background:white;padding:12px;border-radius:10px;margin:10px 0}}
        </style></head><body>
        <h1 style='color:#1B5E20'> EDLIZ 2025</h1>
        <p>9th Edition | NMTPAC / MoHCC | 673 Pages | Offline</p>
        <form><input name='q' placeholder='Search malaria, amoxicillin...' value='{html.escape(q)}'>
        <select name='chapter'>{chapter_options}</select>
        <button>Search</button></form>
        <div class='card'><h3> Dose Calculator</h3>
        <form>Weight (kg): <input name='weight' value='{weight}' placeholder='20'>
        Dose (mg/kg): <input name='mgkg' value='{mgkg}' placeholder='15'>
        <input type='hidden' name='q' value='{html.escape(q)}'>
        <button>Calculate</button></form>{calc_result}
        <p>Example: 20kg x 15mg/kg = 300mg Paracetamol</p></div>
        {results_html}
        <p style='color:#E65100;background:#FFF3E0;padding:10px;border-radius:8px'>Reference only. Verify with official EDLIZ 2025 book, allergy, renal, pregnancy & senior clinician.</p>
        <script>
if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js');
</script>
</body></html>"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(page.encode())
    def log_message(self, *a):
        pass

if __name__ == "__main__":
    if not os.path.exists(PDF_FILE):
        print(" Put EDLIZ-2025.pdf here first:")
        print("cp ~/storage/downloads/EDLIZ-2025.pdf ~/")
        raise SystemExit
    if not os.path.exists(DB_FILE):
        build_index()
    print(f"\n Open Chrome: http://localhost:{PORT}")
    print("Keep Termux open. Press CTRL+C to stop.")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
