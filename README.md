# 👨‍🍳 AI Destekli Akıllı Tarif Öneri Sistemi

Bu proje, evinizde bulunan malzemeleri girerek yapay zekâ desteğiyle saniyeler içinde zengin, detaylı ve alternatifli yemek tarifleri oluşturmanızı sağlayan profesyonel bir Streamlit uygulamasıdır. Hem **Google Gemini** hem de **Groq** API'lerini destekleyen esnek bir AI mimarisine sahiptir. Oluşturulan tüm tarifler otomatik olarak yerel bir SQLite veritabanına kaydedilir, favorilere eklenebilir, geçmiş sekmesinden tekrar incelenebilir ve PDF, Word veya CSV formatlarında dışa aktarılabilir.

---

## 🌟 Öne Çıkan Özellikler

*   **Çift Yapay Zekâ Modeli Desteği:** `.env` dosyasında `GROQ_API_KEY` tanımlıysa kullanıcı arayüz üzerinden Gemini ile Groq arasında geçiş yapabilir. Tanımlı değilse sistem otomatik olarak Gemini modelini kullanır.
*   **Tam Yapılandırılmış JSON Şeması:** Model çıktıları mutlak şekilde doğrulanmış JSON formatındadır. Yemek ismi, hazırlama süresi, kalori, zorluk, malzemeler, eksik malzemeler, adım adım yapılış, sunum önerisi ve 3 adet benzersiz alternatif tarifi içerir.
*   **Gelişmiş Veritabanı Yönetimi:** SQLite veritabanı sayesinde tüm tarif geçmişiniz güvenli bir şekilde saklanır.
*   **Dosya Dışa Aktarma Paketleri:**
    *   **PDF:** Türkçe karakter destekli (Roboto Font entegrasyonu), özel renk ve tablolu tasarım.
    *   **Word:** Profesyonel başlıklar ve listelerle organize edilmiş `.docx` belgesi.
    *   **CSV:** Pandas aracılığıyla veri analitiğine hazır, virgülle ayrılmış sütun formatı.
*   **İnteraktif Grafik & Analiz Paneli:** Plotly kullanılarak hazırlanan analiz sayfasında toplam tarif sayısı, favori oranları, zorluk dağılımı, en çok kullanılan malzemelerin kelime sıklığı analizi ve günlük/haftalık tarif oluşturma trendleri görselleştirilmiştir.
*   **Premium SaaS Tasarımı (UI/UX):** assets/style.css ile entegre Glassmorphic kart tasarımları, gradyan renk geçişleri, hover mikro-animasyonları, özel badge tasarımları ve tam mobil uyumluluk.

---

## 🛠️ Kullanılan Teknolojiler

*   **Programlama Dili:** Python 3.9+
*   **Arayüz:** Streamlit
*   **Yapay Zekâ Motorları:** Google Gemini API (`google-generativeai`), Groq API (`groq`)
*   **Veritabanı:** SQLite3
*   **Veri Analizi & Grafik:** Pandas, Plotly
*   **Raporlama & Export:** FPDF2, Python-Docx, Pillow
*   **Konfigürasyon:** Python-Dotenv

---

## 📁 Proje Dosya Yapısı

```text
AI_Tarif_Asistani/
│
├── app.py                # Ana Streamlit Uygulama Arayüzü & Giriş Ekranı
├── config.py             # Sayfa Ayarları, Tema Renkleri ve Dosya Yolları Sabitleri
├── database.py           # SQLite Veritabanı Kurulumu & CRUD Operasyonları
├── gemini_api.py         # Google Gemini API Bağlantısı & JSON İstek Yönetimi
├── groq_api.py           # Groq API Bağlantısı & Llama JSON İstek Yönetimi
├── prompt.py             # Yapay Zekâ Şef Rolü & JSON Çıktı Şeması Tanımı
├── pdf_generator.py      # Unicode Roboto Font Destekli PDF Rapor Oluşturucu
├── word_generator.py     # python-docx Tabanlı Word Belgesi Rapor Oluşturucu
├── export.py             # CSV Dönüşümü & Dışa Aktarma Yardımcıları
├── charts.py             # Plotly İnteraktif Grafik Tanımlamaları
├── utils.py              # Loglama Ayarları, CSS Injector ve API Durum Kontrolleri
├── requirements.txt      # Gerekli Kütüphaneler Listesi
├── .env                  # API Anahtarları Dosyası (Git'e gönderilmez)
├── .env.example          # API Anahtarları Örnek Şablonu
├── .gitignore            # Git Tarafından Yoksayılacak Klasör/Dosyalar Listesi
│
├── assets/
│   ├── style.css         # Modern SaaS CSS Kodları (Glassmorphism & Gradients)
│   ├── logo.png          # Yapay Zekâ ile Üretilen Premium Proje Logosu
│   └── banner.png        # Yapay Zekâ ile Üretilen Premium Proje Banner Resmi
│
└── exports/              # İndirilebilir PDF, Word ve CSV Dosyalarının Kayıt Klasörü
```

---

## 🚀 Kurulum ve Çalıştırma

### 1. Depoyu Klonlayın veya İndirin

Proje dosyalarını yerel bilgisayarınıza indirin.

### 2. Sanal Ortam Oluşturun (Önerilir)

Terminal veya Komut Satırında aşağıdaki komutları sırasıyla çalıştırın:

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Gerekli Kütüphaneleri Yükleyin

```bash
pip install -r requirements.txt
```

### 4. API Anahtarlarını Yapılandırın

Proje ana dizininde bulunan `.env.example` dosyasının adını `.env` olarak değiştirin ve API anahtarlarınızı ekleyin:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

*   **Gemini API Anahtarı Almak İçin:** [Google AI Studio](https://aistudio.google.com/) adresini ziyaret edin.
*   **Groq API Anahtarı Almak İçin:** [Groq Console](https://console.groq.com/) adresini ziyaret edin.

### 5. Uygulamayı Başlatın

```bash
streamlit run app.py
```

Uygulama çalıştıktan sonra tarayıcınızda otomatik olarak `http://localhost:8501` adresi açılacaktır.

---

## 📊 Veritabanı Yapısı

Sistem, `database.db` adında bir SQLite veritabanı dosyası oluşturur. Veritabanındaki `tarifler` tablosunun yapısı şu şekildedir:

| Kolon Adı | Veri Tipi | Açıklama |
| :--- | :--- | :--- |
| `id` | INTEGER PRIMARY KEY | Otomatik artan tekil numara |
| `kullanici` | TEXT | Tarifi oluşturan kişinin kullanıcı adı |
| `malzemeler` | TEXT | Kullanıcının arama yaptığı ham malzeme listesi |
| `olusturulan_tarif` | TEXT | Yapay zekâ tarafından döndürülen JSON tarifi |
| `favori` | INTEGER | Tarifin favori durumu (0: Hayır, 1: Evet) |
| `ai_modeli` | TEXT | Tarifi oluşturan modelin ismi (Gemini veya Groq) |
| `tarih` | TEXT | Tarifin oluşturulma tarihi (YYYY-MM-DD HH:MM:SS) |

---

## 👨‍💻 Geliştirici Notları

*   Uygulama tamamen **Temiz Kod (Clean Code)**, **SOLID** prensipleri ve **PEP-8** standartlarına uygun şekilde kodlanmıştır.
*   Bütün fonksiyonlar ve sınıflar için **Type Hinting** (Tip Belirteçleri) kullanılmış ve açıklayıcı **Docstring** blokları eklenmiştir.
*   Hata yönetimi (Exception Handling) ve detaylı loglama (`logging` modülü) sayesinde sistem çalışma anında oluşabilecek kesintilere karşı dayanıklıdır.
*   PDF üretimi sırasında Türkçe karakterlerin bozulmaması için uygulamanın ilk açılışında Google Roboto font ailesi `assets/` klasörüne otomatik olarak indirilir.

---

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için lisans dosyasına göz atabilirsiniz.
