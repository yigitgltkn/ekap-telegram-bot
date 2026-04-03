import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from ekap_api import EKAPAPI

def main():
    print("🖥️ HLC EPC İhale Servisi Başlatılıyor...")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(BASE_DIR, '.env')
    sent_file = os.path.join(BASE_DIR, "local_sent_ihales.txt")

    load_dotenv(env_path)

    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ HATA: TELEGRAM_BOT_TOKEN bulunamadı!")
        return

    try:
        GROUP_ID = int(os.environ.get('ADMIN_CHAT_ID'))
    except (TypeError, ValueError):
        print("❌ HATA: ADMIN_CHAT_ID bulunamadı veya geçersiz!")
        return

    # Hafızayı Yükle
    if not os.path.exists(sent_file):
        with open(sent_file, 'a', encoding='utf-8'): pass

    with open(sent_file, 'r', encoding='utf-8') as f:
        sent_ihales = {line.strip() for line in f if line.strip()}

    ekap_api = EKAPAPI()
    print(f"\n🔍 [{datetime.now().strftime('%H:%M:%S')}] İhaleler kontrol ediliyor...")

    try:
        ham_ihaleler = ekap_api.search_ihaleler()
        print(f"\n📊 AŞAMA 1 (Son 7 Gün Tarama): EKAP'tan toplam {len(ham_ihaleler)} adet ham ihale çekildi.")

        real_ihaleler = ekap_api.filter_ozel_ihaleler(ham_ihaleler)
        print(f"📊 AŞAMA 2 (EPC Filtresi): Filtrelerden sonra elde {len(real_ihaleler)} adet ihale kaldı.\n")

        yeni_bulunan_sayisi = 0

        for ihale in real_ihaleler:
            ikn = str(ihale['ihale_no']).strip()

            if ikn in sent_ihales:
                print(f"⏭️ Zaten gönderilmiş, atlanıyor: {ikn}")
                continue

            yeni_bulunan_sayisi += 1
            print(f"✅ YENİ İHALE BULUNDU: {ikn}")

            raw_tarih = ihale.get('ihale_tarihi', '')
            sadece_tarih = raw_tarih[:10] if raw_tarih else 'Belirtilmemiş'

            # Son Teklif ve Fiyatı Güvenli Çek
            try:
                son_teklif = ekap_api.get_ihale_detail(ihale['ihale_id'])
            except Exception:
                son_teklif = 'Belirtilmemiş'

            try:
                yaklasik_maliyet = ekap_api.get_ihale_fiyat(ihale['ihale_id'], ihale['ihale_tutari'])
            except Exception:
                yaklasik_maliyet = 'Sistemde Görünmüyor'

            # KİK Şikayet Bedeli
            sikayet_bedeli = ekap_api.itirazen_sikayet_bedeli(yaklasik_maliyet)

            msg = (
                "<b>⚡ YENİ EPC & ALTYAPI İHALESİ</b> 💧\n\n"
                f"<b>📌 İKN:</b> <code>{ihale['ihale_no']}</code>\n"
                f"<b>📅 Tarih:</b> <code>{sadece_tarih}</code>\n"
                f"<b>📋 İhale:</b> {ihale['ihale_adi']}\n"
                f"<b>🏢 Kurum:</b> {ihale['kurum']}\n"
                f"<b>🏗️ Tür / Usul:</b> {ihale['ihale_turu']} | {ihale['ihale_usulu']}\n"
                f"<b>💰 Yaklaşık Bütçe:</b> {yaklasik_maliyet}\n"
                f"<b>⚖️ İtirazen Şikayet Başvuru Bedeli:</b> {sikayet_bedeli}\n"
                f"<b>⏰ Son Teklif:</b> {son_teklif}\n\n"
                "<i>(Kopyalamak için İKN ve Tarih'in üzerine dokunun)</i>\n"
                "#HLC #EPC #Altyapı"
            )

            try:
                telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                payload = {
                    "chat_id": GROUP_ID,
                    "text": msg,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                    "reply_markup": {
                        "inline_keyboard": [[
                            {"text": "🔗 EKAP Arama Sayfasına Git", "url": ihale['ihale_url']}
                        ]]
                    }
                }

                response = requests.post(telegram_url, json=payload, timeout=10)

                if response.status_code == 200:
                    with open(sent_file, 'a', encoding='utf-8') as f:
                        f.write(f"{ikn}\n")
                    sent_ihales.add(ikn)
                    print(f"💾 {ikn} hafızaya eklendi ve Telegram'a atıldı.")
                else:
                    print(f"⚠️ Telegram hatası ({ikn}): {response.status_code}")

            except Exception as e:
                print(f"❌ Gönderim hatası ({ikn}): {e}")

        print(f"\n✅ İşlem başarıyla tamamlandı. {yeni_bulunan_sayisi} yeni ihale bildirildi.")

    except Exception as e:
        print(f"❌ Kritik hata: {e}")

if __name__ == "__main__":
    main()