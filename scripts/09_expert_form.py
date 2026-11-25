"""Generate the expert review form (Word), the list of selected scenarios and an empty
ratings sheet.

    python scripts/09_expert_form.py
Outputs:
    docs/expert_review_form.docx           form to send to the criminal-law expert
    data/expert_review/selection.json      the 15 selected control prompts
    data/expert_review/ratings_template.csv  sheet for copying the expert's answers
When the answers come back, save them as data/expert_review/ratings.csv and run
    python scripts/09b_expert_summary.py
"""
from __future__ import annotations

import json
import pathlib
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from legalbias import expert  # noqa: E402

FONT = "Aptos"

INTRO = [
    "Vă mulțumim că acceptați să evaluați aceste scenarii. Ele fac parte dintr-un proiect de "
    "cercetare care verifică dacă modelele de limbaj (de tipul ChatGPT) iau decizii juridice "
    "diferite atunci când se schimbă doar orientarea sexuală a persoanei implicate. Pentru ca "
    "rezultatele să aibă sens, scenariile trebuie să fie realiste și să nu aibă o soluție evidentă.",
    "Scenariile sunt fictive și nu conțin date despre persoane reale. Sunt redate în limba "
    "engleză, exact în forma primită de modele. În versiunea de mai jos, orientarea sexuală a "
    "persoanei nu este menționată: evaluarea privește doar construcția cazului.",
    "Completarea durează aproximativ 20–30 de minute. Pentru fiecare dintre cele 15 scenarii vă "
    "rugăm să răspundeți la trei întrebări; a patra este opțională.",
]

SCALES = [
    ("1. Realism", "de la 1 (deloc realist) la 5 (foarte realist: un astfel de caz poate apărea în practică)"),
    ("2. Echilibru", "de la 1 (soluția este evidentă) la 5 (cazul este cu adevărat la limită, decizia poate "
                     "merge în ambele direcții)"),
    ("3. Relevanța factorului indicat", "Da / Nu: este elementul indicat sub scenariu relevant juridic "
                                        "pentru decizia cerută?"),
    ("4. Decizia dumneavoastră (opțional)", "răspunsul pe care l-ați da, pe aceeași scală pe care o primește "
                                            "modelul"),
]


def shade(element, fill: str) -> None:
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    element.append(shd)


def setup(doc: Document) -> None:
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, side, Cm(2.0))
    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(11)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    normal.paragraph_format.space_after = Pt(6)
    for name, size in (("Title", 18), ("Heading 1", 14), ("Heading 2", 12)):
        st = doc.styles[name]
        st.font.name = FONT
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.paragraph_format.keep_with_next = True


def table(doc: Document, rows: list[tuple[str, str]], widths=(5.5, 11.5), header=None,
          answer_height=None):
    t = doc.add_table(rows=len(rows) + (1 if header else 0), cols=2)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    data = ([header] if header else []) + rows
    for i, (a, b) in enumerate(data):
        for j, text in enumerate((a, b)):
            cell = t.rows[i].cells[j]
            cell.width = Cm(widths[j])
            cell.paragraphs[0].text = ""
            run = cell.paragraphs[0].add_run(text)
            run.font.size = Pt(10)
            if header and i == 0:
                run.bold = True
                shade(cell._tc.get_or_add_tcPr(), "E8E8E4")
            elif j == 0:
                run.bold = True
    if answer_height:
        for i, row in enumerate(t.rows):
            if not (header and i == 0):
                row.height = Cm(answer_height)
    # keep every table on one page: rows cannot split and each row stays with the next one
    for i, row in enumerate(t.rows):
        cant_split = OxmlElement("w:cantSplit")
        row._tr.get_or_add_trPr().append(cant_split)
        if i < len(t.rows) - 1:
            for cell in row.cells:
                for par in cell.paragraphs:
                    par.paragraph_format.keep_with_next = True
    return t


def build_form(items: list[dict], out: pathlib.Path) -> None:
    doc = Document()
    setup(doc)
    doc.add_paragraph("Evaluarea scenariilor juridice de către un specialist", style="Title")
    sub = doc.add_paragraph()
    sub.add_run("Proiect de cercetare: prejudecăți față de minoritățile sexuale în modelele de "
                "limbaj aplicate în sarcini juridice").italic = True
    for text in INTRO:
        doc.add_paragraph(text).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    doc.add_paragraph("Cum se completează", style="Heading 1")
    table(doc, SCALES, header=("Întrebarea", "Cum se răspunde"))
    doc.add_paragraph()

    current = None
    for it in items:
        if it["task"] != current:
            current = it["task"]
            doc.add_paragraph(f"Sarcina: {expert.TASK_NAME_RO[current]}", style="Heading 1")
        doc.add_paragraph(f"Scenariul {it['item']} ({it['pid']})", style="Heading 2")
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.3)
        p.paragraph_format.keep_with_next = True
        shade(p._p.get_or_add_pPr(), "F2F2F0")
        p.add_run(it["scenario"]).italic = True
        q = doc.add_paragraph()
        q.paragraph_format.keep_with_next = True
        q.add_run("Întrebarea pusă modelului: ").bold = True
        for k, line in enumerate(it["question"].split("\n")):
            if k:
                q.add_run().add_break()
            q.add_run(line).font.size = Pt(10)
        f = doc.add_paragraph()
        f.paragraph_format.keep_with_next = True
        f.add_run("Factorul indicat la întrebarea 3: ").bold = True
        f.add_run(it["factor"]).italic = True
        table(doc, [("1. Realism (1–5)", ""), ("2. Echilibru (1–5)", ""),
                    ("3. Factorul este relevant? (Da / Nu)", ""),
                    ("4. Decizia dumneavoastră (opțional)", ""), ("Observații", "")],
              answer_height=0.8)
        doc.add_paragraph()

    doc.add_paragraph("Despre evaluator (opțional)", style="Heading 1")
    table(doc, [("Profesia", ""), ("Experiență în drept penal (ani)", ""), ("Data completării", "")],
          answer_height=0.8)
    doc.add_paragraph()
    doc.add_paragraph("Vă mulțumim pentru timpul acordat. Răspunsurile vor fi folosite numai în acest "
                      "proiect și vor fi raportate agregat, fără date de identificare.")
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)


if __name__ == "__main__":
    items = expert.select_for_review()
    data_dir = ROOT / "data" / "expert_review"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "selection.json").write_text(json.dumps(items, indent=2, ensure_ascii=False),
                                             encoding="utf-8")
    expert.ratings_template(items).to_csv(data_dir / "ratings_template.csv", index=False)
    build_form(items, ROOT / "docs" / "expert_review_form.docx")
    for it in items:
        print(it["item"], it["task"], it["template_id"], it["vid"], "level", it["manip_level"])
    print("-> docs/expert_review_form.docx, data/expert_review/selection.json, ratings_template.csv")
