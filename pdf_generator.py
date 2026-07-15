"""
PDF Generator module for the AI-Powered Smart Recipe Recommendation System.
Generates structured PDF documents containing recipe details with Turkish character support.
"""

import os
import urllib.request
from pathlib import Path
from typing import Dict, Any
from fpdf import FPDF
from config import ASSETS_DIR, EXPORTS_DIR
from utils import logger, format_duration

# Font download URLs for Turkish character support
ROBOTO_REGULAR_URL = "https://github.com/google/fonts/raw/main/ofl/roboto/static/Roboto-Regular.ttf"
ROBOTO_BOLD_URL = "https://github.com/google/fonts/raw/main/ofl/roboto/static/Roboto-Bold.ttf"

ROBOTO_REG_PATH = ASSETS_DIR / "Roboto-Regular.ttf"
ROBOTO_BOLD_PATH = ASSETS_DIR / "Roboto-Bold.ttf"


def ensure_pdf_fonts() -> None:
    """
    Downloads Roboto fonts if they do not exist locally to ensure full Turkish character support.
    """
    try:
        if not ROBOTO_REG_PATH.exists():
            logger.info("Downloading Roboto-Regular font...")
            urllib.request.urlretrieve(ROBOTO_REG_URL, str(ROBOTO_REG_PATH))
        if not ROBOTO_BOLD_PATH.exists():
            logger.info("Downloading Roboto-Bold font...")
            urllib.request.urlretrieve(ROBOTO_BOLD_URL, str(ROBOTO_BOLD_PATH))
    except Exception as e:
        logger.error(f"Error downloading fonts: {str(e)}. PDF generation might have encoding errors.")


class RecipePDF(FPDF):
    """
    Custom FPDF class for styling PDF documents.
    """
    def header(self) -> None:
        # Title banner
        self.set_font("Roboto", "B", 10)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "AI Tarif Asistanı - Özel Yemek Tarifi", 0, 1, "R")
        self.ln(5)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Roboto", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Sayfa {self.page_no()}/{{nb}} | Yapay Zekâ Tarafından Oluşturulmuştur", 0, 0, "C")


def generate_recipe_pdf(recipe: Dict[str, Any]) -> str:
    """
    Generates a PDF file for the given recipe.

    Args:
        recipe (Dict[str, Any]): Recipe data matching our schema.

    Returns:
        str: Absolute path to the generated PDF.
    """
    ensure_pdf_fonts()

    pdf = RecipePDF()
    pdf.alias_nb_pages()

    # Load custom fonts
    if ROBOTO_REG_PATH.exists() and ROBOTO_BOLD_PATH.exists():
        pdf.add_font("Roboto", "", str(ROBOTO_REG_PATH))
        pdf.add_font("Roboto", "B", str(ROBOTO_BOLD_PATH))
        font_name = "Roboto"
    else:
        # Fallback to standard Helvetica if download failed
        font_name = "Helvetica"
        logger.warning("Using fallback Helvetica font. Special characters may fail.")

    pdf.add_page()
    pdf.set_margins(15, 20, 15)

    # 1. Yemek Adı (Title)
    pdf.set_font(font_name, "B", 24)
    pdf.set_text_color(255, 87, 34)  # Deep Orange color theme
    pdf.cell(0, 15, recipe["yemek"], 0, 1, "L")

    # Divider line
    pdf.set_draw_color(255, 87, 34)
    pdf.set_line_width(0.8)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(5)

    # 2. Açıklama (Description)
    pdf.set_font(font_name, "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 6, recipe["aciklama"])
    pdf.ln(8)

    # 3. Bilgi Kartları Tablosu (Time, Difficulty, Calories)
    pdf.set_fill_color(245, 245, 245)
    pdf.set_draw_color(220, 220, 220)
    pdf.set_line_width(0.2)
    
    # Draw headers
    pdf.set_font(font_name, "B", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(60, 8, "Hazırlama Süresi", 1, 0, "C", fill=True)
    pdf.cell(60, 8, "Zorluk Seviyesi", 1, 0, "C", fill=True)
    pdf.cell(60, 8, "Yaklaşık Kalori", 1, 1, "C", fill=True)

    # Draw values
    pdf.set_font(font_name, "", 11)
    pdf.set_text_color(33, 33, 33)
    pdf.cell(60, 10, format_duration(recipe["sure_dakika"]), 1, 0, "C")
    pdf.cell(60, 10, recipe["zorluk"], 1, 0, "C")
    pdf.cell(60, 10, f"{recipe['kalori']} kcal", 1, 1, "C")
    pdf.ln(10)

    # 4. Malzemeler (Ingredients)
    pdf.set_font(font_name, "B", 14)
    pdf.set_text_color(76, 175, 80)  # Green color theme
    pdf.cell(0, 8, "📋 Kullanılacak Malzemeler", 0, 1, "L")
    pdf.ln(2)

    pdf.set_font(font_name, "", 10.5)
    pdf.set_text_color(33, 33, 33)
    for malzeme in recipe["malzemeler"]:
        pdf.cell(5, 6, "-", 0, 0, "L")
        pdf.cell(0, 6, malzeme, 0, 1, "L")
    
    # Eksik malzemeler varsa yazdır
    if recipe.get("eksik_malzemeler"):
        pdf.ln(4)
        pdf.set_font(font_name, "B", 11)
        pdf.set_text_color(231, 76, 60)  # Red theme
        pdf.cell(0, 6, "⚠️ Eksik Malzemeler (Satın Alınması Önerilenler):", 0, 1, "L")
        pdf.set_font(font_name, "", 10)
        pdf.set_text_color(33, 33, 33)
        for eksik in recipe["eksik_malzemeler"]:
            pdf.cell(5, 5, "-", 0, 0, "L")
            pdf.cell(0, 5, eksik, 0, 1, "L")
    
    pdf.ln(8)

    # 5. Adım Adım Yapılışı (Steps)
    pdf.set_font(font_name, "B", 14)
    pdf.set_text_color(255, 87, 34)
    pdf.cell(0, 8, "👨🍳 Adım Adım Yapılışı", 0, 1, "L")
    pdf.ln(2)

    pdf.set_font(font_name, "", 10.5)
    pdf.set_text_color(33, 33, 33)
    for idx, adim in enumerate(recipe["yapilis"], 1):
        pdf.set_font(font_name, "B", 10.5)
        pdf.cell(10, 6, f"{idx}.", 0, 0, "L")
        pdf.set_font(font_name, "", 10.5)
        # Handle line wrap for long steps
        pdf.multi_cell(0, 6, adim)
        pdf.ln(2)

    pdf.ln(6)

    # 6. Sunum Önerisi (Presentation)
    pdf.set_font(font_name, "B", 14)
    pdf.set_text_color(156, 39, 176)  # Purple color theme
    pdf.cell(0, 8, "🍽️ Sunum Önerisi", 0, 1, "L")
    pdf.ln(2)

    pdf.set_font(font_name, "", 10.5)
    pdf.set_text_color(33, 33, 33)
    pdf.multi_cell(0, 6, recipe["sunum_onerisi"])
    pdf.ln(8)

    # 7. Alternatif Tarifler (Alternatives)
    pdf.set_font(font_name, "B", 14)
    pdf.set_text_color(33, 150, 243)  # Blue color theme
    pdf.cell(0, 8, "🥗 Alternatif Tarif Önerileri", 0, 1, "L")
    pdf.ln(2)

    pdf.set_font(font_name, "", 11)
    pdf.set_text_color(33, 33, 33)
    for alt in recipe["alternatif_tarifler"]:
        pdf.cell(5, 6, "*", 0, 0, "L")
        pdf.cell(0, 6, alt, 0, 1, "L")

    # Output file path
    # Secure filename
    safe_name = "".join([c if c.isalnum() else "_" for c in recipe["yemek"]])
    pdf_filename = f"tarif_{safe_name}.pdf"
    file_path = EXPORTS_DIR / pdf_filename

    pdf.output(str(file_path))
    logger.info(f"PDF generated successfully at: {file_path}")
    return str(file_path)
