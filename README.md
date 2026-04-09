Markdown
İhale Radarı & Otomasyon Botu

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated-2088FF?style=for-the-badge&logo=github-actions)
![Telegram API](https://img.shields.io/badge/Telegram-Bot-2CA5E0?style=for-the-badge&logo=telegram)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

💧 EKAP Tender Tracker (HLC EPC Service)
Bu proje, EKAP (Elektronik Kamu Alımları Platformu) üzerinden belirli anahtar kelimelerle (SCADA, Otomasyon, GES, RES, Altyapı vb.) otomatik olarak ihale takibi yapan ve kriterlere uygun yeni ihaleleri Telegram üzerinden anlık olarak bildiren bir Python otomasyonudur.

Özellikle EPC (Mühendislik, Tedarik ve Kurulum) projelerine odaklanan gelişmiş bir filtreleme mekanizmasına sahiptir.

✨ Öne Çıkan Özellikler
🔍 Akıllı Arama: Sadece ihale adını değil, EKAP'ın derinliklerindeki teknik detayları tarar.

🛡️ Gelişmiş Filtreleme: EPC dışı işleri (sadece malzeme alımı, sadece danışmanlık/çizim vb.) negatif anahtar kelime listesiyle otomatik eler.

🤖 Anti-Bot Koruması: EKAP'ın güncel Angular altyapısına ve SSL engellerine uyumlu tarama motoru.

🧠 Akıllı Hafıza: Gönderilen ihaleleri local_sent_ihales.txt dosyasında tutar; aynı ihaleyi asla tekrar göndermez.

⚡ Telegram Entegrasyonu: İhale detaylarını (İKN, İdare, Tür, Tarih) şık bir formatla anlık mesaj olarak iletir.

🛠️ Teknik Altyapı
Dil: Python 3.x

Motor: Playwright (Tarayıcı otomasyonu için)

İletişim: Requests (API entegrasyonu için)

Veri Formatı: JSON & HTML Parsing

🚀 Kurulum ve Çalıştırma
1. Depoyu Klonlayın
Bash
git clone https://github.com/kullaniciadi/proje-adi.git
cd proje-adi
2. Sanal Ortamı Oluşturun ve Aktif Edin
Bash
python -m venv venv
# Windows için:
.\venv\Scripts\activate
# Linux/Mac için:
source venv/bin/activate
3. Gerekli Kütüphaneleri Yükleyin
Bash
pip install requests python-dotenv playwright
playwright install chromium
4. Yapılandırma
Klasör dizininde bir .env dosyası oluşturun ve bilgilerinizi girin:

Kod snippet'i
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_CHAT_ID=your_chat_id_here
config.py dosyasını düzenleyerek takip etmek istediğiniz sektörleri (GES, RES, Otomasyon vb.) ve elenmesini istediğiniz kelimeleri özelleştirebilirsiniz.

5. Çalıştırın
Bash
python main.py
📂 Dosya Yapısı
main.py: Ana döngüyü yöneten ve Telegram gönderimlerini yapan ana dosya.

ekap_api.py: EKAP üzerindeki tarama, tıklama ve veri çekme mantığını içeren motor.

config.py: Anahtar kelimeler, negatif kelimeler ve genel ayarlar.

local_sent_ihales.txt: Botun daha önce gönderdiği ihaleleri unutmamak için kullandığı yerel veritabanı.

⚖️ Yasal Uyarı
Bu proje sadece eğitim ve kişisel verimlilik amaçlıdır. Kamu platformlarının kullanım koşullarına ve veri çekme (scraping) politikalarına uyulması kullanıcının sorumluluğundadır.

HLC Endüstriyel Otomasyon & EPC Çözümleri için geliştirilmiştir. 🚀

Küçük Bir Tavsiye:
GitHub'a yüklemeden önce klasöründe bir .gitignore dosyası oluşturup içine şunları yazmayı unutma; böylece özel şifrelerin (Token) ve gereksiz dosyalar internete sızmaz:

Plaintext
.env
venv/
__pycache__/
local_sent_ihales.txt
*.png
Geliştirici Notu: Bu sistem, manuel ihale tarama süreçlerinde harcanan yüzlerce saatlik insan emeğini sıfıra indirmek ve şirket portföyüne en uygun projeleri "ilk duyan" olmak amacıyla yüksek mühendislik standartlarında tasarlanmıştır.
