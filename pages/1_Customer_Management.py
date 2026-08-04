from io import BytesIO

import pandas as pd
import streamlit as st

from database import (
    count_quotations,
    count_this_month,
    count_today,
    delete_quotation,
    fetch_quotations,
    initialize_database,
    update_quotation_status,
)

st.set_page_config(
    page_title="客户管理",
    page_icon="👥",
    layout="wide",
)

initialize_database()

st.title("👥 客户管理 / Управление клиентами")

metric_1, metric_2, metric_3 = st.columns(3)
metric_1.metric("累计报价", count_quotations())
metric_2.metric("今日报价", count_today())
metric_3.metric("本月报价", count_this_month())

search_text = st.text_input(
    "搜索 / Поиск",
    placeholder="客户姓名、电话、品牌、车型或报价编号",
)

data = fetch_quotations(search_text)

if data.empty:
    st.info("没有找到客户记录。")
    st.stop()

display_data = data.rename(
    columns={
        "id": "ID",
        "quote_number": "报价编号",
        "quote_date": "报价日期",
        "valid_until": "有效期",
        "customer_name": "客户姓名",
        "customer_phone": "客户电话",
        "brand": "品牌",
        "model": "车型",
        "production_year": "年份",
        "engine": "排量",
        "source": "来源",
        "original_price_usd": "原价（美元）",
        "vat_amount_usd": "增值税（美元）",
        "price_with_vat_usd": "含税价格（美元）",
        "status": "状态",
        "notes": "备注",
        "created_at": "保存时间",
    }
)

st.dataframe(display_data, width="stretch", hide_index=True)

buffer = BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    display_data.to_excel(writer, index=False, sheet_name="客户报价")

st.download_button(
    "导出 Excel / Экспорт Excel",
    data=buffer.getvalue(),
    file_name="客户报价记录.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.markdown("---")
st.subheader("修改客户状态和备注")

record_options = {
    f"{row['id']} | {row['customer_name']} | {row['brand']} {row['model']}": int(row["id"])
    for _, row in data.iterrows()
}

selected_label = st.selectbox(
    "选择记录",
    options=list(record_options.keys()),
)

selected_id = record_options[selected_label]
selected_row = data[data["id"] == selected_id].iloc[0]

status = st.selectbox(
    "状态",
    options=["已报价", "跟进中", "已成交", "未成交"],
    index=["已报价", "跟进中", "已成交", "未成交"].index(
        selected_row["status"]
        if selected_row["status"] in ["已报价", "跟进中", "已成交", "未成交"]
        else "已报价"
    ),
)

notes = st.text_area(
    "备注",
    value=str(selected_row["notes"] or ""),
)

button_1, button_2 = st.columns(2)

with button_1:
    if st.button("保存修改", type="primary", width="stretch"):
        update_quotation_status(selected_id, status, notes)
        st.success("修改已保存。")
        st.rerun()

with button_2:
    confirm_delete = st.checkbox("确认删除这条记录")
    if st.button(
        "删除记录",
        width="stretch",
        disabled=not confirm_delete,
    ):
        delete_quotation(selected_id)
        st.success("记录已删除。")
        st.rerun()
