import streamlit as st

from database import (
    count_quotations,
    count_this_month,
    count_today,
    fetch_quotations,
    initialize_database,
)

st.set_page_config(
    page_title="数据统计",
    page_icon="📊",
    layout="wide",
)

initialize_database()

st.title("📊 数据统计 / Статистика")

data = fetch_quotations()

metric_1, metric_2, metric_3 = st.columns(3)
metric_1.metric("累计报价", count_quotations())
metric_2.metric("今日报价", count_today())
metric_3.metric("本月报价", count_this_month())

if data.empty:
    st.info("暂时没有数据。")
    st.stop()

st.subheader("热门品牌")
brand_counts = data["brand"].value_counts().head(10)
st.bar_chart(brand_counts)

st.subheader("热门车型")
model_counts = (
    data.assign(vehicle=data["brand"] + " " + data["model"])
    ["vehicle"]
    .value_counts()
    .head(10)
)
st.bar_chart(model_counts)

st.subheader("客户状态")
status_counts = data["status"].value_counts()
st.bar_chart(status_counts)
