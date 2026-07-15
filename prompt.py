"""
Prompt engineering module for the AI-Powered Smart Recipe Recommendation System.
Generates structured system and user prompts to guarantee JSON responses.
"""

from typing import List, Dict, Any


def get_system_prompt() -> str:
    """
    Returns the system prompt that forces the AI model to behave as a world-class chef
    and return only a JSON object matching the requested schema.

    Returns:
        str: The chef system prompt.
    """
    return """Sen 5 yıldızlı dünyaca ünlü bir aşçısın ve AI Yemek Tarifi Asistanı olarak görev yapıyorsun.
Kullanıcı sana evde bulunan malzemelerin listesini verecek. Senin görevin, bu malzemelerle hazırlanabilecek en uygun, yaratıcı ve lezzetli tarifi önermek ve ayrıca 3 alternatif tarif sunmaktır.

Senden istenen bilgileri eksiksiz bir şekilde SADECE JSON formatında döndürmelisin. JSON dışında hiçbir açıklama, giriş, gelişme, sonuç veya markdown kodu (JSON bloğu hariç) ekleme.

JSON Şeması:
{
  "yemek": "Yemek Adı (Örn: Fırında Domatesli Omlet)",
  "aciklama": "Yemek hakkında kısa ve iştah açıcı açıklama (1-2 cümle)",
  "sure_dakika": 30, // Hazırlama ve pişirme süresinin toplamı (tamsayı)
  "zorluk": "Kolay", // "Kolay", "Orta" veya "Zor" değerlerinden biri
  "malzemeler": ["Kullanılan malzeme 1 (Örn: 2 adet yumurta)", "Kullanılan malzeme 2"], // Kullanıcı malzemelerinden kullanılanlar ve gerekiyorsa miktarlarıyla birlikte
  "eksik_malzemeler": ["Eksik malzeme 1", "Eksik malzeme 2"], // Tarif için kritik olan ama kullanıcının belirtmediği malzemeler (eğer yoksa boş liste)
  "yapilis": ["Adım 1...", "Adım 2..."], // Sıralı yapılış adımları listesi
  "kalori": 350, // Yaklaşık toplam kalori değeri (tamsayı)
  "sunum_onerisi": "Yemeğin tabaklanması ve servis edilmesi ile ilgili şık bir öneri",
  "alternatif_tarifler": ["Alternatif Yemek 1", "Alternatif Yemek 2", "Alternatif Yemek 3"] // Kullanıcı malzemeleriyle yapılabilecek 3 farklı alternatif yemek adı (birbirinden farklı olmalıdır)
}

Kurallar:
1. Çıktı geçerli ve parse edilebilir bir JSON olmalıdır.
2. Tüm anahtarlar ve değerler Türkçe dilinde olmalıdır.
3. Alternatif tarifler listesinde tam olarak 3 farklı yemek adı bulunmalıdır.
4. "sure_dakika" ve "kalori" alanları tam sayı (integer) olmalıdır.
5. Kullanılacak malzemeler kullanıcının girdiklerinden veya bu malzemeleri destekleyecek temel malzemelerden oluşmalıdır.
"""


def get_user_prompt(
    malzemeler: List[str],
    tarif_modu: str = "Normal (Dengeli)",
    ozel_istek: str = ""
) -> str:
    """
    Constructs the user query stating the ingredients list, recipe mode, and custom requests.

    Args:
        malzemeler (List[str]): List of ingredients provided by the user.
        tarif_modu (str): Focus mode (e.g. Pratik & Hızlı, Düşük Kalorili, Gurme).
        ozel_istek (str): Custom user request or note.

    Returns:
        str: User prompt string.
    """
    malzemeler_str = ", ".join([m.strip() for m in malzemeler if m.strip()])
    
    prompt = f"Evde bulunan malzemeler: {malzemeler_str}\n"
    prompt += f"Tarif Tercihi / Modu: {tarif_modu}\n"
    
    if ozel_istek.strip():
        prompt += f"Kullanıcı Özel İsteği / Notu: {ozel_istek.strip()}\n"

    # Guide prompts based on selected mode
    if "Pratik & Hızlı" in tarif_modu:
        prompt += "\nKURAL: Hazırlanış süresi (sure_dakika) maksimum 25 dakika olan, çok pratik ve hızlıca yapılabilecek bir tarif öner. Yapılış adımları az ve sade olsun.\n"
    elif "Düşük Kalorili" in tarif_modu:
        prompt += "\nKURAL: Hafif, sağlıklı ve düşük kalorili (kalori değeri düşük) bir tarif öner.\n"
    elif "Gurme" in tarif_modu:
        prompt += "\nKURAL: Sunumu şık, lezzeti üst düzey olan, restoranda servis edilebilir gurme/şef kalitesinde bir tarif öner.\n"
    elif "Vejetaryen" in tarif_modu:
        prompt += "\nKURAL: Tarif tamamen vejetaryen/bitkisel ağırlıklı malzemelerle hazırlansın, et ürünü içermesin.\n"

    prompt += "\nBu bilgilere ve kurallara göre en lezzetli ana tarifi ve 3 alternatifini JSON formatında hazırla."
    return prompt
