from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st

from config import BRAND_CHINESE_NAMES, FIRST_RATE, SECOND_RATE


def normalize_text(value: object) -> str:
    return (
        str(value)
        .upper()
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
        .strip()
    )


def normalize_year(value: object) -> str:
    if pd.isna(value):
        return ""

    try:
        number = float(value)
        if number.is_integer():
            return str(int(number))
        return str(number)
    except (ValueError, TypeError):
        return str(value).strip()


def parse_price(value: object) -> float | None:
    try:
        cleaned = (
            str(value)
            .replace("$", "")
            .replace(",", "")
            .replace(" ", "")
            .strip()
        )
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def format_usd(value: float) -> str:
    return f"${value:,.2f}"


def format_kzt(value: float) -> str:
    return f"{value:,.0f} ₸"


def clean_display_value(value: object) -> str:
    if pd.isna(value):
        return "—"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def calculate_price(original_price: float) -> tuple[float, float]:
    price_with_vat = original_price * (1 + FIRST_RATE) * (1 + SECOND_RATE)
    vat_amount = price_with_vat - original_price
    return vat_amount, price_with_vat


def get_brand_display_name(brand: str) -> str:
    original_brand = str(brand).strip()
    chinese_name = BRAND_CHINESE_NAMES.get(original_brand.upper())
    return f"{chinese_name} / {original_brand}" if chinese_name else original_brand


def make_safe_filename(value: object) -> str:
    text = normalize_text(value)
    result = "".join(ch for ch in text if ch.isalnum())
    return result or "VEHICLE"


@st.cache_data
def load_excel(file_path: Path) -> pd.DataFrame:
    data = pd.read_excel(file_path)
    data.columns = data.columns.astype(str).str.strip()
    return data


def resolve_columns(df: pd.DataFrame) -> dict[str, str]:
    aliases = {
        "brand": ["Марка", "品牌"],
        "model": ["Модель", "车型"],
        "engine": ["Объем", "Объём", "排量"],
        "year": ["Год выпуска", "год выпуска", "年限", "年份"],
        "price": [
            "Цена в долларах США",
            "Цена в долларах x США",
            "美金价格",
            "美元价格",
        ],
        "source": ["Источник", "Источники", "来源"],
    }

    result: dict[str, str] = {}
    for key, names in aliases.items():
        found = next((name for name in names if name in df.columns), None)
        if found is None:
            raise KeyError(f"缺少必要字段：{key}")
        result[key] = found

    return result
