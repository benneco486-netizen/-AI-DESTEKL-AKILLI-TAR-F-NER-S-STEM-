"""
Utility module for the AI-Powered Smart Recipe Recommendation System.
Provides logging initialization, API status checks, CSS loading, and helper utilities.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger: logging.Logger = logging.getLogger("AI_Tarif_Asistani")


def get_api_key(name: str) -> Optional[str]:
    """
    Retrieves the API key from Streamlit secrets (Streamlit Cloud) or environment variables (Local).

    Args:
        name (str): Key name, e.g. "GOOGLE_API_KEY" or "GROQ_API_KEY".

    Returns:
        Optional[str]: API key value, or None.
    """
    # 1. Try Streamlit Secrets (Streamlit Cloud)
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass

    # 2. Fallback to Environment Variables (Local)
    return os.getenv(name)


def get_api_status() -> Dict[str, bool]:
    """
    Checks the status of Gemini and Groq API keys.

    Returns:
        Dict[str, bool]: API name and availability status.
    """
    gemini_key = get_api_key("GOOGLE_API_KEY")
    groq_key = get_api_key("GROQ_API_KEY")

    has_gemini = bool(gemini_key and len(gemini_key.strip()) > 0)
    has_groq = bool(groq_key and len(groq_key.strip()) > 0)

    return {
        "Gemini": has_gemini,
        "Groq": has_groq
    }


def inject_custom_css(css_path: Path) -> None:
    """
    Reads a CSS file and injects it into the Streamlit app.

    Args:
        css_path (Path): Path to the style.css file.
    """
    try:
        if css_path.exists():
            with open(css_path, "r", encoding="utf-8") as f:
                css_content: str = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
            logger.info("Custom CSS successfully injected.")
        else:
            logger.warning(f"CSS file not found at: {css_path}")
    except Exception as e:
        logger.error(f"Error injecting CSS: {str(e)}")


def format_duration(minutes: int) -> str:
    """
    Formats the duration in minutes to a readable Turkish string.

    Args:
        minutes (int): Time in minutes.

    Returns:
        str: Formatted duration (e.g. '45 Dakika' or '1 Saat 15 Dakika').
    """
    if minutes < 60:
        return f"{minutes} Dakika"
    hours: int = minutes // 60
    rem_minutes: int = minutes % 60
    if rem_minutes == 0:
        return f"{hours} Saat"
    return f"{hours} Saat {rem_minutes} Dakika"
