"""
Favorites page for the AI-Powered Smart Recipe Recommendation System.
Enables listing, exploring, and managing favorited recipes.
"""

import streamlit as st
from config import APP_NAME, FAVICON, STYLE_CSS_PATH
from utils import inject_custom_css, get_api_status, format_duration
import database as db
import export

# Page Config
st.set_page_config(
    page_title=f"{APP_NAME} - Favoriler",
    page_icon=FAVICON,
    layout="wide"
)

# Inject styling
inject_custom_css(STYLE_CSS_PATH)

# Initialize database
db.init_db()

# Sidebar Setup
st.sidebar.markdown(f"<div class='sidebar-section'>👤 Kullanıcı Bilgisi</div>", unsafe_allow_html=True)
username = st.sidebar.text_input("Kullanıcı Adı", value="Şef Adayı", key="user_profile_name_favorites")

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
st.markdown("<h1 class='gradient-header'>⭐ Favori Tariflerim</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>En çok beğendiğiniz, sıkça yaptığınız özel yapay zekâ tarifleriniz.</p>", unsafe_allow_html=True)

if not favorites_recipes:
    st.info("Henüz favorilere eklenmiş bir tarif bulunmuyor. Ana sayfadan yeni tarif oluşturup favorilere ekleyebilirsiniz!")
else:
    # Display favorites in expanders
    for item in favorites_recipes:
        recipe_id = item["id"]
        recipe_data = item["olusturulan_tarif"]
        tarih_datetime = item["tarih"]
        ai_engine = item["ai_modeli"]

        title_text = f"⭐ {recipe_data['yemek']} ({tarih_datetime})"
        badge_theme = "custom-badge-primary" if ai_engine.lower() == "gemini" else "custom-badge-warning"

        with st.expander(title_text):
            col_badges = st.columns([1, 1, 1, 1])
            with col_badges[0]:
                st.markdown(f"<span class='custom-badge {badge_theme}'>🤖 Model: {ai_engine}</span>", unsafe_allow_html=True)
            with col_badges[1]:
                st.markdown(f"<span class='custom-badge'>⏱️ {format_duration(recipe_data['sure_dakika'])}</span>", unsafe_allow_html=True)
            with col_badges[2]:
                st.markdown(f"<span class='custom-badge'>🔥 {recipe_data['kalori']} kcal</span>", unsafe_allow_html=True)
            with col_badges[3]:
                st.markdown(f"<span class='custom-badge'>📊 Zorluk: {recipe_data['zorluk']}</span>", unsafe_allow_html=True)

            st.write(f"**Açıklama:** {recipe_data['aciklama']}")
            st.write(f"**Malzemeler:** {item['malzemeler']}")

            tab1, tab2, tab3, tab4 = st.tabs(["📋 Malzemeler", "👨‍🍳 Yapılışı", "🍽️ Sunum", "🥗 Alternatif Tarifler"])

            with tab1:
                st.subheader("Gerekli Malzemeler")
                for m in recipe_data["malzemeler"]:
                    st.checkbox(m, value=True, key=f"fav_m_{recipe_id}_{m}")
                if recipe_data.get("eksik_malzemeler"):
                    st.markdown("---")
                    st.markdown("### ⚠️ Eksik Malzemeler")
                    for eksik in recipe_data["eksik_malzemeler"]:
                        st.markdown(f"<span style='color:#E74C3C;'>• {eksik}</span>", unsafe_allow_html=True)

            with tab2:
                st.subheader("Hazırlanışı")
                for idx, adim in enumerate(recipe_data["yapilis"], 1):
                    st.markdown(
                        f"<div class='step-container'><strong>Adım {idx}:</strong> {adim}</div>",
                        unsafe_allow_html=True
                    )

            with tab3:
                st.subheader("Aşçının Sunum Önerisi")
                st.markdown(
                    f"<div class='presentation-box'>{recipe_data['sunum_onerisi']}</div>",
                    unsafe_allow_html=True
                )

            with tab4:
                st.subheader("Yapabileceğiniz Alternatif Tarifler")
                for alt in recipe_data["alternatif_tarifler"]:
                    st.markdown(f"<span class='custom-badge custom-badge-primary'>{alt}</span>", unsafe_allow_html=True)

            # Footer Controls for this recipe card
            st.markdown("---")
            col_actions = st.columns([1.5, 1, 1, 1])

            # 1. Favorite Toggle
            with col_actions[0]:
                if st.button("❌ Favorilerden Çıkar", key=f"fav_btn_rm_{recipe_id}"):
                    db.toggle_favorite(recipe_id)
                    st.warning("Favorilerden çıkarıldı!")
                    st.rerun()

            # 2. PDF Download
            with col_actions[1]:
                try:
                    pdf_path = export.generate_recipe_pdf(recipe_data)
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📄 PDF İndir",
                            data=f,
                            file_name=f"tarif_{recipe_id}.pdf",
                            mime="application/pdf",
                            key=f"pdf_btn_fav_{recipe_id}"
                        )
                except Exception as e:
                    st.error("PDF oluşturulamadı.")

            # 3. Word Download
            with col_actions[2]:
                try:
                    docx_path = export.generate_recipe_docx(recipe_data)
                    with open(docx_path, "rb") as f:
                        st.download_button(
                            label="📝 Word İndir",
                            data=f,
                            file_name=f"tarif_{recipe_id}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"docx_btn_fav_{recipe_id}"
                        )
                except Exception as e:
                    st.error("Word oluşturulamadı.")

            # 4. CSV Download
            with col_actions[3]:
                csv_data = export.get_single_recipe_csv_data(item)
                st.download_button(
                    label="📊 CSV İndir",
                    data=csv_data,
                    file_name=f"tarif_{recipe_id}.csv",
                    mime="text/csv",
                    key=f"csv_btn_fav_{recipe_id}"
                )
