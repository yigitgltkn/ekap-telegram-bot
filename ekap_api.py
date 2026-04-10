import time
import re
from datetime import datetime
from config import SEARCH_KEYWORDS, NEGATIF_KELIMELER
from playwright.sync_api import sync_playwright

class EKAPAPI:
    def __init__(self):
        self.base_url = "https://ekapv2.kik.gov.tr/b_ihalearama/api/Ihale"
        self.search_keywords = SEARCH_KEYWORDS

    def turkce_buyut(self, metin):
        if not metin: return ""
        return metin.replace('i', 'İ').replace('ı', 'I').replace('ş', 'Ş').replace('ğ', 'Ğ').replace('ü', 'Ü').replace('ö', 'Ö').replace('ç', 'Ç').upper()

    def butce_uygun_mu(self, maliyet_metni):
        maliyet_metni = str(maliyet_metni) if maliyet_metni else ''
        if not maliyet_metni or maliyet_metni in ('N/A', 'None', 'Sistemde Görünmüyor'):
            return True, False

        kucuk_is_terimleri = ['ALTINDA', 'YARISINA KADAR']
        maliyet_buyuk = self.turkce_buyut(maliyet_metni)
        
        for terim in kucuk_is_terimleri:
            if terim in maliyet_buyuk: return False, False

        sayilar = re.findall(r'\d{1,3}(?:\.\d{3})*(?:,\d+)?', maliyet_metni)
        gecerli_butce_var_mi = False
        sayi_bulundu = False

        for s in sayilar:
            if len(s.replace('.', '').replace(',', '')) < 4: continue
            sayi_bulundu = True
            temiz_sayi = s.replace('.', '').replace(',', '.')
            try:
                deger = float(temiz_sayi)
                if deger >= 5000000:  
                    gecerli_butce_var_mi = True
                    break
            except ValueError:
                continue

        if sayi_bulundu and not gecerli_butce_var_mi: return False, False
        if gecerli_butce_var_mi: return True, True
        return True, False

    def filter_ozel_ihaleler(self, ihaleler):
        filtered = []
        for ihale in ihaleler:
            ihale_adi = ihale.get('ihale_adi', '')
            maliyet = ihale.get('ihale_tutari', '')
            aranan_kelime = ihale.get('aranan_kelime', '')
            
            adi_buyuk = self.turkce_buyut(ihale_adi)
            aranan_buyuk = self.turkce_buyut(aranan_kelime)
            ihale_turu = self.turkce_buyut(str(ihale.get('ihale_turu', '')))
            ihale_usulu = self.turkce_buyut(str(ihale.get('ihale_usulu', '')))

            if "21/F" in ihale_usulu or "DOĞRUDAN" in ihale_usulu: continue

            kara_liste_uygun = False
            for negatif in NEGATIF_KELIMELER:
                if self.turkce_buyut(negatif) in adi_buyuk:
                    kara_liste_uygun = True
                    break
            if kara_liste_uygun: continue

            butce_gecerli, acikca_buyuk_mu = self.butce_uygun_mu(maliyet)
            if not butce_gecerli: continue

            if "MAL" in ihale_turu or "HİZMET" in ihale_turu:
                if not acikca_buyuk_mu: continue

            if aranan_kelime.isdigit():
                kelime_uygun = True
            else:
                kelime_uygun = bool(re.search(rf'(?:\W|^){re.escape(aranan_buyuk)}(?:\W|$)', adi_buyuk))

            if not kelime_uygun: continue
            filtered.append(ihale)
        return filtered

    def search_ihaleler(self):
        all_results = []
        print("\n🤖 Basit Tarayıcı Başlatılıyor (Sadece Ana Liste)...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0"
            )
            page = context.new_page()

            for kw in self.search_keywords:
                print(f"\n🔍 Taranıyor: {kw}")
                basari = False
                deneme_sayisi = 0
                
                while not basari and deneme_sayisi < 3:
                    try:
                        deneme_sayisi += 1
                        page.goto("https://ekapv2.kik.gov.tr/ekap/search", wait_until="domcontentloaded", timeout=60000)
                        page.wait_for_timeout(2000) 

                        search_input = page.locator("input[placeholder='Ara']:visible").first
                        search_input.clear()
                        search_input.press_sequentially(kw, delay=150) 
                        
                        with page.expect_response(lambda response: "GetListByParameters" in response.url, timeout=20000) as response_info:
                            search_input.press("Enter")
                            page.wait_for_timeout(1000) 

                        response = response_info.value
                        if response.status == 200:
                            data = response.json()
                            total = data.get('totalCount', 'Bilinmiyor')
                            print(f"🕵️ [{kw}] Toplam {total} ihale var.")
                            results = self.parse_api_response(data, kw)
                            all_results.extend(results)
                            basari = True 
                        else:
                            print(f"⚠️ [{kw}] Hata: {response.status}")
                            basari = True 

                    except Exception as e:
                        print(f"❌ [{kw}] Zaman aşımı. Tekrar deneniyor... ({deneme_sayisi}/3)")
                        page.wait_for_timeout(3000)

            browser.close()

        unique = []
        seen = set()
        for i in all_results:
            uid = i['ihale_no'] if i['ihale_no'] != 'N/A' else i['ihale_id']
            if uid not in seen:
                unique.append(i)
                seen.add(uid)
        return unique

    def parse_api_response(self, data, keyword):
        ihaleler = []
        bugun = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if 'list' not in data: return ihaleler

        for item in data['list']:
            raw_tarih = item.get('ihaleTarihSaat', '')
            try:
                if 'T' in raw_tarih:
                    ihale_tarihi = datetime.strptime(raw_tarih.split('T')[0], "%Y-%m-%d")
                elif ' ' in raw_tarih:
                    ihale_tarihi = datetime.strptime(raw_tarih.split(' ')[0], "%d.%m.%Y")
                else: ihale_tarihi = bugun
                if ihale_tarihi < bugun: continue
            except Exception: pass

            ikn = item.get('ikn', 'N/A')
            ihale_adi = item.get('ihaleAdi', 'N/A')
            guvenli_url = "https://ekapv2.kik.gov.tr/ekap/search"

            turu_kodu = str(item.get('ihaleTuru', ''))
            if turu_kodu == '1': tur_adi = "Mal Alımı"
            elif turu_kodu == '2': tur_adi = "Hizmet Alımı"
            elif turu_kodu == '3': tur_adi = "Yapım İşi"
            elif turu_kodu == '4': tur_adi = "Danışmanlık"
            else:
                adi_buyuk = self.turkce_buyut(ihale_adi)
                if any(k in adi_buyuk for k in ["YAPIM", "İNŞAAT", "TESİSİ", "İKMAL"]): tur_adi = "Yapım İşi (Tahmini)"
                elif any(k in adi_buyuk for k in ["ALIMI", "MALZEME"]): tur_adi = "Mal Alımı (Tahmini)"
                else: tur_adi = item.get('ihaleTuruAciklama', 'Belirtilmemiş')

            usul_adi = item.get('ihaleUsulAciklama') or item.get('ihaleUsul', 'Belirtilmemiş')
            if "OPEN" in self.turkce_buyut(usul_adi): usul_adi = "Açık İhale"

            ihaleler.append({
                'ihale_no': ikn, 'ihale_adi': ihale_adi, 'kurum': item.get('idareAdi', 'N/A'),
                'ihale_tarihi': raw_tarih.replace('T', ' ')[:16] if 'T' in raw_tarih else raw_tarih,
                'ihale_url': guvenli_url, 'ihale_id': str(item.get('id', '')),
                'ihale_tutari': item.get('yaklasikMaliyet', ''), 'ihale_turu': tur_adi,
                'ihale_usulu': usul_adi, 'aranan_kelime': keyword
            })
        return ihaleler
