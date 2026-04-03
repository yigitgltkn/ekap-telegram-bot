import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

EKAP_BASE_URL = "https://ekap.kik.gov.tr/EKAP/Ortak/IhaleArama/index.html"

# 1. Klasik Otomasyon Kelimeleri (Pano, RTU, Yazılım işleri)
ANAHTAR_KELIMELER = [
    "SCADA", "Otomasyon", "RTU", "Telemetri", "Hidrolik Modelleme", "DMA"
]

# 2. Dev EPC Projeleri (Arıtma, Altyapı, Tesis Kurulumu)
EPC_KELIMELERI = [
    "Arıtma", "İsale Hattı", "Terfi Merkezi", "Su Deposu"
]

# 3. KİK Resmi CPV Kodları (Başlıkta geçmese bile içeriğinden yakalar)
CPV_KODLARI = [
    "45232100", # Su boru hattı yapım işleri
    "45252127", # Atık su arıtma tesisi yapım işleri
    "45252100", # Kanalizasyon arıtma tesisi yapım işleri
    "71320000"  # Mühendislik tasarım hizmetleri (Modelleme)
]

# Botun arama yaparken kullanacağı ana liste
SEARCH_KEYWORDS = ANAHTAR_KELIMELER + EPC_KELIMELERI + CPV_KODLARI

# --- HLC EPC KARA LİSTESİ (KÜÇÜK İŞLERİ ELER) ---
NEGATIF_KELIMELER = [
    "Malzemeleri", "Malzemesi", "Yedek Parça", "Sarf", 
    "Laboratuvar", "Kamera", "Güvenlik", "Kırtasiye", 
    "Araç Kiralama", "Dezenfekte", "Temiz", "Temizlik", "Klor", "Kimyasal",
    "Akaryakıt", "Lastik", "Bakım ve Onarım", "Numune", "Yağ", "Projeleri Hazırlanması", "Müşavirliği", "Çamur", "Ölçüm Cihazları"
]

DATABASE_PATH = "ihaleler.db"
CHECK_INTERVAL_MINUTES = 5
RECENT_CHECK_HOURS = 1