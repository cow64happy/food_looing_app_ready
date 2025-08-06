
import streamlit as st
import os
from PIL import Image
import uuid
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

if "food_counts" not in st.session_state:
    st.session_state.food_counts = {}
if "log" not in st.session_state:
    st.session_state.log = []

st.set_page_config(page_title="🍽️ 음식 기록 & 분석", layout="centered")
st.title("📸 음식 사진 기록 & 소비 분석 앱")

label = st.text_input("🍴 음식 이름을 입력하세요 (예: 김치, 사과, 라면 등)")
img = st.camera_input("📷 음식 사진을 찍어주세요")
uploaded_file = st.file_uploader("📁 또는 사진 파일을 업로드하세요", type=["jpg", "png", "jpeg"])
if uploaded_file is not None:
    img = uploaded_file

if img and label:
    save_dir = os.path.join("dataset", label)
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{uuid.uuid4()}.jpg"
    save_path = os.path.join(save_dir, filename)
    image = Image.open(img).convert("RGB")
    image.save(save_path)

    st.session_state.food_counts[label] = st.session_state.food_counts.get(label, 0) + 1
    now = datetime.now().strftime("%Y-%m-%d")
    weekday = datetime.now().strftime("%A")
    st.session_state.log.append({"날짜": now, "요일": weekday, "음식": label, "파일명": filename})

    st.success(f"✅ '{label}' 사진 저장 완료! 총 {st.session_state.food_counts[label]}개 기록됨")

    df = pd.DataFrame(st.session_state.log)
    df.to_csv("food_log.csv", index=False, encoding="utf-8-sig")

if st.session_state.food_counts:
    st.markdown("---")
    st.subheader("📅 날짜 필터로 보기")

    df = pd.DataFrame(st.session_state.log)
    df["날짜"] = pd.to_datetime(df["날짜"])
    min_date = df["날짜"].min()
    max_date = df["날짜"].max()
    date_range = st.date_input("날짜 범위 선택", [min_date, max_date])

    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df["날짜"] >= pd.to_datetime(start_date)) & (df["날짜"] <= pd.to_datetime(end_date))]

    st.markdown("---")
    st.subheader("📊 상위 음식 Top 5")

    top_foods = df["음식"].value_counts().head(5)
    st.bar_chart(top_foods)

    st.markdown("---")
    st.subheader("📈 월별 음식 소비 추이")
    df["월"] = df["날짜"].dt.to_period("M").astype(str)
    monthly = df.groupby(["월", "음식"]).size().unstack(fill_value=0)
    st.line_chart(monthly)

    st.markdown("---")
    st.subheader("📅 날짜별 음식 소비 기록")
    grouped = df.groupby(["날짜", "음식"]).size().unstack(fill_value=0)
    st.bar_chart(grouped)

    st.markdown("---")
    st.subheader("📆 요일별 소비 패턴")
    weekday_grouped = df.groupby(["요일", "음식"]).size().unstack(fill_value=0)
    st.bar_chart(weekday_grouped)

    st.markdown("📁 저장된 CSV 파일: `food_log.csv`")

st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)
