# 💧 HLC EPC Tender Intelligence
> **An Advanced Automated Procurement Tracking System for EPC & Industrial Automation**

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Automated-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot_API-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

**HLC EPC Tender Intelligence**, EKAP (Elektronik Kamu Alımları Platformu) üzerindeki devasa veri yığınını gerçek zamanlı olarak tarayan, **GES, RES, HES, SCADA ve Altyapı** gibi yüksek bütçeli EPC projelerini ayıklayan profesyonel bir otomasyon çözümüdür.

## 🎯 Proje Vizyonu

Standart botların aksine, bu sistem EKAP'ın modern Angular altyapısını ve SSL güvenlik duvarlarını aşmak için optimize edilmiştir.

| Özellik | Açıklama |
| :--- | :--- |
| **🔍 Multi-Vector Search** | SCADA, Otomasyon, GES, RES gibi anahtar kelimelerle çapraz tarama. |
| **🛡️ Smart Filtering** | EPC dışı işlerin (Danışmanlık, küçük malzeme alımı vb.) otomatik eliminasyonu. |
| **🚀 Direct Data Extraction** | Sayfa yükleme derdi olmadan, saf veri çekme hızı. |
| **📱 Telegram Dashboard** | İKN, Tarih ve Kurum bilgilerini Telegram üzerinden interaktif linklerle sunma. |
| **🧠 Intelligent Memory** | Gönderilen ihaleleri asla tekrar göndermeyen yerel veritabanı. |

## 🛠️ Kurulum Rehberi

### 1. Ortamı Hazırlayın
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Paketleri yükleyin:
pip install requests python-dotenv playwright
playwright install chromium

TELEGRAM_BOT_TOKEN=123456789:ABCDEF...
ADMIN_CHAT_ID=-100123456789

python main.py
---

### 4. Bölüm: Mimari ve Akış (Interactive Section)
```markdown
## ⚙️ Akıllı Filtreleme Sistemi

Sistem, `config.py` üzerinden yönetilen iki katmanlı bir filtre kullanır:

1. **Pozitif Filtre:** Belirlenen EPC sektörlerine (Enerji, Su, Otomasyon) odaklanır.
2. **Negatif Filtre (Blacklist):** "Bakım", "Onarım", "Malzeme Alımı", "Müşavirlik" gibi EPC kapsamı dışındaki işleri otomatik olarak eler.

```python
# Örnek Sektör Ekleme:
ENERJI_KELIMELERI = ["Güneş Enerjisi", "GES", "RES", "HES"]

## 🗺️ Gelecek Planları (Roadmap)

- [x] API tabanlı hızlı veri çekme motoru.
- [x] SSL/TLS handshake sorunlarının çözümü.
- [ ] **AI-Powered Analysis:** İhale dökümanlarını (PDF) okuyup teknik yeterlilik analizi yapma.
- [ ] **Web Dashboard:** Geçmiş ihalelerin grafiksel analizi.

---

## 🤝 Katkıda Bulunma

Bu bir EPC otomasyon çözümüdür. Katkılarınızı (Pull Request) her zaman bekliyoruz!

---
**HLC EPC Automation Team** 🚀
