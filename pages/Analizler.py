"""
Analytics page for the AI-Powered Smart Recipe Recommendation System.
Renders Plotly visualizations to analyze user recipe generation stats and patterns.
"""

import streamlit as st
import database as db
import charts
from config import APP_NAME, FAVICON, STYLE_CSS_PATH
from utils import inject_custom_css, get_api_status

# Page Config
st.set_page_config(
    page_title=f"{APP_NAME} - Analizler",
    page_icon=FAVICON,
    layout="wide"
)

# Inject styling
inject_custom_css(STYLE_CSS_PATH)

# Initialize database
db.init_db()

# Sidebar Setup
st.sidebar.markdown(f"<div class='sidebar-section'>👤 Kullanıcı Bilgisi</div>", unsafe_allow_html=True)
username = st.sidebar.text_input("Kullanıcı Adı", value="Şef Adayı", key="user_profile_name_analytics")

st.sidebar.markdown(f"<div class='sidebar-section'>🔌 API Bağlantı Durumu</div>", unsafe_allow_html=True)
api_statuses = get_api_status()
for api_name, status in api_statuses.items():
    status_text = "🟢 Aktif" if status else "🔴 Pasif"
    status_class = "api-ok" if status else "api-err"
    st.sidebar.markdown(f"**{api_name}:** <span class='{status_class}'>{status_text}</span>", unsafe_allow_html=True)

st.sidebar.markdown(f"<div class='sidebar-section'>💾 Veritabanı Durumu</div>", unsafe_allow_html=True)
all_recipes = db.get_all_recipes()
favorites_recipes = db.get_favorites()
st.sidebar.write(f"📁 Toplam Kayıt: **{len(all_recipes)}**")
st.sidebar.write(f"⭐ Favori Tarifler: **{len(favorites_recipes)}**")

# Page Title
st.markdown("<h1 class='gradient-header'>📈 Tarif Analiz Paneli</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>Yemek alışkanlıklarınızı, en çok kullandığınız malzemeleri ve tarif detaylarını grafiklerle inceleyin.</p>", unsafe_allow_html=True)

if not all_recipes:
    st.info("Kayıtlı tarif bulunmadığından analiz gösterilemiyor. Lütfen önce ana sayfadan tarif oluşturun.")
else:
    # 1. Summary Cards (KPIs)
    df_recipes = charts.get_df_from_recipes(all_recipes)
    
    total_count = len(df_recipes)
    fav_count = len(df_recipes[df_recipes["favori"] == "Evet"])
    avg_prep = df_recipes["sure_dakika"].mean()
    avg_cal = df_recipes["kalori"].mean()

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.metric("📁 Toplam Tarif", f"{total_count} Adet")
    with col_kpi2:
        st.metric("⭐ Favori Tarif", f"{fav_count} Adet")
    with col_kpi3:
        st.metric("⏱️ Ort. Hazırlama", f"{avg_prep:.1f} Dakika")
    with col_kpi4:
        st.metric("🔥 Ort. Kalori", f"{avg_cal:.0f} kcal")
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Charts Layout Grid
    st.write("") # Spacer

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        fig_trend = charts.plot_recipe_trend(all_recipes)
        if fig_trend:
            st.plotly_chart(fig_trend, use_container_width=True)
            
    with col_chart2:
        fig_diff = charts.plot_difficulty_distribution(all_recipes)
        if fig_diff:
            st.plotly_chart(fig_diff, use_container_width=True)

    st.write("") # Spacer

    col_chart3, col_chart4 = st.columns(2)
    with col_chart3:
        fig_fav = charts.plot_favorites_ratio(all_recipes)
        if fig_fav:
            st.plotly_chart(fig_fav, use_container_width=True)

    with col_chart4:
        fig_metrics = charts.plot_avg_metrics(all_recipes)
        if fig_metrics:
            st.plotly_chart(fig_metrics, use_container_width=True)

    st.write("") # Spacer

    col_chart5, col_chart6 = st.columns(2)
    with col_chart5:
        fig_ing = charts.plot_top_ingredients(all_recipes)
        if fig_ing:
            st.plotly_chart(fig_ing, use_container_width=True)

    with col_chart6:
        fig_ai = charts.plot_ai_model_distribution(all_recipes)
        if fig_ai:
            st.plotly_chart(fig_ai, use_container_width=True)
