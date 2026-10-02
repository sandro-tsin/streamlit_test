from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Аналитика продаж", page_icon="📊", layout="wide")
st.title("📊 Аналитика продаж")
st.caption("Синтетические продажи за 2025 год · снимок данных из Iceberg в Parquet")

@st.cache_data
def load_data():
    df = pd.read_parquet(Path(__file__).parent / "data/sales.parquet")
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df

try:
    data = load_data()
except Exception as error:
    st.error(f"Не удалось прочитать данные: {error}")
    st.stop()

with st.sidebar:
    st.header("Фильтры")
    city = st.selectbox("Город", ["Все", *sorted(data.city.unique())])
    channel = st.selectbox("Канал", ["Все", *sorted(data.channel.unique())])
    start, end = data.order_date.min().date(), data.order_date.max().date()
    dates = st.date_input("Период", value=(start, end), min_value=start, max_value=end)
    st.caption(f"Всего в файле: {len(data):,} заказов")
if len(dates) != 2:
    st.info("Выберите начало и конец периода.")
    st.stop()

filtered = data.loc[data.order_date.between(pd.Timestamp(dates[0]), pd.Timestamp(dates[1]))]
for column, value in [("city", city), ("channel", channel)]:
    if value != "Все":
        filtered = filtered.loc[filtered[column] == value]
a, b, c = st.columns(3)
a.metric("Выручка", f"{filtered.revenue.sum():,.0f} ₽")
b.metric("Заказы", f"{len(filtered):,}")
c.metric("Средний чек", f"{filtered.revenue.mean() if len(filtered) else 0:,.0f} ₽")
if filtered.empty:
    st.info("За выбранный период заказов нет.")
    st.stop()

daily = filtered.groupby("order_date", as_index=False).revenue.sum()
st.plotly_chart(px.line(daily, x="order_date", y="revenue", title="Выручка по дням", labels={"order_date": "Дата", "revenue": "Выручка, ₽"}), use_container_width=True)
left, right = st.columns(2)
for container, column, title in [(left, "category", "По категориям"), (right, "city", "По городам")]:
    grouped = filtered.groupby(column, as_index=False).revenue.sum().sort_values("revenue", ascending=False)
    container.plotly_chart(px.bar(grouped, x=column, y="revenue", title=title, labels={column: "", "revenue": "Выручка, ₽"}), use_container_width=True)
st.subheader("Последние заказы")
st.dataframe(filtered.sort_values(["order_date", "order_id"], ascending=False).head(100), use_container_width=True, hide_index=True)
st.download_button("Скачать выбранные заказы (CSV)", filtered.to_csv(index=False).encode("utf-8-sig"), file_name="sales.csv", mime="text/csv")
