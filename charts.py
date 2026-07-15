"""
Charts module for the AI-Powered Smart Recipe Recommendation System.
Generates interactive Plotly visualizations for recipe statistics and history trends.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from utils import logger


def get_df_from_recipes(recipes: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Helper function to parse raw recipe dict list into a structured DataFrame.
    """
    flat_data = []
    for r in recipes:
        inner = r.get("olusturulan_tarif", {})
        flat_data.append({
            "id": r.get("id"),
            "kullanici": r.get("kullanici"),
            "favori": "Evet" if r.get("favori") == 1 else "Hayır",
            "ai_modeli": r.get("ai_modeli"),
            "tarih": pd.to_datetime(r.get("tarih")),
            "yemek": inner.get("yemek", "Bilinmeyen"),
            "sure_dakika": inner.get("sure_dakika", 0),
            "zorluk": inner.get("zorluk", "Belirsiz"),
            "kalori": inner.get("kalori", 0),
            "malzemeler": inner.get("malzemeler", [])
        })
    return pd.DataFrame(flat_data)


def plot_recipe_trend(recipes: List[Dict[str, Any]]) -> Optional[go.Figure]:
    """
    Plots the trend of generated recipes over time (daily).
    """
    if not recipes:
        return None
    df = get_df_from_recipes(recipes)
    df["tarih_gun"] = df["tarih"].dt.date
    trend_df = df.groupby("tarih_gun").size().reset_index(name="Tarif Sayısı")

    fig = px.line(
        trend_df,
        x="tarih_gun",
        y="Tarif Sayısı",
        title="📅 Günlük Tarif Oluşturma Trendi",
        labels={"tarih_gun": "Tarih", "Tarif Sayısı": "Oluşturulan Tarif"},
        markers=True,
        color_discrete_sequence=["#FF5722"]
    )
    fig.update_layout(hovermode="x unified", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def plot_difficulty_distribution(recipes: List[Dict[str, Any]]) -> Optional[go.Figure]:
    """
    Plots a donut chart representing the distribution of recipe difficulty levels.
    """
    if not recipes:
        return None
    df = get_df_from_recipes(recipes)
    diff_counts = df["zorluk"].value_counts().reset_index(name="Adet")
    diff_counts.columns = ["Zorluk Seviyesi", "Adet"]

    fig = px.pie(
        diff_counts,
        names="Zorluk Seviyesi",
        values="Adet",
        title="📊 Tarif Zorluk Dağılımı",
        hole=0.4,
        color_discrete_sequence=["#2ECC71", "#F1C40F", "#E74C3C"]
    )
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
    return fig


def plot_favorites_ratio(recipes: List[Dict[str, Any]]) -> Optional[go.Figure]:
    """
    Plots a pie chart representing the ratio of favorited recipes.
    """
    if not recipes:
        return None
    df = get_df_from_recipes(recipes)
    fav_counts = df["favori"].value_counts().reset_index(name="Adet")
    fav_counts.columns = ["Favori Durumu", "Adet"]

    fig = px.pie(
        fav_counts,
        names="Favori Durumu",
        values="Adet",
        title="⭐ Tarif Favori Oranı",
        hole=0.4,
        color="Favori Durumu",
        color_discrete_map={"Evet": "#FFD700", "Hayır": "#BDC3C7"}
    )
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
    return fig


def plot_avg_metrics(recipes: List[Dict[str, Any]]) -> Optional[go.Figure]:
    """
    Plots a bar chart showing average duration and calories by difficulty level.
    """
    if not recipes:
        return None
    df = get_df_from_recipes(recipes)
    avg_df = df.groupby("zorluk")[["sure_dakika", "kalori"]].mean().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=avg_df["zorluk"],
        y=avg_df["sure_dakika"],
        name="Ort. Süre (Dk)",
        marker_color="#FF9800"
    ))
    fig.add_trace(go.Bar(
        x=avg_df["zorluk"],
        y=avg_df["kalori"],
        name="Ort. Kalori (kcal)",
        marker_color="#3F51B5",
        yaxis="y2"
    ))

    fig.update_layout(
        title="📈 Zorluk Derecesine Göre Ortalamalar",
        yaxis=dict(title="Süre (Dakika)", titlefont=dict(color="#FF9800"), tickfont=dict(color="#FF9800")),
        yaxis2=dict(title="Kalori (kcal)", titlefont=dict(color="#3F51B5"), tickfont=dict(color="#3F51B5"),
                    overlaying="y", side="right"),
        legend=dict(x=1.1, y=1),
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def plot_top_ingredients(recipes: List[Dict[str, Any]]) -> Optional[go.Figure]:
    """
    Plots a bar chart of the top 10 most frequently used ingredients.
    """
    if not recipes:
        return None
    
    ingredients_list = []
    for r in recipes:
        # Get raw ingredients from generated recipe or raw search keywords
        # Let's count user raw inputs or final ingredients (both are useful, final ingredients is better)
        inner = r.get("olusturulan_tarif", {})
        ingredients_list.extend(inner.get("malzemeler", []))
    
    # Clean list: lower case, strip quantities to find base ingredient
    cleaned_ingredients = []
    for ing in ingredients_list:
        # Simple rule to strip digits and measurements
        words = ing.lower().split()
        # Keep words that are not numbers and common quantity words
        filtered = [w for w in words if not w.isdigit() and w not in ["adet", "gram", "gr", "kaşık", "yemek", "tatlı", "su", "bardağı", "çay", "yarım", "bir", "iki", "çimdik", "paket", "diş"]]
        clean_ing = " ".join(filtered).strip()
        if clean_ing:
            cleaned_ingredients.append(clean_ing.capitalize())

    counts = Counter(cleaned_ingredients).most_common(10)
    if not counts:
        return None

    df_counts = pd.DataFrame(counts, columns=["Malzeme", "Kullanım Sıklığı"])
    fig = px.bar(
        df_counts,
        x="Kullanım Sıklığı",
        y="Malzeme",
        orientation="h",
        title="🥦 En Çok Kullanılan İlk 10 Malzeme",
        color="Kullanım Sıklığı",
        color_continuous_scale="Viridis"
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def plot_ai_model_distribution(recipes: List[Dict[str, Any]]) -> Optional[go.Figure]:
    """
    Plots distribution of AI models utilized.
    """
    if not recipes:
        return None
    df = get_df_from_recipes(recipes)
    model_counts = df["ai_modeli"].value_counts().reset_index(name="Adet")
    model_counts.columns = ["AI Modeli", "Adet"]

    fig = px.bar(
        model_counts,
        x="AI Modeli",
        y="Adet",
        title="🤖 Kullanılan Yapay Zekâ Modeli Dağılımı",
        color="AI Modeli",
        color_discrete_sequence=["#9C27B0", "#00BCD4"]
    )
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig
