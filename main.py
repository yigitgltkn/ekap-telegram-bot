# ⚡ EKAP İhale Takip Botu

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Headless-45ba4b?style=for-the-badge&logo=playwright&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![License](https://img.shields.io/badge/Lisans-MIT-yellow?style=for-the-badge)

**Türkiye'nin kamu ihale platformu EKAP'ı gerçek zamanlı olarak izleyen,**  
**EPC & Altyapı projelerini akıllı filtreleyip anında Telegram'a bildiren otomasyon sistemi.**

</div>

---

## 📌 İçindekiler

- [Proje Hakkında](#-proje-hakkında)
- [Mimari](#-mimari)
- [Özellikler](#-özellikler)
- [Kurulum](#-kurulum)
- [Konfigürasyon](#-konfigürasyon)
- [Kullanım](#-kullanım)
- [Akış Diyagramı](#-akış-diyagramı)
- [Klasör Yapısı](#-klasör-yapısı)
- [Katkı Sağlama](#-katkı-sağlama)

---

## 🎯 Proje Hakkında

Bu sistem, **HLC EPC** firmaları için özelleştirilmiş bir kamu ihale izleme botudur. EKAP (Elektronik Kamu Alımları Platformu) üzerindeki ihaleleri headless browser ile tarar, akıllı filtreleme algoritması ile küçük ve ilgisiz ihaleleri eleyerek yalnızca büyük ölçekli **EPC, altyapı, arıtma ve otomasyon** projelerini tespit eder. Bulunan ihaleler anında **Telegram grubu** üzerinden ekibe bildirilir.

> Sistem, yalnızca API sorgularına dayanmaz. Gizli bütçe ve detay bilgilerini elde edebilmek için **Popup Dedektif** adı verilen özel bir mekanizma ile ihale tıklamalarını simüle ederek arka planda çalışan API isteklerini yakalar.

---

## 🏗️ Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                              │
│          Orkestrasyon & Telegram Bildirim Katmanı           │
└───────────────────────┬─────────────────────────────────────┘
                        │
          ┌─────────────▼──────────────┐
          │         ekap_api.py        │
          │   EKAP Tarama & Filtreleme │
          └──────┬──────────┬──────────┘
                 │          │
    ┌────────────▼──┐  ┌────▼────────────────┐
    │  search_      │  │  get_ihale_detail()  │
    │  ihaleler()   │  │  🕵️ Popup Dedektif   │
    │  Playwright   │  │  Playwright          │
    └───────────────┘  └─────────────────────┘
```

| Bileşen | Görev |
|---|---|
| `main.py` | Ana orkestrasyon, Telegram mesaj gönderimi, hafıza yönetimi |
| `ekap_api.py` | EKAP tarama motoru, filtreleme algoritması, bütçe hesaplayıcı |
| `config.py` | Anahtar kelimeler, CPV kodları, kara liste, ortam değişkenleri |

---

## ✨ Özellikler

### 🔍 Çok Katmanlı Arama
- **Anahtar Kelime Tarama** — `SCADA`, `Otomasyon`, `Telemetri`, `Arıtma`, `İsale Hattı` ve daha fazlası
- **CPV Kodu Tarama** — Resmi KİK kodlarıyla başlıkta geçmeyen ihaleleri de yakalar
- **Akıllı Tekilleştirme** — Aynı ihale birden fazla kelimede eşleşse bile yalnızca bir kez bildirilir

### 🧠 EPC Filtre Motoru
- **Bütçe Eşiği** — 5.000.000 TL altındaki ihaleler otomatik elenir
- **İhale Türü Kontrolü** — Mal & Hizmet alımları için daha sıkı bütçe kriteri uygulanır
- **Usul Dışı Bırakma** — `21/F (Pazarlık)` ve `Doğrudan Temin` ihaleleri atlanır
- **Kara Liste** — Küçük malzeme, temizlik, akaryakıt gibi ilgisiz ihaleler regex ile elenir

### 🕵️ Popup Dedektif Mekanizması
Bazı ihaleler yaklaşık maliyetini API listesinde göstermez. Bu sistem:
1. Headless Chromium ile EKAP'a gerçek bir tarayıcı gibi giriş yapar
2. İlgili ihaleye tıklamayı simüle eder
3. Arka planda tetiklenen `GetById` API isteğini ağ trafiğinden yakalar
4. Gizli bütçeyi ve detay bilgileri (`son teklif tarihi`, `ihale yeri`, `işin yapılacağı yer`) alır

### 📬 Telegram Bildirimleri
- HTML formatlı, okunması kolay mesajlar
- İKN ve tarih alanları `<code>` etiketi ile kopyalanabilir hâlde sunulur
- **KİK İtirazen Şikayet Başvuru Bedeli** otomatik hesaplanır
- Inline button ile EKAP arama sayfasına doğrudan bağlantı

### 💾 Hafıza Sistemi
- Bir kez bildirilen ihaleler `ihaleler_liste.txt` dosyasına yazılır
- Bot yeniden başlatıldığında aynı ihaleler ikinci kez bildirilmez

---

## 🚀 Kurulum

### Gereksinimler

- Python 3.10+
- pip

### Adımlar

```bash
# 1. Repoyu klonla
git clone https://github.com/kullanici-adi/ekap-ihale-botu.git
cd ekap-ihale-botu

# 2. Sanal ortam oluştur ve aktifleştir
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Playwright tarayıcısını indir
playwright install chromium

# 5. Ortam değişkenlerini ayarla
cp .env.example .env
# .env dosyasını düzenle (aşağıya bak)
```

### `requirements.txt`

```
playwright
python-dotenv
requests
```

---

## ⚙️ Konfigürasyon

### `.env` Dosyası

```env
TELEGRAM_BOT_TOKEN=123456789:ABCDEFGHijklmnopqrstuvwxyz
ADMIN_CHAT_ID=-1001234567890
```

| Değişken | Açıklama |
|---|---|
| `TELEGRAM_BOT_TOKEN` | [@BotFather](https://t.me/BotFather) üzerinden alınan bot token'ı |
| `ADMIN_CHAT_ID` | Bildirimlerin gönderileceği grup veya kanal ID'si (negatif olabilir) |

### `config.py` — Arama Kelimelerini Özelleştirme

```python
# Sektöre özgü teknik anahtar kelimeler
ANAHTAR_KELIMELER = ["SCADA", "Otomasyon", "RTU", ...]

# Büyük altyapı projeleri
EPC_KELIMELERI = ["Arıtma", "İsale Hattı", "Terfi Merkezi", ...]

# KİK resmi CPV kodları
CPV_KODLARI = ["45232100", "45252127", ...]

# İlgisiz ihaleleri otomatik eleyecek kara liste
NEGATIF_KELIMELER = ["Malzemeleri", "Yedek Parça", "Temizlik", ...]
```

### Bütçe Eşiği

`ekap_api.py` içindeki `butce_uygun_mu()` fonksiyonunda eşiği değiştirebilirsiniz:

```python
if deger >= 5000000:   # ← Minimum bütçe (TL cinsinden)
    gecerli_butce_var_mi = True
```

---

## 🖥️ Kullanım

### Tek Seferlik Çalıştırma

```bash
python main.py
```

### Zamanlanmış Görev (Cron) — Linux/macOS

Her 30 dakikada bir otomatik çalıştırmak için:

```bash
crontab -e
```

```cron
*/30 * * * * /path/to/venv/bin/python /path/to/ekap-ihale-botu/main.py >> /var/log/ekap_bot.log 2>&1
```

### Zamanlanmış Görev — Windows (Task Scheduler)

```
Eylem: Program/script → python.exe
Bağımsız değişkenler: C:\path\to\main.py
Başlangıç yeri: C:\path\to\ekap-ihale-botu\
```

---

## 🔄 Akış Diyagramı

```
main.py başlar
     │
     ▼
EKAP'ta her anahtar kelime için arama yap (Playwright)
     │
     ▼
Ham ihaleleri topla & tekilleştir
     │
     ▼
EPC Filtre Motoru:
  ├─ Usul kontrolü (Pazarlık / Doğrudan → Eله)
  ├─ Kara liste kontrolü (negatif kelimeler → ELE)
  ├─ Bütçe eşiği kontrolü (< 5M TL → ELE)
  ├─ İhale türü × bütçe kombinasyonu
  └─ Anahtar kelime tam eşleşme kontrolü
     │
     ▼
Hafıza kontrolü: Bu İKN daha önce gönderildi mi?
  ├─ EVET → Atla
  └─ HAYIR → Devam et
               │
               ▼
          🕵️ Popup Dedektif:
          Tıklamayı simüle et → GetById'ı yakala
          Gizli bütçeyi & detayları al
               │
               ▼
          KİK Şikayet Bedeli Hesapla
               │
               ▼
          Telegram'a HTML mesaj gönder
               │
               ▼
          İKN'yi hafızaya (txt) yaz
```

---

## 📁 Klasör Yapısı

```
ekap-ihale-botu/
├── main.py               # Ana orkestrasyon & Telegram gönderimi
├── ekap_api.py           # EKAP tarama motoru & Popup Dedektif
├── config.py             # Anahtar kelimeler, CPV kodları, konfigürasyon
├── .env                  # Gizli değişkenler (git'e ekleme!)
├── .env.example          # Örnek .env şablonu
├── ihaleler_liste.txt    # Gönderilen İKN hafızası (otomatik oluşur)
├── requirements.txt      # Python bağımlılıkları
└── README.md
```

---

## 📊 Telegram Mesaj Örneği

```
⚡ YENİ EPC & ALTYAPI İHALESİ 💧

📌 İKN:     2025/123456
📅 Tarih:   2025-09-15
📋 İhale:   Merkezi Atıksu Arıtma Tesisi Yapımı
🏢 Kurum:   Ankara Su ve Kanalizasyon İdaresi
🏗️ Tür / Usul:  Yapım İşi | Açık İhale
💰 Yaklaşık Bütçe:  45.000.000,00 TL
⚖️ İtirazen Şikayet Bedeli:  194.085 TL
⏰ Son Teklif:  2025-09-15 10:00

(Kopyalamak için İKN ve Tarih'in üzerine dokunun)
#HLC #EPC #Altyapı

[ 🔗 EKAP Arama Sayfasına Git ]
```

---

## ⚠️ Önemli Notlar

- **Headless Browser** kullanıldığından EKAP'ın yapısı değişirse `locator` ifadelerinin güncellenmesi gerekebilir.
- Bot, EKAP'ta anlık olarak ilanı açık olan ihaleleri getirir; geçmiş tarihli ihaleler filtrelenir.
- `.env` dosyasını asla `git push` etmeyin. `.gitignore`'a eklenmiş olduğundan emin olun.

---

## 🤝 Katkı Sağlama

1. Fork'layın
2. Feature branch açın (`git checkout -b feature/yeni-ozellik`)
3. Değişiklikleri commit'leyin (`git commit -m 'feat: yeni özellik eklendi'`)
4. Branch'i push'layın (`git push origin feature/yeni-ozellik`)
5. Pull Request açın

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında dağıtılmaktadır.

---

<div align="center">
  <sub>HLC EPC için 🛠️ ile inşa edildi.</sub>
</div>
