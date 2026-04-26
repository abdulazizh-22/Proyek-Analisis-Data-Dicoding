import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Bike-sharing Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)
sns.set_style("whitegrid")

@st.cache_data
def load_data():
    main_data = pd.read_csv("dashboard/main_data.csv")
    main_data["dteday"] = pd.to_datetime(main_data["dteday"])
    
    # Tambahkan tipe hari
    main_data['day_type'] = main_data['weekday'].apply(
        lambda x: 'Weekend' if x == 0 or x == 6 else 'Weekday'
    )
    
    return main_data

main_data = load_data()

#Filter
st.sidebar.title("Filter Eksplorasi")

start_date, end_date = st.sidebar.date_input(
    "Rentang Waktu",
    [main_data['dteday'].min(), main_data['dteday'].max()]
)

season = st.sidebar.multiselect(
    "Pilih Musim",
    options=main_data["season"].unique(),
    default=main_data["season"].unique()
)

hour_range = st.sidebar.slider("Rentang Jam", 0, 23, (0, 23))

filtered_data = main_data[
    (main_data['dteday'] >= pd.to_datetime(start_date)) &
    (main_data['dteday'] <= pd.to_datetime(end_date)) &
    (main_data['season'].isin(season)) &
    (main_data['hr'] >= hour_range[0]) &
    (main_data['hr'] <= hour_range[1])
]

# metric pengukuran data sewa
st.title("Bike-sharing Dashboard")
st.markdown("Analisis Data Sewa Sepeda")

c1, c2 = st.columns(2)
c1.metric("Total Penyewaan", f"{filtered_data['cnt'].sum():,.0f}")
c2.metric("Rata-rata/Jam", f"{filtered_data['cnt'].mean():.2f}")

st.markdown("---")

# Trend Harian
st.subheader("Tren Penyewaan Harian")
trend = filtered_data.groupby("dteday")["cnt"].sum()
fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(trend, color="#72BCD4", linewidth=2)
st.pyplot(fig)

#Heatmap pola sewa harian
st.write("---")
st.subheader("Heatmap Pola Harian Sewa")

weekday_map = {0: "Minggu", 1: "Senin", 2: "Selasa", 3: "Rabu", 4: "Kamis", 5: "Jumat", 6: "Sabtu"}
day_order = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

heatmap_data = filtered_data.copy()
heatmap_data['weekday_name'] = heatmap_data['weekday'].map(weekday_map)
heatmap_data['weekday_name'] = pd.Categorical(
    heatmap_data['weekday_name'], 
    categories=day_order, 
    ordered=True
)

pivot_table = heatmap_data.groupby(
    ['weekday_name', 'hr'], 
    observed=False
)['cnt'].mean().unstack()

fig, ax = plt.subplots(figsize=(15, 6))

sns.heatmap(
    pivot_table,
    cmap="rocket",
    ax=ax
)

ax.set_xlabel("Jam")
ax.set_ylabel("Hari")
ax.set_title("Heatmap Penyewaan Sepeda Berdasarkan Hari dan Jam")

st.pyplot(fig)

# Pilih hari untuk analisa sewa
st.write("---")
st.subheader("Pola Penyewaan Harian")
st.info("Pilih Hari untu Melihat Tren Sewa Perjamnya")

selected_day = st.selectbox(
    "Pilih Hari Spesifik:",
    options=["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
)

day_to_num = {"Minggu": 0, "Senin": 1, "Selasa": 2, "Rabu": 3, "Kamis": 4, "Jumat": 5, "Sabtu": 6}
specific_day_df = filtered_data[filtered_data['weekday'] == day_to_num[selected_day]].copy()
specific_day_df = specific_day_df.rename(columns={"hr": "Jam"})

col_l, col_r = st.columns(2)

with col_l:
    st.markdown(f"**Rata-rata Penyewaan per Jam ({selected_day})**")
    if not specific_day_df.empty:
        hourly_plot = specific_day_df.groupby("Jam")["cnt"].mean()
        fig, ax = plt.subplots()
        sns.lineplot(x=hourly_plot.index, y=hourly_plot.values, marker="o", color="#1f77b4")
        ax.set_xlabel("Jam")
        ax.set_ylabel("Rata-rata Penyewaan")
        st.pyplot(fig)

# Analisis perhari dan Musim
st.write("---")
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Analisis Berdasarkan Hari")

    day_stats = filtered_data.groupby("weekday")["cnt"].mean().reset_index()
    day_stats["weekday"] = day_stats["weekday"].map(weekday_map)
    day_stats = day_stats.sort_values("cnt", ascending=True)

    colors = ["#FDF06A"] * len(day_stats)
    colors[-1] = "#FB5D5D"  # highlight tertinggi (kuning)

    fig, ax = plt.subplots(figsize=(6,4))
    ax.barh(day_stats["weekday"], day_stats["cnt"], color=colors)

    ax.set_xlabel("Rata-rata Penyewaan")
    ax.set_ylabel("Hari")
    ax.set_title("Rata-rata Penyewaan Sepeda per Hari")

    st.pyplot(fig)

with col_b:
    st.subheader("Analisis Berdasarkan Musim")

    season_stats = filtered_data.groupby("season")["cnt"].mean().reset_index()
    season_stats = season_stats.sort_values("cnt", ascending=True)

    colors = ["#FDF06A"] * len(season_stats)
    colors[-1] = "#FB5D5D"  # highlight tertinggi (kuning)

    fig, ax = plt.subplots(figsize=(6,4))
    ax.barh(season_stats["season"].astype(str), season_stats["cnt"], color=colors)

    ax.set_xlabel("Rata-rata Penyewaan")
    ax.set_ylabel("Musim")
    ax.set_title("Pengaruh Musim terhadap Penyewaan")

    st.pyplot(fig)