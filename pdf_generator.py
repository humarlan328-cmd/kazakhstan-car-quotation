from __future__ import annotations

from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from config import (
    BROKER_SERVICE_FEE,
    CUSTOMS_COLLECTION,
    SBKTS_EPTS_FEE,
    WHATSAPP_NUMBER,
)
from utils import format_kzt, format_usd

def register_pdf_font() -> str:
    """注册 PDF 字体（支持中文、俄文、英文）"""

    from pathlib import Path
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    font_path = Path("fonts/SourceHanSansSC-Regular.otf")

    if not font_path.exists():
        raise RuntimeError(
            f"字体不存在：{font_path}\n请确认已放入 V5/fonts 文件夹。"
        )

    font_name = "VehicleQuoteFont"

    try:
        pdfmetrics.registerFont(
            TTFont(font_name, str(font_path))
        )
    except Exception as e:
        raise RuntimeError(f"字体加载失败：{e}")

    return font_name
       


def create_quote_pdf(data: dict) -> bytes:
    font_name = register_pdf_font()
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
        title="哈萨克斯坦车辆进口报价单",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleCN",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=17,
        leading=23,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17365D"),
    )

    body_style = ParagraphStyle(
        "BodyCN",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=9.2,
        leading=13,
    )

    section_style = ParagraphStyle(
        "SectionCN",
        parent=styles["Heading2"],
        fontName=font_name,
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#17365D"),
    )

    def p(value: object) -> Paragraph:
        return Paragraph(escape(str(value)), body_style)

    def table(rows: list[list[Paragraph]], widths: list[float]) -> Table:
        t = Table(rows, colWidths=widths)
        t.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BFCBDD")),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        return t

    story = [
        Paragraph(
            "哈萨克斯坦车辆进口报价单"
            "<br/>Коммерческое предложение на импорт автомобиля",
            title_style,
        ),
        Spacer(1, 5 * mm),
        Paragraph(
            f"报价编号 / Номер：{escape(data['quote_number'])}"
            f"<br/>报价日期 / Дата：{escape(data['quote_date'])}"
            f"<br/>有效期至 / Действительно до：{escape(data['valid_until'])}",
            body_style,
        ),
        Spacer(1, 5 * mm),
        Paragraph("客户信息 / Информация о клиенте", section_style),
        table(
            [
                [p("项目 / Параметр"), p("信息 / Информация")],
                [p("客户姓名 / Имя клиента"), p(data["customer_name"])],
                [p("客户电话 / Телефон клиента"), p(data["customer_phone"])],
            ],
            [65 * mm, 105 * mm],
        ),
        Spacer(1, 5 * mm),
        Paragraph("车辆信息 / Информация об автомобиле", section_style),
        table(
            [
                [p("项目 / Параметр"), p("信息 / Информация")],
                [p("品牌 / Марка"), p(data["brand"])],
                [p("车型 / Модель"), p(data["model"])],
                [p("生产年份 / Год выпуска"), p(data["production_year"])],
                [p("排量 / Объем"), p(data["engine"])],
                [p("来源 / Источник"), p(data["source"])],
            ],
            [65 * mm, 105 * mm],
        ),
        Spacer(1, 5 * mm),
        Paragraph("价格及费用 / Стоимость и расходы", section_style),
        table(
            [
                [p("费用项目 / Наименование"), p("金额 / Сумма")],
                [p("原价 / Исходная цена"), p(format_usd(data["original_price_usd"]))],
                [p("增值税 / НДС"), p(format_usd(data["vat_amount_usd"]))],
                [p("含税价格 / Цена с НДС"), p(format_usd(data["price_with_vat_usd"]))],
                [p("海关收费 / Сборы"), p(format_kzt(CUSTOMS_COLLECTION))],
                [p("关税 / Пошлина"), p("待计算 / В разработке")],
                [p("报废税 / Утильсбор"), p("待计算 / В разработке")],
                [p("首次注册 / Первичка"), p("待计算 / В разработке")],
                [p("认证 + 电子车辆护照 / СБКТС + ЭПТС"), p(format_kzt(SBKTS_EPTS_FEE))],
                [p("报关服务费 / Услуги брокера"), p(format_kzt(BROKER_SERVICE_FEE))],
            ],
            [105 * mm, 65 * mm],
        ),
        Spacer(1, 7 * mm),
        Paragraph(
            f"WhatsApp：{escape(WHATSAPP_NUMBER)}"
            "<br/>关税、报废税和首次注册费暂未计入。"
            "<br/>Пошлина, утильсбор и первичная регистрация пока не включены.",
            body_style,
        ),
    ]

    document.build(story)
    return buffer.getvalue()
