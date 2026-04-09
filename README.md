Markdown
İhale Radarı & Otomasyon Botu

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated-2088FF?style=for-the-badge&logo=github-actions)
![Telegram API](https://img.shields.io/badge/Telegram-Bot-2CA5E0?style=for-the-badge&logo=telegram)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

EKAP ihale radari, EKAP (Elektronik Kamu Alımları Platformu) üzerinde yayınlanan altyapı, SCADA, otomasyon ve su yapıları (isale hattı, arıtma vb.) ihalelerini 7/24 izleyen, süzen ve kritik projeleri doğrudan Telegram grubuna raporlayan **tam otonom bir iş geliştirme asistanıdır.**

Sistem; sıradan bir web kazıyıcı (scraper) değil, bütçe sınırlarını, ihale usullerini ve KİK yasal bedellerini analiz eden akıllı bir mühendislik botudur.

---

## 🔥 Temel Özellikler

* **🧠 Akıllı Filtreleme Algoritması:** 5.000.000 TL altındaki bütçeleri, 21/f (pazarlık) ve doğrudan temin usullerini, standart mal/hizmet alımlarını otomatik eler. Sadece devasa EPC projelerine odaklanır.
* **⚖️ KİK İtirazen Şikayet Bedeli Hesaplayıcı:** İhalenin yaklaşık maliyetine göre 2026 Kamu İhale Kurumu tarifesi üzerinden güncel başvuru bedelini anında hesaplar ve rapora ekler.
* **🇹🇷 Türkçe Karakter Zekası:** Gelişmiş Regex altyapısı ile Python'un Türkçe karakter (I/i, Ş/ş) körlüğünü aşar. "Arıtma", "İsale" gibi kelimeleri hatasız eşleştirir.
* **💾 Kusursuz Hafıza (Amnesia Proof):** Bulunan her ihalenin İKN'sini (İhale Kayıt Numarası) kaydeder. Aynı ihale asla ikinci kez Telegram'a düşmez.
* **☁️ %100 Bulut Otomasyonu:** GitHub Actions entegrasyonu sayesinde hiçbir fiziksel sunucuya veya açık bilgisayara ihtiyaç duymaz. Her sabah Türkiye saati ile belirlenen vakitte uyanır, görevini yapar ve kapanır.

---

## 🛠️ Kullanılan Teknolojiler

* **Python 3.10:** Temel programlama dili.
* **Cloudscraper:** EKAP'ın Cloudflare ve bot koruma güvenlik duvarlarını yasal sınırlar içinde aşmak için.
* **Requests:** Telegram Bot API ile kusursuz haberleşme.
* **Regex (re):** Karmaşık bütçe metinlerini ve ihale başlıklarını ayrıştırmak için.
* **GitHub Actions (CI/CD):** Zamanlanmış (Cron) görev yönetimi ve bulut sunucu altyapısı.

---

## ⚙️ Kurulum & Lokal Test

Projeyi kendi bilgisayarında test etmek istersen aşağıdaki adımları izleyebilirsin:

**1. Repoyu Klonla:**
```bash
git clone [https://github.com/KULLANICI_ADIN/hlc-epc-ihale-radari.git](https://github.com/KULLANICI_ADIN/hlc-epc-ihale-radari.git)
cd hlc-epc-ihale-radari
2. Gerekli Kütüphaneleri Yükle:

Bash
pip install -r requirements.txt
3. Çevre Değişkenlerini (Environment Variables) Ayarla:
Proje dizininde bir .env dosyası oluşturun ve Telegram kimlik bilgilerinizi girin:

Kod snippet'i
TELEGRAM_BOT_TOKEN=senin_bot_tokenin_buraya
ADMIN_CHAT_ID=senin_grup_id_numaran_buraya
4. Botu Ateşle:

Bash
python main.py
☁️ GitHub Actions İle Bulut Dağıtımı (Deployment)
Sistemin otomatik çalışması için .env dosyasındaki şifreleri GitHub repository'sine eklemeniz yeterlidir:

Deponuzda Settings > Secrets and variables > Actions yolunu izleyin.

TELEGRAM_BOT_TOKEN ve ADMIN_CHAT_ID anahtarlarını New repository secret olarak ekleyin.

Bot, .github/workflows/ekap_bot.yml dosyasındaki cron ayarına göre her gün otomatik olarak çalışacaktır. Dilerseniz Actions sekmesinden manuel olarak da tetikleyebilirsiniz.

📋 Örnek Telegram Çıktısı
Plaintext
⚡ YENİ EPC & ALTYAPI İHALESİ 💧

📌 İKN: 2026/123456
📅 Tarih: 15.04.2026
📋 İhale: 10.000 m3 Kapasiteli İleri Biyolojik Atıksu Arıtma Tesisi ve SCADA Otomasyonu
🏢 Kurum: X Büyükşehir Belediyesi Su ve Kanalizasyon İdaresi
🏗️ Tür / Usul: Yapım İşi | Açık İhale
💰 Yaklaşık Bütçe: 145.500.000,00 TL
⚖️ İtirazen Şikayet Başvuru Bedeli: 194.085 TL
⏰ Son Teklif: 15.04.2026 10:00

(Kopyalamak için İKN ve Tarih'in üzerine dokunun)
#HLC #EPC #Altyapı
Geliştirici Notu: Bu sistem, manuel ihale tarama süreçlerinde harcanan yüzlerce saatlik insan emeğini sıfıra indirmek ve şirket portföyüne en uygun projeleri "ilk duyan" olmak amacıyla yüksek mühendislik standartlarında tasarlanmıştır.
