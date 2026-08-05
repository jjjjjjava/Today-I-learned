from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / "output/pdf/潘锐琦-Android开发工程师-视觉优化版.pdf"
PROFILE_IMAGE = ROOT / "resume/assets/profile.jpg"

PAGE_W, PAGE_H = A4
BG = colors.HexColor("#F5F2EA")
DARK = colors.HexColor("#102D38")
TEXT = colors.HexColor("#334B53")
MUTED = colors.HexColor("#71858B")
TEAL = colors.HexColor("#00A79D")
LINE = colors.HexColor("#B7C7C3")
SOFT = colors.HexColor("#E7EEEA")
PAPER = colors.HexColor("#FCFAF5")


def register_fonts() -> None:
    pdfmetrics.registerFont(
        TTFont("CN-Light", "/System/Library/Fonts/STHeiti Light.ttc", subfontIndex=1)
    )
    pdfmetrics.registerFont(
        TTFont("CN-Medium", "/System/Library/Fonts/STHeiti Medium.ttc", subfontIndex=1)
    )
    pdfmetrics.registerFont(
        TTFont("Avenir-Regular", "/System/Library/Fonts/Avenir Next.ttc", subfontIndex=7)
    )
    pdfmetrics.registerFont(
        TTFont("Avenir-Demi", "/System/Library/Fonts/Avenir Next.ttc", subfontIndex=2)
    )
    pdfmetrics.registerFontFamily(
        "CN-Light",
        normal="CN-Light",
        bold="CN-Medium",
        italic="CN-Light",
        boldItalic="CN-Medium",
    )


register_fonts()


STYLES = {
    "body": ParagraphStyle(
        "body",
        fontName="CN-Light",
        fontSize=8.5,
        leading=12.2,
        textColor=TEXT,
        spaceAfter=2.4,
        wordWrap="CJK",
    ),
    "bullet": ParagraphStyle(
        "bullet",
        fontName="CN-Light",
        fontSize=8.5,
        leading=12.2,
        textColor=TEXT,
        leftIndent=12,
        firstLineIndent=0,
        bulletIndent=1,
        bulletFontName="CN-Medium",
        bulletFontSize=6.5,
        bulletColor=TEAL,
        spaceAfter=2.2,
        wordWrap="CJK",
    ),
    "job": ParagraphStyle(
        "job",
        fontName="CN-Medium",
        fontSize=10.6,
        leading=13.7,
        textColor=DARK,
        spaceBefore=2,
        spaceAfter=3,
        wordWrap="CJK",
    ),
    "date": ParagraphStyle(
        "date",
        fontName="CN-Light",
        fontSize=9.1,
        leading=12,
        textColor=DARK,
        alignment=TA_RIGHT,
    ),
    "project": ParagraphStyle(
        "project",
        fontName="CN-Medium",
        fontSize=10.7,
        leading=13.8,
        textColor=DARK,
        spaceBefore=0,
        spaceAfter=1.2,
        wordWrap="CJK",
    ),
    "tags": ParagraphStyle(
        "tags",
        fontName="CN-Light",
        fontSize=8.3,
        leading=10.5,
        textColor=MUTED,
        spaceAfter=3,
        wordWrap="CJK",
    ),
    "links": ParagraphStyle(
        "links",
        fontName="CN-Light",
        fontSize=8.2,
        leading=11,
        textColor=MUTED,
        leftIndent=12,
        spaceAfter=4,
        wordWrap="CJK",
    ),
    "section_en": ParagraphStyle(
        "section_en",
        fontName="Avenir-Demi",
        fontSize=7.1,
        leading=8,
        textColor=TEAL,
        spaceAfter=0,
    ),
    "section_cn": ParagraphStyle(
        "section_cn",
        fontName="CN-Medium",
        fontSize=14,
        leading=17,
        textColor=DARK,
    ),
    "section_no": ParagraphStyle(
        "section_no",
        fontName="Avenir-Demi",
        fontSize=7.6,
        leading=8,
        textColor=colors.white,
        alignment=TA_CENTER,
    ),
}


def bullet(text: str):
    return Paragraph(text, STYLES["bullet"], bulletText="•")


def section(number: str, english: str, chinese: str):
    labels = Table(
        [
            [
                Paragraph(number, STYLES["section_no"]),
                [
                    Paragraph(english, STYLES["section_en"]),
                    Paragraph(chinese, STYLES["section_cn"]),
                ],
            ]
        ],
        colWidths=[9 * mm, 155 * mm],
        rowHeights=[11 * mm],
    )
    labels.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), TEAL),
                ("BACKGROUND", (1, 0), (1, 0), SOFT),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ("LEFTPADDING", (0, 0), (0, 0), 0),
                ("RIGHTPADDING", (0, 0), (0, 0), 0),
                ("LEFTPADDING", (1, 0), (1, 0), 8),
                ("RIGHTPADDING", (1, 0), (1, 0), 0),
                ("TOPPADDING", (1, 0), (1, 0), 2),
                ("BOTTOMPADDING", (1, 0), (1, 0), 1),
                ("LINEBELOW", (1, 0), (1, 0), 0.8, TEAL),
            ]
        )
    )
    return [Spacer(1, 2 * mm), labels, Spacer(1, 1.2 * mm)]


def job(title: str, date: str, bullets: list[str]):
    heading = Table(
        [[Paragraph(title, STYLES["job"]), Paragraph(date, STYLES["date"])]],
        colWidths=[119 * mm, 45 * mm],
    )
    heading.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("BACKGROUND", (1, 0), (1, 0), SOFT),
                ("LEFTPADDING", (1, 0), (1, 0), 5),
                ("RIGHTPADDING", (1, 0), (1, 0), 5),
                ("TOPPADDING", (1, 0), (1, 0), 2),
                ("BOTTOMPADDING", (1, 0), (1, 0), 2),
            ]
        )
    )
    return [heading, *[bullet(item) for item in bullets], Spacer(1, 1.2 * mm)]


def project(title: str, tags: str | None, bullets: list[str]):
    heading_content = [Paragraph(title, STYLES["project"])]
    if tags:
        heading_content.append(Paragraph(tags, STYLES["tags"]))
    heading = Table(
        [["", heading_content]],
        colWidths=[2 * mm, 162 * mm],
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
                ("LEFTPADDING", (1, 0), (1, 0), 7),
                ("RIGHTPADDING", (1, 0), (1, 0), 5),
                ("TOPPADDING", (1, 0), (1, 0), 4),
                ("BOTTOMPADDING", (1, 0), (1, 0), 3),
            ]
        )
    )
    return [
        Spacer(1, 1.2 * mm),
        KeepTogether([heading, Spacer(1, 0.8 * mm), bullet(bullets[0])]),
        *[bullet(item) for item in bullets[1:]],
    ]


def link_line(items: list[tuple[str, str]]):
    links = " ｜ ".join(
        f'<link href="{url}" color="#149E96"><u>{label}</u></link>' for label, url in items
    )
    return Paragraph(f"<b>链接：</b>{links}", STYLES["links"])


class ResumeDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=24 * mm,
            rightMargin=22 * mm,
            bottomMargin=13 * mm,
            topMargin=13 * mm,
            title="潘锐琦 - Android 开发工程师简历",
            author="潘锐琦",
        )
        first_frame = Frame(
            24 * mm,
            15 * mm,
            PAGE_W - 46 * mm,
            PAGE_H - 96 * mm,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            id="first",
        )
        later_frame = Frame(
            24 * mm,
            15 * mm,
            PAGE_W - 46 * mm,
            PAGE_H - 56 * mm,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            id="later",
        )
        self.addPageTemplates(
            [
                PageTemplate(id="First", frames=[first_frame], onPage=draw_first_page),
                PageTemplate(id="Later", frames=[later_frame], onPage=draw_later_page),
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
    canvas.setFillColor(DARK)
    canvas.rect(0, 0, PAGE_W, 12 * mm, stroke=0, fill=1)
    canvas.setFillColor(TEAL)
    canvas.rect(PAGE_W - 22 * mm, 0, 22 * mm, 12 * mm, stroke=0, fill=1)
    canvas.setFont("Avenir-Demi", 7.2)
    canvas.setFillColor(colors.HexColor("#C9D5D3"))
    canvas.drawString(22 * mm, 4.4 * mm, "PAN RUIQI · ANDROID ENGINEER")
    canvas.setFillColor(colors.white)
    canvas.drawCentredString(PAGE_W - 11 * mm, 4.4 * mm, f"{page_number:02d}")
    canvas.restoreState()


def draw_first_page(canvas, doc) -> None:
    draw_background(canvas)
    canvas.saveState()
    canvas.setFillColor(DARK)
    canvas.rect(0, PAGE_H - 76 * mm, PAGE_W, 76 * mm, stroke=0, fill=1)
    canvas.setFillColor(TEAL)
    canvas.rect(0, PAGE_H - 76 * mm, 7 * mm, 76 * mm, stroke=0, fill=1)
    canvas.rect(24 * mm, PAGE_H - 75.2 * mm, 58 * mm, 0.8 * mm, stroke=0, fill=1)
    canvas.setFillColor(TEAL)
    canvas.setFont("Avenir-Demi", 8.1)
    canvas.drawString(24 * mm, PAGE_H - 22 * mm, "ANDROID · PERFORMANCE · ENGINEERING")
    canvas.setFillColor(colors.white)
    canvas.setFont("CN-Medium", 25)
    canvas.drawString(24 * mm, PAGE_H - 39 * mm, "潘锐琦")
    canvas.setFont("CN-Light", 11.2)
    canvas.setFillColor(colors.HexColor("#E6EEEC"))
    canvas.drawString(
        24 * mm,
        PAGE_H - 49 * mm,
        "Android开发工程师｜2年+软件开发经验｜性能与稳定性方向",
    )
    canvas.setFont("Avenir-Regular", 8.1)
    canvas.setFillColor(colors.HexColor("#AFC0BE"))
    canvas.drawString(24 * mm, PAGE_H - 61 * mm, "19212064006 · qq934137388@gmail.com")
    canvas.setFillColor(TEAL)
    canvas.drawString(24 * mm, PAGE_H - 69 * mm, "github.com/jjjjjjava")

    if PROFILE_IMAGE.exists():
        x, y, w, h = PAGE_W - 50 * mm, PAGE_H - 65 * mm, 27 * mm, 38 * mm
        canvas.setFillColor(TEAL)
        canvas.rect(x + 2.2 * mm, y - 2.2 * mm, w + 2.4 * mm, h + 2.4 * mm, stroke=0, fill=1)
        canvas.setFillColor(PAPER)
        canvas.rect(x - 1.5 * mm, y - 1.5 * mm, w + 3 * mm, h + 3 * mm, stroke=0, fill=1)
        canvas.drawImage(
            str(PROFILE_IMAGE),
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
    page_number = doc.page
    page_titles = {2: "SELECTED WORK", 3: "OPEN SOURCE"}
    title = page_titles.get(page_number, "SELECTED WORK")
    canvas.saveState()
    canvas.setFillColor(DARK)
    canvas.rect(0, PAGE_H - 34 * mm, PAGE_W, 34 * mm, stroke=0, fill=1)
    canvas.setFillColor(TEAL)
    canvas.rect(0, PAGE_H - 34 * mm, 7 * mm, 34 * mm, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont("Avenir-Demi", 19)
    canvas.drawString(22 * mm, PAGE_H - 21 * mm, title)
    canvas.setFont("CN-Light", 8.5)
    canvas.setFillColor(colors.HexColor("#AFC0BE"))
    canvas.drawRightString(
        PAGE_W - 22 * mm, PAGE_H - 21 * mm, "潘锐琦 · Android开发工程师"
    )
    canvas.setFillColor(TEAL)
    canvas.rect(22 * mm, PAGE_H - 27 * mm, 35 * mm, 0.8 * mm, stroke=0, fill=1)
    canvas.restoreState()
    draw_footer(canvas, page_number)


def build_story():
    story = []

    story += section("01", "EXPERTISE", "专业技能")
    story += [
        bullet(
            "<b>Android与语言：</b>Kotlin、Java、Activity/Fragment、"
            "Handler/Looper/MessageQueue、App冷启动流程。"
        ),
        bullet(
            "<b>性能与稳定性：</b>Benchmark、Perfetto/Systrace、Android Studio Profiler、"
            "Bugly ANR Trace；具备启动耗时、主线程IO、锁等待、View创建及ANR调用链分析经验。"
        ),
        bullet(
            "<b>构建与工程化：</b>Gradle/AGP、ASM字节码处理、ARouter编译期路由注册；"
            "处理过AGP 8、Java 21及复杂Variant兼容问题。"
        ),
        bullet(
            "<b>音视频与Native：</b>MediaCodec、SurfaceTexture、OpenGL ES、MediaMuxer、"
            "C/C++、FFmpeg；具备视频解码、纹理合成、水印渲染及重新编码实践。"
        ),
        bullet(
            "<b>跨端能力：</b>Flutter/Dart、MethodChannel、OpenHarmony ArkTS/AKI；"
            "具备pub.dev、OHPM及JitPack包发布经验。"
        ),
    ]

    story += section("02", "HIGHLIGHTS", "核心业绩")
    story += [
        bullet(
            "<b>启动性能治理：</b>本地冷启动Benchmark由2.98s降至1.74s，降低41.6%；"
            "线上P50由1.8s降至1.5s，P90由4.6s降至3.1s。"
        ),
        bullet(
            "<b>ARouter性能治理：</b>定位Gradle/AGP升级后插件失效并回退运行时Dex扫描的问题，"
            "将本地初始化耗时由7.84s降至100ms内，灰度低性能设备P90由12.8s恢复至4.5s。"
        ),
        bullet(
            "<b>线上稳定性治理：</b>梳理近90天Top ANR，定位并解决主线程图片压缩与文件IO阻塞、"
            "播放器释放等待等Top ANR问题，涉及约4.56万条记录、影响用户比例超过12%。"
        ),
        bullet(
            "<b>工程化与开源：</b>向ARouter Gradle插件提交Java 21兼容及构建Variant修复，"
            "2项PR均获维护者合并；向OpenHarmony-TPC FFmpeg移植仓提交硬件编码器码率参数修复，"
            "1项PR获合并；自研OpenHarmony音视频工具库，OHPM累计下载600+次；修复"
            "<font name='Avenir-Regular'>getui_flutter</font> Android通知payload丢失问题，"
            "并将自维护版本发布至pub.dev。"
        ),
    ]

    story += section("03", "EXPERIENCE", "工作经历")
    story += job(
        "万店掌｜Android开发工程师",
        "2025.04 - 至今",
        [
            "参与ToB门店数字化产品矩阵开发，负责Android业务需求及启动性能、稳定性、音视频等专项治理，"
            "同时承担部分Flutter与OpenHarmony跨端需求。",
            "负责App启动性能存量治理，结合线上监控、Benchmark与Perfetto定位首屏路径中的冗余初始化和"
            "View创建开销，推动方案落地并跟踪线上效果。",
            "负责Gradle/AGP升级后ARouter启动劣化治理，将路由扫描与注册前移至编译期，并处理Java 21"
            "字节码及复杂Variant兼容问题。",
            "基于线上监控与ANR Trace，定位并解决主线程图片压缩与文件IO阻塞、"
            "播放器释放等待等Top ANR问题，后续未再发现同类阻塞栈。",
            "完成OpenHarmony录像下载与视频加水印能力建设，并将ArkTS与Native音视频处理能力沉淀为"
            "可复用工具库。",
            "参与Android视频水印处理链路优化，使用MediaCodec与OpenGL ES完成视频解码、纹理合成及"
            "重新编码。",
        ],
    )
    story += job(
        "翼辉信息｜内核开发工程师",
        "2023.05 - 2024.06",
        [
            "参与嵌入式系统内核问题定位与维护，涉及设备树、系统启动流程及底层日志分析，"
            "曾定位并修复设备树挂载异常。",
            "参与爱智App部分UI页面及基础交互开发；底层排障经历为后续Android构建系统、"
            "Native层及系统问题定位提供了技术基础。",
        ],
    )

    story.append(PageBreak())
    story += section("04", "PROJECTS", "项目经历")
    story += project(
        "App启动性能存量治理",
        "Benchmark / Perfetto / ViewPager2 / WebView",
        [
            "基于线上启动监控定位首屏构建阶段耗时，发现ViewPager2预加载及WebView初始化等任务"
            "在启动关键路径承担过多工作。",
            "选择低端设备进行多轮冷启动Benchmark，通过中位数轮次Perfetto分析View创建、布局与渲染耗时。",
            "恢复ViewPager2懒加载，避免启动时一次创建6个Tab Fragment；移除XML静态WebView，"
            "改为轻量容器占位并在进入Web场景时按需创建。",
            "本地受控Benchmark由2.98s降至1.74s，降低41.6%；线上P50由1.8s降至1.5s，"
            "P90由4.6s降至3.1s。",
        ],
    )
    story += project(
        "ARouter启动增量劣化治理",
        "Android Studio Profiler / Gradle / AGP / ASM / ARouter",
        [
            "Gradle/AGP升级后，ARouter注册插件失效并回退至运行时Dex扫描，"
            "导致灰度低性能设备P90由约4.5s升至12.8s。",
            "通过Android Studio Profiler确认<font name='Avenir-Regular'>openDexFileNative</font>"
            "耗时约7.6s，并定位到编译期路由注册未生效。",
            "接入兼容AGP 8的ARouter Gradle插件，将路由表扫描与注册前移至编译期；"
            "同时升级ASM并修复Java 21字节码及复杂Variant兼容问题。",
            "修复后，本地ARouter初始化由约7.84s降至100ms内，灰度低性能设备P90恢复至约4.5s，"
            "消除候选版本新增的约8.3s劣化。",
        ],
    )
    story += project(
        "线上Top ANR专项治理",
        "Bugly / ANR Trace / 生命周期 / 异步存储",
        [
            "基于Bugly梳理近90天Top ANR，聚焦主线程图片压缩与文件IO阻塞、"
            "播放器释放等待等Top ANR问题。",
            "结合ANR Trace、线程状态和业务调用链定位根因，分别通过生命周期释放、"
            "异步存储及播放器资源管理完成针对性修复。",
            "相关问题累计涉及约4.56万条记录、影响用户比例超过12%；"
            "修复方案已落地并持续跟踪线上效果。",
        ],
    )
    story += project(
        "OpenHarmony录像下载与视频加水印",
        "OpenHarmony / ArkTS / AKI / C / C++ / FFmpeg",
        [
            "为支持录像下载与视频加水印需求，基于FFmpeg fftools封装音视频处理工具库，"
            "打通ArkTS与Native之间的命令调用、处理进度及结果回调。",
            "针对FFmpeg命令结束可能导致宿主进程退出的问题，改造异常退出及结果返回链路，"
            "保障处理任务在应用内稳定运行。",
            "接入<font name='Avenir-Regular'>h264_ohosavcodec</font>硬件编码，"
            "将业务场景中2分钟视频加水印耗时由约150s降至27s，降低约82%。",
            "相关能力已沉淀为<font name='Avenir-Regular'>ffmpeg_tools</font>并发布至GitHub和OHPM，"
            "累计下载600+次。",
        ],
    )
    story += project(
        "其他项目",
        None,
        [
            "<b>Flutter推送插件适配：</b>定位"
            "<font name='Avenir-Regular'>getui_flutter</font> Android插件未解析和透传通知payload的问题，"
            "补充Native至Flutter的数据传递链路，并发布自维护的pub.dev版本。",
            "<b>Android视频水印处理优化：</b>使用MediaCodec、SurfaceTexture与OpenGL ES完成视频解码、"
            "纹理合成、水印渲染及重新编码，并修复相关渲染异常。",
        ],
    )

    story.append(PageBreak())
    story += section("05", "OPEN SOURCE", "开源贡献")
    story += project(
        "ffmpeg_tools｜OpenHarmony音视频工具库",
        None,
        [
            "基于FFmpeg fftools封装ArkTS可调用的Native音视频处理能力，支持音视频转码、录像下载、"
            "视频加水印、处理进度回调及硬件编解码。",
            "打通ArkTS与C/C++双向调用，并处理FFmpeg命令结束可能导致宿主进程退出的问题。",
            "接入<font name='Avenir-Regular'>h264_ohosavcodec</font>硬件编码，"
            "在业务场景中将2分钟视频加水印耗时由约150s降至27s。",
            "已发布至GitHub和OHPM，累计下载600+次。",
        ],
    )
    story.append(
        link_line(
            [
                ("OHPM", "https://ohpm.openharmony.cn/#/cn/detail/@prq%2Fffmpeg-tools"),
                ("GitHub", "https://github.com/jjjjjjava/ffmpeg_tools"),
                ("GitHub Issue #5", "https://github.com/jjjjjjava/ffmpeg_tools/issues/5"),
            ]
        )
    )
    story += project(
        "ArouterGradlePlugin｜外部开源贡献",
        None,
        [
            "定位ASM版本过低导致Java 21字节码无法解析的问题，将ASM升级至9.7并保持旧版本兼容，"
            "修复获维护者合并。",
            "定位插件对Variant名称进行精确匹配，导致复杂Variant场景下配置失效的问题，"
            "补充兼容逻辑并获维护者合并。",
        ],
    )
    story.append(
        link_line(
            [
                ("Java 21兼容修复", "https://github.com/JailedBird/ArouterGradlePlugin/pull/16"),
                ("Variant匹配修复", "https://github.com/JailedBird/ArouterGradlePlugin/pull/19"),
                ("自维护JitPack", "https://jitpack.io/#jjjjjjava/ArouterGradlePlugin"),
            ]
        )
    )
    story += project(
        "OpenHarmony-TPC FFmpeg｜外部开源贡献",
        None,
        [
            "定位<font name='Avenir-Regular'>h264_ohosavcodec</font>编码器未正确透传目标码率参数的问题。",
            "修复OpenHarmony硬件编码器参数传递链路，使指定码率能够正确下发并生效。",
            "向OpenHarmony-TPC FFmpeg移植仓提交修复PR并获合并。",
        ],
    )
    story.append(
        link_line(
            [
                (
                    "合并记录",
                    "https://gitee.com/openharmony-tpc-incubate/FFmpeg/pulls/49",
                )
            ]
        )
    )
    story += project(
        "getui_flutter｜Flutter推送插件",
        None,
        [
            "定位<font name='Avenir-Regular'>getui_flutter</font> Android端未解析通知payload，"
            "导致数据无法透传至Flutter的问题。",
            "补充Android Native至Flutter的数据解析与传递链路，支持业务侧获取通知payload。",
            "基于修复版本发布自维护的pub.dev插件包，为项目提供可直接集成的稳定版本。",
        ],
    )
    story.append(
        link_line([("pub.dev", "https://pub.dev/packages/getui_flutter")])
    )

    story += section("06", "TECHNICAL WRITING", "技术输出")
    story += [
        Paragraph(
            "持续分享Android、JVM及OpenHarmony相关技术内容，累计发布29篇原创文章，"
            "阅读量10,000+。",
            STYLES["body"],
        ),
        link_line(
            [
                ("CSDN", "https://blog.csdn.net/qq_35829566"),
                ("掘金", "https://juejin.cn/user/499639464759898"),
            ]
        ),
    ]

    story += section("07", "EDUCATION", "教育经历")
    education = Table(
        [
            [
                Paragraph("<b>暨南大学</b>", STYLES["job"]),
                Paragraph("软件工程 · 本科", STYLES["body"]),
                Paragraph("2019.09 - 2023.06", STYLES["date"]),
            ]
        ],
        colWidths=[48 * mm, 68 * mm, 48 * mm],
    )
    education.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 0), (-1, -1), SOFT),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(education)
    return story


def main() -> None:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = ResumeDocTemplate(str(output))
    doc.build(build_story())
    print(output)


if __name__ == "__main__":
    main()
