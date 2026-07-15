"""
Main Entry point for the AI-Powered Smart Recipe Recommendation System.
Coordinates the UI layout, input gathering, AI generation, and tab views.
"""

import streamlit as st
import os
from pathlib import Path
import database as db
from config import (
    APP_NAME, APP_TITLE, APP_SUBTITLE, FAVICON, 
    STYLE_CSS_PATH, LOGO_PATH
)
from utils import inject_custom_css, get_api_status, format_duration
from gemini_api import generate_recipe_gemini
from groq_api import generate_recipe_groq
import export
import time

# Page config
st.set_page_config(
    page_title=APP_NAME,
    page_icon=FAVICON,
    layout="wide"
)

# Initialize database
db.init_db()

# Inject styling
inject_custom_css(STYLE_CSS_PATH)

# Session State Initialization
if "generated_recipe" not in st.session_state:
    st.session_state.generated_recipe = None
if "recipe_db_id" not in st.session_state:
    st.session_state.recipe_db_id = None
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Gemini"

# Check API Keys
api_statuses = get_api_status()

# --- SIDEBAR PANELS ---
st.sidebar.markdown("<div class='sidebar-section'>👤 Kullanıcı Bilgisi</div>", unsafe_allow_html=True)
username = st.sidebar.text_input("Kullanıcı Adı", value="Şef Adayı", key="user_profile_name_app")

st.sidebar.markdown("<div class='sidebar-section'>🤖 Yapay Zekâ Modeli</div>", unsafe_allow_html=True)
if api_statuses["Groq"]:
    st.session_state.selected_model = st.sidebar.selectbox(
        "Kullanılacak Model",
        options=["Gemini", "Groq"],
        index=0 if st.session_state.selected_model == "Gemini" else 1
    )
else:
    st.session_state.selected_model = "Gemini"
    st.sidebar.info("Groq API Anahtarı bulunamadı, varsayılan olarak Gemini kullanılacaktır.")

st.sidebar.markdown("<div class='sidebar-section'>🔌 API Bağlantı Durumu</div>", unsafe_allow_html=True)
for api_name, status in api_statuses.items():
    status_text = "🟢 Aktif" if status else "🔴 Pasif"
    status_class = "api-ok" if status else "api-err"
    st.sidebar.markdown(f"**{api_name}:** <span class='{status_class}'>{status_text}</span>", unsafe_allow_html=True)

# Fetch DB Stats for Sidebar
all_recipes = db.get_all_recipes()
favorites_recipes = db.get_favorites()

st.sidebar.markdown("<div class='sidebar-section'>💾 Veritabanı Durumu</div>", unsafe_allow_html=True)
st.sidebar.write(f"📁 Toplam Tarif: **{len(all_recipes)}**")
st.sidebar.write(f"⭐ Favori Tarif: **{len(favorites_recipes)}**")


# --- MAIN INTERFACE ---

# Render Logo if it exists
if LOGO_PATH.exists():
    # Show logo centered
    col_logo_l, col_logo_c, col_logo_r = st.columns([1, 1, 1])
    with col_logo_c:
        st.image(str(LOGO_PATH), width=200)

st.markdown(f"<h1 class='gradient-header'>{APP_TITLE}</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='subtitle-text'>{APP_SUBTITLE}</p>", unsafe_allow_html=True)

# Central Glassmorphism Input Card
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.subheader("🥦 Malzemelerinizi Girin")
ingredients_input = st.text_area(
    "Evdeki malzemeleri virgülle ayırarak yazın:",
    placeholder="Yumurta, domates, kaşar peyniri, tereyağı, zeytinyağı...",
    key="ingredients_text_area",
    height=120
)

# Custom recipe options for appetizing suggestions
col_pref1, col_pref2 = st.columns(2)
with col_pref1:
    recipe_mode = st.selectbox(
        "🍳 Tarif Modu / Tercihi",
        options=[
            "Normal (Dengeli)",
            "Pratik & Hızlı (Maks. 25 Dk)",
            "Düşük Kalorili & Sağlıklı",
            "Gurme & Şef Özel",
            "Vejetaryen / Vegan"
        ],
        index=0,
        key="recipe_mode_selector"
    )
with col_pref2:
    custom_request = st.text_input(
        "✍️ Özel İstek veya Not (İsteğe Bağlı)",
        placeholder="Örn: Hızlı ve basit olsun, misafirim var...",
        key="custom_request_input"
    )

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    create_recipe_clicked = st.button("🧑🍳 Tarif Oluştur", use_container_width=True)
with col_btn2:
    create_diff_recipe_clicked = st.button("🔄 Farklı Tarif Oluştur", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Processing generation logic
ingredients_list = [i.strip() for i in ingredients_input.split(",") if i.strip()]

def trigger_recipe_generation(diff_variant: bool = False, mode: str = "Normal (Dengeli)", request_note: str = ""):
    """
    Triggers generation via Gemini or Groq, updates UI, and stores recipe.
    """
    if not ingredients_list:
        st.error("Lütfen tarif oluşturabilmek için en az bir malzeme girin!")
        return

    progress_text = "Yapay zekâ şefiniz isteklerinizi inceliyor..."
    progress_bar = st.progress(0, text=progress_text)
    
    # Progress simulation
    for percent_complete in range(1, 40):
        time.sleep(0.01)
        progress_bar.progress(percent_complete, text=progress_text)

    # Prepare ingredients list, append different token if user requested a variant
    generation_ingredients = ingredients_list.copy()
    if diff_variant:
        generation_ingredients.append("farklı alternatif lezzetler olsun")

    recipe_result = None
    try:
        with st.spinner("Şefiniz mutfağa girdi, tarif hazırlanıyor..."):
            if st.session_state.selected_model == "Gemini":
                recipe_result = generate_recipe_gemini(
                    generation_ingredients, 
                    tarif_modu=mode, 
                    ozel_istek=request_note
                )
            elif st.session_state.selected_model == "Groq":
                recipe_result = generate_recipe_groq(
                    generation_ingredients, 
                    tarif_modu=mode, 
                    ozel_istek=request_note
                )
    except Exception as e:
        st.error(f"Bağlantı sırasında bir hata oluştu: {str(e)}")
        return

    for percent_complete in range(40, 101):
        time.sleep(0.005)
        progress_bar.progress(percent_complete, text="Tarif tabağa yerleştiriliyor...")

    # Clear progress bar
    progress_bar.empty()

    if recipe_result:
        st.toast("Tarifiniz başarıyla oluşturuldu!", icon="🎉")
        
        # Save to database
        db_id = db.save_recipe(
            kullanici=username,
            malzemeler=ingredients_list,
            olusturulan_tarif=recipe_result,
            favori=False,
            ai_modeli=st.session_state.selected_model
        )
        
        # Store in session state
        st.session_state.generated_recipe = recipe_result
        st.session_state.recipe_db_id = db_id
        
        st.success("Yeni tarif başarıyla veritabanına kaydedildi!")
    else:
        st.error("Tarif oluşturulurken bir hata oluştu. Lütfen API anahtarlarınızı kontrol edin veya tekrar deneyin.")


if create_recipe_clicked:
    trigger_recipe_generation(diff_variant=False, mode=recipe_mode, request_note=custom_request)
elif create_diff_recipe_clicked:
    trigger_recipe_generation(diff_variant=True, mode=recipe_mode, request_note=custom_request)


# --- DISPLAY GENERATED RECIPE ---
if st.session_state.generated_recipe:
    recipe = st.session_state.generated_recipe
    recipe_db_id = st.session_state.recipe_db_id

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:#FF5722; text-align:center;'>🍽️ {recipe['yemek']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; font-style:italic;'>{recipe['aciklama']}</p>", unsafe_allow_html=True)

    # Summary statistics cards
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.markdown(
            f"<div class='info-card'>⏱️ <strong>Hazırlama Süresi</strong><br/>{format_duration(recipe['sure_dakika'])}</div>",
            unsafe_allow_html=True
        )
    with col_stat2:
        st.markdown(
            f"<div class='info-card' style='border-left-color:#4CAF50;'>🔥 <strong>Yaklaşık Kalori</strong><br/>{recipe['kalori']} kcal</div>",
            unsafe_allow_html=True
        )
    with col_stat3:
        st.markdown(
            f"<div class='info-card' style='border-left-color:#9C27B0;'>📊 <strong>Zorluk Seviyesi</strong><br/>{recipe['zorluk']}</div>",
            unsafe_allow_html=True
        )

    st.write("") # Spacer

    # Interactive Detail Tabs
    tab_ingredients, tab_steps, tab_presentation, tab_alternatives = st.tabs([
        "📋 Malzemeler", "👨🍳 Yapılışı", "🍽 Sunum Önerisi", "🥗 Alternatif Tarifler"
    ])

    with tab_ingredients:
        st.subheader("Gerekli Malzemeler")
        st.write("Elinizdeki malzemeleri işaretleyerek hazırlığa başlayabilirsiniz:")
        for m in recipe["malzemeler"]:
            st.checkbox(m, value=True, key=f"app_m_{m}")
        
        if recipe.get("eksik_malzemeler"):
            st.markdown("---")
            st.markdown("### ⚠️ Satın Alınması Önerilen Eksik Malzemeler")
            for eksik in recipe["eksik_malzemeler"]:
                st.markdown(f"<span style='color:#E74C3C;'>• {eksik}</span>", unsafe_allow_html=True)

    with tab_steps:
        st.subheader("Hazırlanış Adımları")
        for idx, adim in enumerate(recipe["yapilis"], 1):
            st.markdown(
                f"<div class='step-container'><strong>Adım {idx}:</strong> {adim}</div>",
                unsafe_allow_html=True
            )

    with tab_presentation:
        st.subheader("Şefin Sunum Tavsiyesi")
        st.markdown(
            f"<div class='presentation-box'>{recipe['sunum_onerisi']}</div>",
            unsafe_allow_html=True
        )

    with tab_alternatives:
        st.subheader("Benzer Malzemelerle 3 Alternatif Tarif")
        st.write("Bu malzemeleri farklı şekillerde değerlendirmek isterseniz:")
        for alt in recipe["alternatif_tarifler"]:
            st.markdown(f"<span class='custom-badge custom-badge-primary'>{alt}</span>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True) # End of glass card

    # Action Controls (Favorite and Downloads)
    st.write("")
    col_act1, col_act2, col_act3, col_act4 = st.columns([1.5, 1, 1, 1])

    # 1. Favorite Button
    with col_act1:
        if recipe_db_id:
            # Query if currently favorited
            current_recipes = db.search_recipes(search_query=recipe["yemek"])
            is_fav = False
            for c in current_recipes:
                if c["id"] == recipe_db_id:
                    is_fav = c["favori"] == 1
                    break
            
            fav_btn_label = "⭐ Favorilerden Çıkar" if is_fav else "⭐ Favorilere Ekle"
            if st.button(fav_btn_label, use_container_width=True):
                db.toggle_favorite(recipe_db_id)
                st.toast("Favori durumu başarıyla güncellendi!", icon="⭐")
                st.rerun()

    # 2. PDF Export Download
    with col_act2:
        try:
            pdf_path = export.generate_recipe_pdf(recipe)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📄 PDF İndir",
                    data=f,
                    file_name=f"tarif_{recipe_db_id or 'yeni'}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"PDF İndirme Butonu Hatası: {str(e)}")

    # 3. Word Export Download
    with col_act3:
        try:
            docx_path = export.generate_recipe_docx(recipe)
            with open(docx_path, "rb") as f:
                st.download_button(
                    label="📝 Word İndir",
                    data=f,
                    file_name=f"tarif_{recipe_db_id or 'yeni'}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"Word İndirme Butonu Hatası: {str(e)}")

    # 4. CSV Bulk/Single Export Download
    with col_act4:
        try:
            if recipe_db_id:
                # Find DB record
                conn = db.get_connection()
                row = conn.execute(f"SELECT * FROM {db.DB_TABLE_NAME} WHERE id = ?", (recipe_db_id,)).fetchone()
                conn.close()
                if row:
                    item_dict = dict(row)
                    # Parse json
                    import json
                    item_dict["olusturulan_tarif"] = json.loads(item_dict["olusturulan_tarif"])
                    csv_data = export.get_single_recipe_csv_data(item_dict)
                    st.download_button(
                        label="📊 CSV Dışa Aktar",
                        data=csv_data,
                        file_name=f"tarif_{recipe_db_id}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
        except Exception as e:
            st.error(f"CSV Dışa Aktarma Butonu Hatası: {str(e)}")
