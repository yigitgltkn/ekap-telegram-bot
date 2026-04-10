import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

EKAP_BASE_URL = "https://ekap.kik.gov.tr/EKAP/Ortak/IhaleArama/index.html"

# 1. OTOMASYON, SCADA VE ELEKTRİK (Kazandığınız ihaleler eklendi)
ANAHTAR_KELIMELER = [
    "SCADA", "Otomasyon", "RTU", "Telemetri", "Hidrolik Modelleme", "DMA", "Pano",
    "Soft Starter", "Yol Verici", "Frekans Konvertörü", "VFD", "Sürücü", "MCC Pano",
    "Debi Ölçüm", "İzleme Sistemi", "Basınç Yönetimi", "Kayıp-Kaçak"
]

# 2. GÜÇ SİSTEMLERİ VE MOTOR (Yeni uzmanlık alanlarınız)
GUC_VE_MOTOR_KELIMELERI = [
    "Transformatör", "Trafo", "Asenkron Motor", "OG Motor", "Yüksek Gerilim", 
    "Hücre Temini", "SF6 Gaz İzoleli", "Modüler Hücre", "Tevsiat", "TM Yapımı", 
    "Motor Sarım", "Motopomp", "Dikey Milli"
]

# 3. EPC VE ALTYAPI PROJELERİ
EPC_KELIMELERI = [
    "Arıtma Tesisi", "İsale Hattı", "Terfi Merkezi", "Su Deposu",
    "İçmesuyu Şebeke", "Kanalizasyon Şebeke", "Yağmursuyu", 
    "Biyolojik Arıtma", "Su Boru Hattı", "Altyapı Yapım", "Rehabilitasyonu"
]

# 4. YENİLENEBİLİR ENERJİ PROJELERİ (GES, RES, HES)
ENERJI_KELIMELERI = [
    "Güneş Enerjisi", "GES", "Rüzgar Enerjisi", "RES", 
    "Hidroelektrik", "HES", "Biyokütle", "Enerji Santrali", "Yenilenebilir Enerji"
]

# Botun arama yaparken kullanacağı ana liste
SEARCH_KEYWORDS = ANAHTAR_KELIMELER + GUC_VE_MOTOR_KELIMELERI + EPC_KELIMELERI + ENERJI_KELIMELERI

# --- NEGATIF KELIMELER (Kazandığınız ihaleleri elemeyecek şekilde esnetildi) ---
NEGATIF_KELIMELER = [
    # ❌ Sadece küçük sarf malzemeleri (Montaj ve büyük cihaz alımları hariç)
    "Yedek Parça", "Kırtasiye", "Klor", "Kimyasal", "Akaryakıt", "Lastik", 
    "Numune", "Yağ", "Çamur", "Yemek", "Personel Çalıştırılması",
    
    # ❌ Sadece Danışmanlık ve Çizim (Siz yapım ve montaj istiyorsunuz)
    "Projeleri Hazırlanması", "Projesi Hazırlanması", "Müşavirliği", "Müşavirlik", 
    "Danışmanlık", "Danışmanlığı", "Etüt", "Fizibilite",
    
    # ❌ Alakasız Sektörler
    "Laboratuvar", "Araç Kiralama", "Dezenfekte", "Kamera", "Güvenlik"
] 

DATABASE_PATH = "ihaleler.db"
CHECK_INTERVAL_MINUTES = 5
RECENT_CHECK_HOURS = 1
