"""
Configuration module for the AI-Powered Smart Recipe Recommendation System.
Defines constants, style themes, API parameters, database options, and file paths.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Base Directory of the Project
BASE_DIR: Path = Path(__file__).resolve().parent

# Application Info
APP_NAME: str = "AI Tarif Asistanı"
APP_TITLE: str = "👨🍳 AI Destekli Akıllı Tarif Öneri Sistemi"
APP_SUBTITLE: str = "Evde bulunan malzemelerle saniyeler içinde yapay zekâ destekli tarif oluşturun."
FAVICON: str = "🍳"

# Directory Paths
EXPORTS_DIR: Path = BASE_DIR / "exports"
ASSETS_DIR: Path = BASE_DIR / "assets"
PAGES_DIR: Path = BASE_DIR / "pages"

# Ensure directories exist
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
PAGES_DIR.mkdir(parents=True, exist_ok=True)

# Asset Paths
LOGO_PATH: Path = ASSETS_DIR / "logo.png"
BANNER_PATH: Path = ASSETS_DIR / "banner.png"
STYLE_CSS_PATH: Path = ASSETS_DIR / "style.css"

# Database Configuration
DB_PATH: Path = BASE_DIR / "database.db"
DB_TABLE_NAME: str = "tarifler"

# AI Model Selection Options
DEFAULT_MODEL_GEMINI: str = "gemini-2.5-flash"
DEFAULT_MODEL_GROQ: str = "llama-3.3-70b-versatile"

# UI/UX & Style Colors (Hex values for components/Plotly)
THEME_COLORS: Dict[str, str] = {
    "primary": "#FF5722",      # Deep Orange
    "secondary": "#4CAF50",    # Green
    "accent": "#9C27B0",       # Purple
    "background_dark": "#1E1E2F",
    "background_light": "#F8F9FA",
    "card_dark": "rgba(255, 255, 255, 0.05)",
    "card_light": "rgba(0, 0, 0, 0.03)",
    "text_dark": "#FFFFFF",
    "text_light": "#212121",
    "success": "#2ECC71",
    "warning": "#F1C40F",
    "danger": "#E74C3C"
}

# Default Prompt Configurations
RECIPE_SCHEMA: Dict[str, Any] = {
    "yemek": "Yemek Adı",
    "aciklama": "Kısa Açıklama",
    "sure_dakika": 0,
    "zorluk": "Kolay/Orta/Zor",
    "malzemeler": ["liste"],
    "eksik_malzemeler": ["liste"],
    "yapilis": ["adım 1", "adım 2"],
    "kalori": 0,
    "sunum_onerisi": "sunum önerisi",
    "alternatif_tarifler": ["tarif 1", "tarif 2", "tarif 3"]
}
