"""
Groq API integration module.
Configures the client, sends system/user messages, and handles JSON decoding.
"""

import os
import json
from typing import Dict, Any, List, Optional
from groq import Groq
from config import DEFAULT_MODEL_GROQ
from prompt import get_system_prompt, get_user_prompt
from utils import logger, get_api_key


def generate_recipe_groq(
    malzemeler: List[str],
    tarif_modu: str = "Normal (Dengeli)",
    ozel_istek: str = ""
) -> Optional[Dict[str, Any]]:
    """
    Calls the Groq API to generate a recipe from given ingredients.

    Args:
        malzemeler (List[str]): List of ingredients.
        tarif_modu (str): Focus mode (e.g. Pratik, Diyet, Gurme).
        ozel_istek (str): Custom user request or note.

    Returns:
        Optional[Dict[str, Any]]: Parsed recipe JSON, or None if failed.
    """
    api_key = get_api_key("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY could not be retrieved from environment or Streamlit secrets.")
        return None

    try:
        # Initialize the Groq client
        client = Groq(api_key=api_key)

        system_instruction = get_system_prompt()
        user_prompt = get_user_prompt(malzemeler, tarif_modu, ozel_istek)

        logger.info(f"Generating recipe with Groq model: {DEFAULT_MODEL_GROQ}...")

        # Create chat completion with JSON mode
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_instruction,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            model=DEFAULT_MODEL_GROQ,
            response_format={"type": "json_object"},
            temperature=0.7
        )

        response_content = chat_completion.choices[0].message.content
        if not response_content:
            logger.error("Empty response received from Groq.")
            return None

        # Clean codeblock indicators if present
        raw_text = response_content.strip()
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                raw_text = "\n".join(lines[1:-1])

        # Validate JSON
        recipe_data: Dict[str, Any] = json.loads(raw_text)
        logger.info("Recipe successfully generated and parsed from Groq.")
        return recipe_data

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error from Groq output: {str(e)}")
        if 'response_content' in locals() and response_content:
            logger.debug(f"Raw response text: {response_content}")
        return None
    except Exception as e:
        logger.error(f"Error in Groq recipe generation: {str(e)}")
        return None
