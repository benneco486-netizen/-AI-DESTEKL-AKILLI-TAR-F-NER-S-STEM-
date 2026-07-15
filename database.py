"""
Database module for the AI-Powered Smart Recipe Recommendation System.
Handles SQLite connection, schema initialization, and CRUD operations for recipe storage.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import DB_PATH, DB_TABLE_NAME
from utils import logger


def get_connection() -> sqlite3.Connection:
    """
    Creates and returns a connection to the SQLite database.

    Returns:
        sqlite3.Connection: SQLite database connection.
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        # Return row objects which behave like dicts
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {str(e)}")
        raise e


def init_db() -> None:
    """
    Initializes the database schema if the table does not exist.
    """
    query = f"""
    CREATE TABLE IF NOT EXISTS {DB_TABLE_NAME} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kullanici TEXT NOT NULL,
        malzemeler TEXT NOT NULL,
        olusturulan_tarif TEXT NOT NULL,
        favori INTEGER DEFAULT 0,
        ai_modeli TEXT NOT NULL,
        tarih TEXT NOT NULL
    );
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        logger.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {str(e)}")
    finally:
        if conn:
            conn.close()


def save_recipe(
    kullanici: str,
    malzemeler: List[str],
    olusturulan_tarif: Dict[str, Any],
    favori: bool,
    ai_modeli: str
) -> Optional[int]:
    """
    Saves a generated recipe to the database.

    Args:
        kullanici (str): The user's name.
        malzemeler (List[str]): List of ingredient inputs.
        olusturulan_tarif (Dict[str, Any]): The structured recipe output from AI.
        favori (bool): Default favorite flag state.
        ai_modeli (str): AI model name (e.g. Gemini, Groq).

    Returns:
        Optional[int]: The ID of the inserted recipe, or None if save failed.
    """
    query = f"""
    INSERT INTO {DB_TABLE_NAME} (kullanici, malzemeler, olusturulan_tarif, favori, ai_modeli, tarih)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    conn = None
    inserted_id: Optional[int] = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        tarih_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            query,
            (
                kullanici,
                ", ".join(malzemeler),
                json.dumps(olusturulan_tarif, ensure_ascii=False),
                1 if favori else 0,
                ai_modeli,
                tarih_str
            )
        )
        conn.commit()
        inserted_id = cursor.lastrowid
        logger.info(f"Recipe saved successfully with ID: {inserted_id}")
    except sqlite3.Error as e:
        logger.error(f"Error saving recipe: {str(e)}")
    finally:
        if conn:
            conn.close()
    return inserted_id


def toggle_favorite(recipe_id: int) -> bool:
    """
    Toggles the favorited status of a recipe.

    Args:
        recipe_id (int): Database recipe record ID.

    Returns:
        bool: True if operation succeeded, False otherwise.
    """
    query_select = f"SELECT favori FROM {DB_TABLE_NAME} WHERE id = ?"
    query_update = f"UPDATE {DB_TABLE_NAME} SET favori = ? WHERE id = ?"
    conn = None
    success = False
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query_select, (recipe_id,))
        row = cursor.fetchone()
        if row:
            current_fav = row["favori"]
            new_fav = 0 if current_fav == 1 else 1
            cursor.execute(query_update, (new_fav, recipe_id))
            conn.commit()
            success = True
            logger.info(f"Recipe ID {recipe_id} favorite toggled to: {new_fav}")
    except sqlite3.Error as e:
        logger.error(f"Error toggling favorite: {str(e)}")
    finally:
        if conn:
            conn.close()
    return success


def delete_recipe(recipe_id: int) -> bool:
    """
    Deletes a recipe from the database.

    Args:
        recipe_id (int): Database recipe record ID.

    Returns:
        bool: True if operation succeeded, False otherwise.
    """
    query = f"DELETE FROM {DB_TABLE_NAME} WHERE id = ?"
    conn = None
    success = False
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (recipe_id,))
        conn.commit()
        success = True
        logger.info(f"Recipe ID {recipe_id} deleted successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error deleting recipe: {str(e)}")
    finally:
        if conn:
            conn.close()
    return success


def get_all_recipes() -> List[Dict[str, Any]]:
    """
    Retrieves all recipes sorted by date descending.

    Returns:
        List[Dict[str, Any]]: List of recipe rows as dictionaries.
    """
    query = f"SELECT * FROM {DB_TABLE_NAME} ORDER BY tarih DESC"
    conn = None
    results: List[Dict[str, Any]] = []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            recipe_dict = dict(row)
            # Parse json recipe field back to Python dictionary
            recipe_dict["olusturulan_tarif"] = json.loads(recipe_dict["olusturulan_tarif"])
            results.append(recipe_dict)
    except sqlite3.Error as e:
        logger.error(f"Error fetching recipes: {str(e)}")
    finally:
        if conn:
            conn.close()
    return results


def get_favorites() -> List[Dict[str, Any]]:
    """
    Retrieves all favorited recipes.

    Returns:
        List[Dict[str, Any]]: List of favorited recipe dicts.
    """
    query = f"SELECT * FROM {DB_TABLE_NAME} WHERE favori = 1 ORDER BY tarih DESC"
    conn = None
    results: List[Dict[str, Any]] = []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            recipe_dict = dict(row)
            recipe_dict["olusturulan_tarif"] = json.loads(recipe_dict["olusturulan_tarif"])
            results.append(recipe_dict)
    except sqlite3.Error as e:
        logger.error(f"Error fetching favorites: {str(e)}")
    finally:
        if conn:
            conn.close()
    return results


def search_recipes(
    search_query: str = "",
    date_filter: Optional[str] = None,
    favorite_filter: Optional[bool] = None
) -> List[Dict[str, Any]]:
    """
    Searches and filters recipes in the database.

    Args:
        search_query (str): Substring to search inside recipe name or ingredients.
        date_filter (Optional[str]): YYYY-MM-DD date filter.
        favorite_filter (Optional[bool]): True for favorited, False/None for all.

    Returns:
        List[Dict[str, Any]]: List of matched recipe dictionaries.
    """
    sql = f"SELECT * FROM {DB_TABLE_NAME} WHERE 1=1"
    params = []

    if search_query.strip():
        # Match within user ingredients, or generated recipe name/description/alternatives
        sql += " AND (malzemeler LIKE ? OR olusturulan_tarif LIKE ?)"
        like_pattern = f"%{search_query}%"
        params.extend([like_pattern, like_pattern])

    if date_filter:
        sql += " AND date(tarih) = ?"
        params.append(date_filter)

    if favorite_filter is not None:
        sql += " AND favori = ?"
        params.append(1 if favorite_filter else 0)

    sql += " ORDER BY tarih DESC"

    conn = None
    results: List[Dict[str, Any]] = []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        for row in rows:
            recipe_dict = dict(row)
            recipe_dict["olusturulan_tarif"] = json.loads(recipe_dict["olusturulan_tarif"])
            results.append(recipe_dict)
    except sqlite3.Error as e:
        logger.error(f"Error searching recipes: {str(e)}")
    finally:
        if conn:
            conn.close()
    return results
