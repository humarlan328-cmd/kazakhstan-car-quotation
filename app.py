from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from config import (
    BROKER_SERVICE_FEE,
    CUSTOMS_COLLECTION,
    EXCEL_PATH,
    QUOTE_VALID_DAYS,
    SBKTS_EPTS_FEE,
    WHATSAPP_NUMBER,
)
from database import initialize_database, save_quotation
from pdf_generator import create_quote_pdf
from utils import (
    calculate_price,
    clean_display_value,
    format_kzt,
    format_usd,
    get_brand_display_name,
    load_excel,
    make_safe_filename,
    normalize_text,
    normalize_year,
    parse_price,
    resolve_columns,
)


st.set_page_config(
    page_title="哈萨克斯坦车辆进口报价系统 V5",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background-color: #f4f7fb; }
    .block-container { max-width: 1180px; padding-top: 1.5rem; }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #d9e3ef;
        padding: 16px;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

initialize_database()

if not EXCEL_PATH.exists():
    st.error("找不到 Cars price.xlsx，请把它放在 app.py 同一个文件夹。")
    st.stop()

try:
    df = load_excel(EXCEL_PATH)
    columns = resolve_columns(df)
except Exception as error:
    st.error("Excel 读取或表头匹配失败。")
    st.exception(error)
    st.stop()

brand_column = columns["brand"]
model_column = columns["model"]
engine_column = columns["engine"]
year_column = columns["year"]
price_column = columns["price"]
source_column = columns["source"]

df = df.dropna(subset=[brand_column, model_column]).copy()
df[brand_column] = df[brand_column].astype(str).str.strip()
df[model_column] = df[model_column].astype(str).str.strip()
df["_brand_normalized"] = df[brand_column].apply(normalize_text)
df["_model_normalized"] = df[model_column].apply(normalize_text)
df["_year_normalized"] = df[year_column].apply(normalize_year)

st.title("🚗 哈萨克斯坦车辆进口报价系统")
st.subheader("Расчёт стоимости импорта автомобиля в Казахстан")
st.caption("V5 正式版：报价、PDF、客户数据库和后台管理。")

st.markdown("### 客户资料 / Данные клиента")

customer_col_1, customer_col_2 = st.columns(2)
with customer_col_1:
   customer_name = st.text_input(
   "客户姓名 * / Имя клиента *",
        placeholder="请输入客户姓名",
    )
with customer_col_2:
    customer_phone = st.text_input(
    "客户电话 * / Телефон клиента *",
        placeholder="+7 700 000 0000",
    )
if not customer_name.strip():
    st.info("请输入客户姓名 / Введите имя клиента")

if not customer_phone.strip():
    st.info("请输入客户电话 / Введите номер телефона")
st.markdown("### 车辆查询 / Поиск автомобиля")

brands = sorted(
    df[brand_column].dropna().astype(str).str.strip().unique().tolist(),
    key=lambda value: value.upper(),
)

column_1, column_2, column_3 = st.columns(3)

with column_1:
    brand = st.selectbox(
        "车辆品牌 / Марка",
        options=brands,
        index=None,
        placeholder="请选择品牌",
        format_func=get_brand_display_name,
    )

if brand:
    brand_rows = df[
        df["_brand_normalized"].eq(normalize_text(brand))
    ].copy()
    models = sorted(
        brand_rows[model_column]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist(),
        key=normalize_text,
    )
else:
    brand_rows = df.iloc[0:0].copy()
    models = []

with column_2:
    model = st.selectbox(
        "车辆车型 / Модель",
        options=models,
        index=None,
        placeholder="请选择车型" if brand else "请先选择品牌",
        disabled=not brand,
    )

if brand and model:
    model_rows = brand_rows[
        brand_rows["_model_normalized"].eq(normalize_text(model))
    ].copy()
    years = [
        value
        for value in (
            model_rows["_year_normalized"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
        if value.strip()
    ]
    years = sorted(
        years,
        key=lambda value: float(value) if value.replace(".", "", 1).isdigit() else 0,
        reverse=True,
    )
else:
    years = []

with column_3:
    year = st.selectbox(
        "生产年份 / Год выпуска",
        options=years,
        index=None,
        placeholder="请选择年份" if model else "请先选择车型",
        disabled=not model,
    )
def is_valid_phone(phone: str) -> bool:
    """手机号码至少包含 10 位数字。"""
    digits = "".join(
        character
        for character in phone
        if character.isdigit()
    )
    return len(digits) >= 10


name_is_valid = bool(customer_name.strip())
phone_is_valid = is_valid_phone(customer_phone)

if customer_phone and not phone_is_valid:
    st.warning(
        "请输入正确的手机号码，至少包含 10 位数字。"
        " / Введите корректный номер телефона."
    )
search_button = st.button(
    "查询并生成报价 / Найти и подготовить предложение",
    type="primary",
    width="stretch",
    disabled=(
        not name_is_valid
        or not phone_is_valid
        or not brand
        or not model
        or not year
    ),
)

if search_button:
    if not customer_name.strip():
        st.error("❌ 请输入客户姓名")
        st.stop()

    if not customer_phone.strip():
        st.error("❌ 请输入客户手机号")
        st.stop()

    result = df[
        df["_brand_normalized"].eq(normalize_text(brand))
        & df["_model_normalized"].eq(normalize_text(model))
        & df["_year_normalized"].eq(normalize_year(year))
    ].copy()

    if result.empty:
        st.error("没有找到符合条件的车辆。")
        st.stop()

    result["_price_number"] = result[price_column].apply(parse_price)
    result = result.sort_values(
        by="_price_number",
        ascending=True,
        na_position="last",
    )

    st.success(f"找到 {len(result)} 条记录")

    for number, (row_index, row) in enumerate(result.iterrows(), start=1):
        original_price = parse_price(row[price_column])
        if original_price is None:
            continue

        vat_amount, price_with_vat = calculate_price(original_price)

        now = datetime.now()
        quote_number = now.strftime(f"KZ-%Y%m%d-%H%M%S-%f-{number}")
        quote_date = now.strftime("%Y-%m-%d %H:%M")
        valid_until = (
            now + timedelta(days=QUOTE_VALID_DAYS)
        ).strftime("%Y-%m-%d")

        quotation_data = {
            "quote_number": quote_number,
            "quote_date": quote_date,
            "valid_until": valid_until,
            "customer_name": customer_name.strip(),
            "customer_phone": customer_phone.strip(),
            "brand": clean_display_value(row[brand_column]),
            "model": clean_display_value(row[model_column]),
            "production_year": normalize_year(row[year_column]),
            "engine": clean_display_value(row[engine_column]),
            "source": clean_display_value(row[source_column]),
            "original_price_usd": original_price,
            "vat_amount_usd": vat_amount,
            "price_with_vat_usd": price_with_vat,
        }

        saved = save_quotation(quotation_data)

        with st.container(border=True):
            st.markdown(
                f"## {number}. "
                f"{quotation_data['brand']} {quotation_data['model']}"
            )

            info_1, info_2, info_3 = st.columns(3)
            info_1.metric("排量 / Объем", quotation_data["engine"])
            info_2.metric("年份 / Год", quotation_data["production_year"])
            info_3.metric("来源 / Источник", quotation_data["source"])

            price_1, price_2, price_3 = st.columns(3)
            price_1.metric("原价 / Исходная цена", format_usd(original_price))
            price_2.metric("增值税 / НДС", format_usd(vat_amount))
            price_3.metric("含税价格 / Цена с НДС", format_usd(price_with_vat))

            fee_table = pd.DataFrame(
                {
                    "费用项目 / Наименование": [
                        "海关收费 / Сборы",
                        "关税 / Пошлина",
                        "增值税 / НДС",
                        "海关部分合计 / Итого по ДТ",
                        "报废税 / Утильсбор",
                        "首次注册 / Первичка",
                        "认证 + 电子车辆护照 / СБКТС + ЭПТС",
                        "报关服务费 / Услуги брокера",
                    ],
                    "金额 / Сумма": [
                        format_kzt(CUSTOMS_COLLECTION),
                        "待计算 / В разработке",
                        format_usd(vat_amount),
                        format_usd(price_with_vat),
                        "待计算 / В разработке",
                        "待计算 / В разработке",
                        format_kzt(SBKTS_EPTS_FEE),
                        format_kzt(BROKER_SERVICE_FEE),
                    ],
                }
            )
            st.dataframe(fee_table, width="stretch", hide_index=True)

            if saved:
                st.success("客户报价已保存到数据库。")

            try:
                pdf_data = create_quote_pdf(quotation_data)
                file_name = (
                    f"quotation_{quote_number}_"
                    f"{make_safe_filename(quotation_data['brand'])}_"
                    f"{make_safe_filename(quotation_data['model'])}.pdf"
                )
                st.download_button(
                    "📄 下载 PDF 报价单 / Скачать PDF",
                    data=pdf_data,
                    file_name=file_name,
                    mime="application/pdf",
                    width="stretch",
                    on_click="ignore",
                    key=f"pdf_{row_index}_{number}",
                )
            except Exception as error:
                st.error("PDF 生成失败。")
                st.exception(error)

st.caption(f"WhatsApp：{WHATSAPP_NUMBER}")
