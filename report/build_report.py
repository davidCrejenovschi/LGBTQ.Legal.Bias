"""Build the Lab5-8 report (.docx) from the Markdown sources in report/.

Supported markup (a small, predictable subset):
    # / ## / ###          headings (chapter / section / subsection)
    blank line            paragraph break
    - item                bullet
    | a | b |             table (first row = header, second row = ---)
    Table: caption        caption of the next table (numbered automatically)
    ![caption](path)      figure (numbered automatically)
    $$ latex $$ (n)       display equation, rendered with matplotlib mathtext
    > text                monospaced box (prompt examples)
    [[include:file.md]]   include a generated snippet
    \\newpage             page break
    **bold**, *italic*, `code`

    python report/build_report.py   ->  IV.docx (repository root)
"""
from __future__ import annotations

import io
import pathlib
import re
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from docx import Document  # noqa: E402
from docx.enum.section import WD_SECTION  # noqa: E402,F401
from docx.enum.table import WD_TABLE_ALIGNMENT  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Cm, Pt, RGBColor  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCES = ["00_front.md", "01_modelare.md", "02_studiu_de_caz.md", "03_related_work.md",
           "04_repository.md", "99_bibliografie.md"]
OUT = ROOT / "IV.docx"
FONT = "Aptos"
BODY_PT = 12

plt.rcParams.update({"mathtext.fontset": "cm", "font.size": 13})


# ---------------------------------------------------------------- styles
def setup(doc: Document) -> None:
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.59), Cm(27.94)       # Letter, as in Lab I-III
    for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, side, Cm(2.0))
    st = doc.styles
    normal = st["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(BODY_PT)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    pf = normal.paragraph_format
    pf.space_after = Pt(6)
    pf.line_spacing = 1.15
    for name, size, italic in (("Heading 1", 16, False), ("Heading 2", 13, False),
                               ("Heading 3", 12, True)):
        h = st[name]
        h.font.name = FONT
        h.font.size = Pt(size)
        h.font.bold = True
        h.font.italic = italic
        h.font.color.rgb = RGBColor(0, 0, 0)
        rpr = h.element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            rpr.append(rfonts)
        for k in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            rfonts.set(qn(k), FONT)
        for k in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            if rfonts.get(qn(k)) is not None:
                del rfonts.attrib[qn(k)]
        h.paragraph_format.space_before = Pt(16 if name == "Heading 1" else 10)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
    cap = st["Caption"]
    cap.font.name = FONT
    cap.font.size = Pt(10)
    cap.font.italic = False
    cap.font.bold = False
    cap.font.color.rgb = RGBColor(0x33, 0x33, 0x33)


# ------------------------------------------------------------ inline runs
INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")


def add_inline(par, text: str, size: float | None = None) -> None:
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**"):
            run = par.add_run(part[2:-2])
            run.bold = True
        elif part.startswith("`"):
            run = par.add_run(part[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt((size or BODY_PT) - 1.5)
        elif part.startswith("*"):
            run = par.add_run(part[1:-1])
            run.italic = True
        else:
            run = par.add_run(part)
        if size and not part.startswith("`"):
            run.font.size = Pt(size)


def shade(cell_or_par_element, fill: str) -> None:
    pr = cell_or_par_element
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pr.append(shd)


# ---------------------------------------------------------------- blocks
class Builder:
    def __init__(self):
        self.doc = Document()
        setup(self.doc)
        self.n_table = 0
        self.n_figure = 0
        self.pending_caption: str | None = None

    def heading(self, text: str, level: int):
        self.doc.add_heading(text, level=level)

    def paragraph(self, text: str):
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        add_inline(p, text)

    def bullet(self, text: str):
        p = self.doc.add_paragraph(style="List Bullet")
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(3)
        add_inline(p, text)

    def code_box(self, lines: list[str]):
        for i, line in enumerate(lines):
            p = self.doc.add_paragraph()
            pf = p.paragraph_format
            pf.space_after = Pt(0) if i < len(lines) - 1 else Pt(8)
            pf.space_before = Pt(0)
            pf.line_spacing = 1.0
            pf.left_indent = Cm(0.4)
            pf.right_indent = Cm(0.4)
            shade(p._p.get_or_add_pPr(), "F2F2F0")
            run = p.add_run(line if line else " ")
            run.font.name = "Consolas"
            run.font.size = Pt(9)

    def table(self, rows: list[list[str]]):
        header, body = rows[0], rows[1:]
        if self.pending_caption:
            self.n_table += 1
            p = self.doc.add_paragraph(style="Caption")
            p.paragraph_format.keep_with_next = True
            add_inline(p, f"**Tabelul {self.n_table}.** {self.pending_caption}", size=10)
            self.pending_caption = None
        t = self.doc.add_table(rows=1 + len(body), cols=len(header))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        size = 9 if len(header) >= 6 else 10
        for j, h in enumerate(header):
            c = t.rows[0].cells[j]
            c.paragraphs[0].text = ""
            add_inline(c.paragraphs[0], f"**{h}**" if h and not h.startswith("**") else h, size=size)
            shade(c._tc.get_or_add_tcPr(), "E8E8E4")
        for i, row in enumerate(body, start=1):
            for j in range(len(header)):
                c = t.rows[i].cells[j]
                c.paragraphs[0].text = ""
                add_inline(c.paragraphs[0], row[j] if j < len(row) else "", size=size)
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs:
                    p.paragraph_format.space_after = Pt(1)
                    p.paragraph_format.line_spacing = 1.0
        # repeat header row on page breaks
        trpr = t.rows[0]._tr.get_or_add_trPr()
        el = OxmlElement("w:tblHeader")
        el.set(qn("w:val"), "true")
        trpr.append(el)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(2)

    def figure(self, caption: str, path: str):
        img = (HERE / path) if not pathlib.Path(path).is_absolute() else pathlib.Path(path)
        if not img.exists():
            self.paragraph(f"[figura lipsă: {path}]")
            return
        self.n_figure += 1
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(str(img), width=Cm(16.5))
        c = self.doc.add_paragraph(style="Caption")
        c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_inline(c, f"**Figura {self.n_figure}.** {caption}", size=10)

    def equation(self, latex: str, number: str | None):
        fig = plt.figure(figsize=(0.01, 0.01))
        fig.text(0, 0, f"${latex}$", fontsize=13)
        buf = io.BytesIO()
        fig.savefig(buf, dpi=300, bbox_inches="tight", pad_inches=0.03, transparent=True)
        plt.close(fig)
        buf.seek(0)
        from PIL import Image
        w_px, h_px = Image.open(buf).size
        buf.seek(0)
        p = self.doc.add_paragraph()
        usable = 21.59 - 4.0
        p.paragraph_format.tab_stops.add_tab_stop(Cm(usable / 2), WD_TAB_ALIGNMENT.CENTER)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(usable), WD_TAB_ALIGNMENT.RIGHT)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(8)
        p.add_run("\t")
        width_cm = min(w_px / 300 * 2.54, usable - 2.5)
        p.add_run().add_picture(buf, width=Cm(width_cm))
        if number:
            p.add_run(f"\t({number})")

    def page_break(self):
        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def expand_includes(text: str) -> str:
    def repl(m):
        return (HERE / m.group(1)).read_text(encoding="utf-8")
    return re.sub(r"\[\[include:([^\]]+)\]\]", repl, text)


def render(md: str, b: Builder) -> None:
    lines = expand_includes(md).splitlines()
    i, para = 0, []

    def flush():
        if para:
            b.paragraph(" ".join(s.strip() for s in para))
            para.clear()

    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            flush()
        elif s.startswith("<!--"):
            flush()
            while "-->" not in lines[i]:
                i += 1
        elif s == r"\newpage":
            flush()
            b.page_break()
        elif s.startswith("::title ") or s.startswith("::center "):
            flush()
            is_title = s.startswith("::title ")
            p = b.doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_inline(p, s.split(" ", 1)[1], size=16 if is_title else BODY_PT)
            if is_title:
                for r in p.runs:
                    r.bold = True
                p.paragraph_format.space_after = Pt(12)
        elif s.startswith("#"):
            flush()
            level = len(s) - len(s.lstrip("#"))
            b.heading(s[level:].strip(), level)
        elif s.startswith("- "):
            flush()
            b.bullet(s[2:])
        elif s.startswith("Table:"):
            flush()
            b.pending_caption = s[len("Table:"):].strip()
        elif s.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            b.table(rows)
            continue
        elif s.startswith("!["):
            flush()
            m = re.match(r"!\[(.*)\]\((.+)\)", s)
            b.figure(m.group(1), m.group(2))
        elif s.startswith("$$"):
            flush()
            m = re.match(r"\$\$(.+)\$\$\s*(?:\((\w+)\))?", s)
            b.equation(m.group(1).strip(), m.group(2))
        elif s.startswith(">"):
            flush()
            block = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                block.append(lines[i].strip()[1:].removeprefix(" "))
                i += 1
            b.code_box(block)
            continue
        else:
            para.append(s)
        i += 1
    flush()


def main(out: pathlib.Path = OUT) -> None:
    b = Builder()
    for name in SOURCES:
        path = HERE / name
        if path.exists():
            render(path.read_text(encoding="utf-8"), b)
    b.doc.core_properties.title = "Lab5-8 - Partea aplicativa a raportului de cercetare"
    b.doc.save(out)
    print(f"{out}  ({b.n_table} tabele, {b.n_figure} figuri)")


if __name__ == "__main__":
    main(pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else OUT)
