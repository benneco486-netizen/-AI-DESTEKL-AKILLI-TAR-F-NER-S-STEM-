"""
Google Gemini API integration module.
Configures the client, sends system/user prompts, and handles JSON decoding.
"""

import os
import json
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from config import DEFAULT_MODEL_GEMINI
from prompt import get_system_prompt, get_user_prompt
from utils import logger


def generate_recipe_gemini(
    malzemeler: List[str],
    tarif_modu: str = "Normal (Dengeli)",
    ozel_istek: str = ""
) -> Optional[Dict[str, Any]]:
    """
    Calls the Google Gemini API to generate a recipe from given ingredients.

    Args:
        malzemeler (List[str]): List of ingredients.
        tarif_modu (str): Focus mode (e.g. Pratik, Diyet, Gurme).
        ozel_istek (str): Custom user request or note.

    Returns:
        Optional[Dict[str, Any]]: Parsed recipe JSON, or None if failed.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY is not defined in the environment variables.")
        return None

    try:
        # Configure Gemini
        genai.configure(api_key=api_key)

        # Use system instructions & JSON mode if supported
        system_instruction = get_system_prompt()
        user_prompt = get_user_prompt(malzemeler, tarif_modu, ozel_istek)

        # Set up generation configuration with json mode
        generation_config = {
            "response_mime_type": "application/json",
            "temperature": 0.7
        }

        # Initialize the model
        model = genai.GenerativeModel(
            model_name=DEFAULT_MODEL_GEMINI,
            generation_config=generation_config,
            system_instruction=system_instruction
        )

        logger.info(f"Generating recipe with Gemini model: {DEFAULT_MODEL_GEMINI}...")
        response = model.generate_content(user_prompt)

        if not response or not response.text:
            logger.error("Empty response received from Gemini.")
            return None

        # Clean codeblock indicators if present
        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            # strip markdown block
            lines = raw_text.splitlines()
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                raw_text = "\n".join(lines[1:-1])

        # Validate JSON
        recipe_data: Dict[str, Any] = json.loads(raw_text)
        logger.info("Recipe successfully generated and parsed from Gemini.")
        return recipe_data

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error from Gemini output: {str(e)}")
        # Log response.text for debugging
        if 'response' in locals() and response.text:
            logger.debug(f"Raw response text: {response.text}")
        return None
    except Exception as e:
        logger.error(f"Error in Gemini recipe generation: {str(e)}")
        return None
