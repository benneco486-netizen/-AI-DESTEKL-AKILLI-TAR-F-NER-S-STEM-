"""
Export orchestration module for the AI-Powered Smart Recipe Recommendation System.
Integrates PDF, DOCX, and CSV exporters for Streamlit download buttons.
"""

import pandas as pd
from typing import Dict, Any, List
from pathlib import Path
from pdf_generator import generate_recipe_pdf
from word_generator import generate_recipe_docx
from config import EXPORTS_DIR
from utils import logger


def get_recipe_csv_data(recipes: List[Dict[str, Any]]) -> str:
    """
    Converts a list of recipe records into a CSV string using Pandas.

    Args:
        recipes (List[Dict[str, Any]]): List of recipes loaded from the database.

    Returns:
        str: CSV string data.
    """
    flat_data = []
    for r in recipes:
        # Load inner dictionary for columns
        inner = r.get("olusturulan_tarif", {})
        flat_data.append({
            "ID": r.get("id"),
            "Kullanici": r.get("kullanici"),
            "Giris_Malzemeleri": r.get("malzemeler"),
            "Yemek_Adi": inner.get("yemek"),
            "Aciklama": inner.get("aciklama"),
            "Sure_Dakika": inner.get("sure_dakika"),
            "Zorluk": inner.get("zorluk"),
            "Kalori": inner.get("kalori"),
            "Kullanilan_Malzemeler": ", ".join(inner.get("malzemeler", [])),
            "Eksik_Malzemeler": ", ".join(inner.get("eksik_malzemeler", [])),
            "Sunum_Onerisi": inner.get("sunum_onerisi"),
            "AI_Modeli": r.get("ai_modeli"),
            "Kayit_Tarihi": r.get("tarih")
        })

    df = pd.DataFrame(flat_data)
    # Convert to CSV string
    return df.to_csv(index=False, encoding="utf-8-sig")


def get_single_recipe_csv_data(recipe: Dict[str, Any]) -> str:
    """
    Converts a single recipe record into a CSV string.

    Args:
        recipe (Dict[str, Any]): A recipe loaded from the database.

    Returns:
        str: CSV string data.
    """
    return get_recipe_csv_data([recipe])
