from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

import generate_resume as base


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / "output/pdf/潘锐琦-Android开发工程师-HR优化版.pdf"
PAGE_W, PAGE_H = A4

# Preserve the existing navy/teal identity on a warm paper tone.
BG = colors.HexColor("#F5F2EA")
DARK = colors.HexColor("#102D38")
TEXT = colors.HexColor("#2F4851")
MUTED = colors.HexColor("#6F8288")
TEAL = colors.HexColor("#00A79D")
LINE = colors.HexColor("#B7C7C3")
SOFT = colors.HexColor("#E7EEEA")
PAPER = colors.HexColor("#FBF8F1")


def configure_base() -> None:
    base.BG = BG
    base.DARK = DARK
    base.TEXT = TEXT
    base.MUTED = MUTED
    base.TEAL = TEAL
    base.LINE = LINE
    base.SOFT = SOFT
    base.PAPER = PAPER

    body = base.STYLES["body"]
    body.fontSize = 9
    body.leading = 12.2
    body.textColor = TEXT
    body.spaceAfter = 1.8

    bullet = base.STYLES["bullet"]
    bullet.fontSize = 9
    bullet.leading = 12.2
    bullet.textColor = TEXT
    bullet.leftIndent = 11
    bullet.bulletIndent = 1
    bullet.bulletFontSize = 6.2
    bullet.bulletColor = TEAL
    bullet.spaceAfter = 1.9

    job = base.STYLES["job"]
    job.fontSize = 11
    job.leading = 13.4
    job.textColor = DARK
    job.spaceBefore = 1
    job.spaceAfter = 2

    date = base.STYLES["date"]
    date.fontSize = 8.8
    date.leading = 11
    date.textColor = MUTED
    date.alignment = TA_RIGHT

    project = base.STYLES["project"]
    project.fontSize = 11
    project.leading = 13.4
    project.textColor = DARK
    project.spaceAfter = 0.6

    tags = base.STYLES["tags"]
    tags.fontSize = 8.2
    tags.leading = 10
    tags.textColor = MUTED
    tags.spaceAfter = 1.5

    links = base.STYLES["links"]
    links.fontSize = 8.1
    links.leading = 10.1
    links.textColor = MUTED
    links.leftIndent = 11
    links.spaceAfter = 2.3

    section_en = base.STYLES["section_en"]
    section_en.fontSize = 6.8
    section_en.leading = 7

    section_cn = base.STYLES["section_cn"]
    section_cn.fontSize = 12.8
    section_cn.leading = 14.5

    section_no = base.STYLES["section_no"]
    section_no.fontSize = 7.2
    section_no.leading = 7.4

    base.section = section
    base.job = job_block
    base.project = project_block


def section(number: str, english: str, chinese: str):
    labels = Table(
        [
            [
                Paragraph(number, base.STYLES["section_no"]),
                [
                    Paragraph(english, base.STYLES["section_en"]),
                    Paragraph(chinese, base.STYLES["section_cn"]),
                ],
            ]
        ],
        colWidths=[8 * mm, 156 * mm],
        rowHeights=[9.5 * mm],
    )
    labels.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), TEAL),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ("LEFTPADDING", (0, 0), (0, 0), 0),
                ("RIGHTPADDING", (0, 0), (0, 0), 0),
                ("LEFTPADDING", (1, 0), (1, 0), 7),
                ("RIGHTPADDING", (1, 0), (1, 0), 0),
                ("TOPPADDING", (1, 0), (1, 0), 1),
                ("BOTTOMPADDING", (1, 0), (1, 0), 0),
                ("LINEBELOW", (1, 0), (1, 0), 0.55, LINE),
            ]
        )
    )
    return [Spacer(1, 1.4 * mm), labels, Spacer(1, 0.9 * mm)]


def job_block(title: str, date: str, bullets: list[str]):
    heading = Table(
        [
            [
                Paragraph(title, base.STYLES["job"]),
                Paragraph(date, base.STYLES["date"]),
            ]
        ],
        colWidths=[120 * mm, 44 * mm],
    )
    heading.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("LINEBELOW", (0, 0), (-1, -1), 0.35, SOFT),
            ]
        )
    )
    return [
        heading,
        *[base.bullet(item) for item in bullets],
        Spacer(1, 0.9 * mm),
    ]


def project_block(title: str, tags: str | None, bullets: list[str]):
    heading_content = [Paragraph(title, base.STYLES["project"])]
    if tags:
        heading_content.append(Paragraph(tags, base.STYLES["tags"]))
    heading = Table(
        [["", heading_content]],
        colWidths=[1.4 * mm, 162.6 * mm],
    )
    heading.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), TEAL),
                ("BACKGROUND", (1, 0), (1, 0), PAPER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (0, 0), 0),
                ("RIGHTPADDING", (0, 0), (0, 0), 0),
                ("TOPPADDING", (0, 0), (0, 0), 0),
                ("BOTTOMPADDING", (0, 0), (0, 0), 0),
                ("LEFTPADDING", (1, 0), (1, 0), 6),
                ("RIGHTPADDING", (1, 0), (1, 0), 4),
                ("TOPPADDING", (1, 0), (1, 0), 2.6),
                ("BOTTOMPADDING", (1, 0), (1, 0), 2.2),
            ]
        )
    )
    return [
        Spacer(1, 0.9 * mm),
        KeepTogether([heading, Spacer(1, 0.6 * mm), base.bullet(bullets[0])]),
        *[base.bullet(item) for item in bullets[1:]],
    ]


class ResumeHrDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=24 * mm,
            rightMargin=22 * mm,
            bottomMargin=15 * mm,
            topMargin=12 * mm,
            title="潘锐琦 - Android 开发工程师简历",
            author="潘锐琦",
        )
        first_frame = Frame(
            24 * mm,
            15 * mm,
            PAGE_W - 46 * mm,
            PAGE_H - 82 * mm,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            id="first",
        )
        second_frame = Frame(
            24 * mm,
            15 * mm,
            PAGE_W - 46 * mm,
            PAGE_H - 35 * mm,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            id="second",
        )
        self.addPageTemplates(
            [
                PageTemplate(id="First", frames=[first_frame], onPage=draw_first_page),
                PageTemplate(id="Later", frames=[second_frame], onPage=draw_later_page),
            ]
        )

    def afterPage(self):
        if self.page == 1:
            self.handle_nextPageTemplate("Later")


def draw_background(canvas) -> None:
    canvas.saveState()
    canvas.setFillColor(BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    canvas.setStrokeColor(colors.HexColor("#D8E0DB"))
    canvas.setLineWidth(0.35)
    canvas.line(18 * mm, 15 * mm, 18 * mm, PAGE_H - 15 * mm)
    canvas.restoreState()


def draw_footer(canvas, page_number: int) -> None:
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.35)
    canvas.line(22 * mm, 11.5 * mm, PAGE_W - 22 * mm, 11.5 * mm)
    canvas.setFont("Avenir-Demi", 6.7)
    canvas.setFillColor(MUTED)
    canvas.drawString(22 * mm, 6.1 * mm, "PAN RUIQI · ANDROID ENGINEER")
    canvas.drawRightString(PAGE_W - 22 * mm, 6.1 * mm, f"{page_number:02d}")
    canvas.restoreState()


def add_text_link(canvas, text: str, url: str, x: float, y: float, font: str, size: float):
    width = pdfmetrics.stringWidth(text, font, size)
    canvas.linkURL(
        url,
        (x, y - 1.5, x + width, y + size + 1.5),
        relative=0,
        thickness=0,
    )


def draw_first_page(canvas, doc) -> None:
    draw_background(canvas)
    canvas.saveState()

    canvas.setFillColor(SOFT)
    canvas.roundRect(
        22 * mm,
        PAGE_H - 62 * mm,
        PAGE_W - 44 * mm,
        48 * mm,
        2.5 * mm,
        stroke=0,
        fill=1,
    )
    canvas.setFillColor(TEAL)
    canvas.rect(22 * mm, PAGE_H - 62 * mm, 1.3 * mm, 48 * mm, stroke=0, fill=1)

    canvas.setFont("Avenir-Demi", 7.4)
    canvas.setFillColor(TEAL)
    canvas.drawString(28 * mm, PAGE_H - 22 * mm, "ANDROID · PERFORMANCE · ENGINEERING")

    canvas.setFont("CN-Medium", 23)
    canvas.setFillColor(DARK)
    canvas.drawString(28 * mm, PAGE_H - 34.5 * mm, "潘锐琦")

    canvas.setFont("CN-Medium", 10.6)
    canvas.setFillColor(TEXT)
    canvas.drawString(
        28 * mm,
        PAGE_H - 43.5 * mm,
        "Android开发工程师｜2年+软件开发经验｜性能与稳定性方向",
    )

    contact_x = 28 * mm
    contact_y = PAGE_H - 52.5 * mm
    canvas.setFont("Avenir-Regular", 7.8)
    canvas.setFillColor(MUTED)
    contact = "19212064006 · qq934137388@gmail.com"
    canvas.drawString(contact_x, contact_y, contact)
    email_prefix = "19212064006 · "
    email_x = contact_x + pdfmetrics.stringWidth(
        email_prefix, "Avenir-Regular", 7.8
    )
    add_text_link(
        canvas,
        "qq934137388@gmail.com",
        "mailto:qq934137388@gmail.com",
        email_x,
        contact_y,
        "Avenir-Regular",
        7.8,
    )

    github_y = PAGE_H - 58.2 * mm
    canvas.setFillColor(TEAL)
    canvas.drawString(contact_x, github_y, "github.com/jjjjjjava")
    add_text_link(
        canvas,
        "github.com/jjjjjjava",
        "https://github.com/jjjjjjava",
        contact_x,
        github_y,
        "Avenir-Regular",
        7.8,
    )

    if base.PROFILE_IMAGE.exists():
        x = PAGE_W - 49 * mm
        y = PAGE_H - 55.5 * mm
        w = 23 * mm
        h = 32.5 * mm
        canvas.setFillColor(TEAL)
        canvas.rect(
            x + 1.3 * mm,
            y - 1.3 * mm,
            w + 1.2 * mm,
            h + 1.2 * mm,
            stroke=0,
            fill=1,
        )
        canvas.setFillColor(PAPER)
        canvas.rect(
            x - 1 * mm,
            y - 1 * mm,
            w + 2 * mm,
            h + 2 * mm,
            stroke=0,
            fill=1,
        )
        canvas.drawImage(
            str(base.PROFILE_IMAGE),
            x,
            y,
            width=w,
            height=h,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )

    canvas.restoreState()
    draw_footer(canvas, 1)


def draw_later_page(canvas, doc) -> None:
    draw_background(canvas)
    canvas.saveState()
    page_number = doc.page
    page_title = {2: "SELECTED WORK", 3: "OPEN SOURCE"}.get(
        page_number, "SELECTED WORK"
    )
    canvas.setFont("Avenir-Demi", 11.5)
    canvas.setFillColor(DARK)
    canvas.drawString(22 * mm, PAGE_H - 13.5 * mm, page_title)
    canvas.setFont("CN-Light", 7.4)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(
        PAGE_W - 22 * mm,
        PAGE_H - 13.5 * mm,
        "潘锐琦 · Android开发工程师",
    )
    canvas.setFillColor(TEAL)
    canvas.rect(22 * mm, PAGE_H - 17.5 * mm, 27 * mm, 0.65 * mm, stroke=0, fill=1)
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.35)
    canvas.line(49 * mm, PAGE_H - 17.2 * mm, PAGE_W - 22 * mm, PAGE_H - 17.2 * mm)
    canvas.restoreState()
    draw_footer(canvas, page_number)


def build_hr_story():
    configure_base()
    return base.build_story()


def main() -> None:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = ResumeHrDocTemplate(str(output))
    doc.build(build_hr_story())
    print(output)


if __name__ == "__main__":
    main()
