import cloudscraper
import time
import re
from datetime import datetime, timedelta
from config import SEARCH_KEYWORDS, NEGATIF_KELIMELER
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EKAPAPI:
    def __init__(self):
        self.base_url = "https://ekapv2.kik.gov.tr/b_ihalearama/api/Ihale"
        self.search_keywords = SEARCH_KEYWORDS
        self.session = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        self.session.headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Origin': 'https://ekapv2.kik.gov.tr',
            'Referer': 'https://ekapv2.kik.gov.tr/ekap/search'
        })

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
                if deger >= 5000000: # 5 MİLYON TL
                    gecerli_butce_var_mi = True
                    break
            except ValueError:
                continue

        if sayi_bulundu and not gecerli_butce_var_mi: return False, False
        if gecerli_butce_var_mi: return True, True
        return True, False

    def itirazen_sikayet_bedeli(self, maliyet_metni):
        try:
            temiz = str(maliyet_metni).replace('.', '').replace(',', '.').replace(' TL', '').strip()
            deger = float(temiz)
            if deger <= 0: return "Geçersiz Bütçe"
            elif deger <= 10_785_492: return "64.652 TL"
            elif deger <= 43_142_132: return "129.385 TL"
            elif deger <= 323_566_103: return "194.085 TL"
            else: return "258.810 TL"
        except (ValueError, TypeError):
            return "Hesaplanamadı"

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

    def get_ihale_detail(self, ihale_id):
        try:
            url = f"{self.base_url}/GetById/{ihale_id}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json().get('teklifVermeGunSaat') or 'Belirtilmemiş'
        except Exception: pass
        return 'Belirtilmemiş'

    def get_ihale_fiyat(self, ihale_id, liste_fiyati):
        if liste_fiyati and str(liste_fiyati) not in ('', 'None', 'Sistemde Görünmüyor'):
            return self._fiyat_formatla(liste_fiyati)
        try:
            url = f"{self.base_url}/GetById/{ihale_id}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                detail = response.json()
                detay_fiyat = detail.get('yaklasikMaliyet') or detail.get('yaklasikMaliyetTL') or detail.get('tahminiMaliyet')
                if detay_fiyat: return self._fiyat_formatla(detay_fiyat)
        except Exception: pass
        return 'Sistemde Görünmüyor'

    def _fiyat_formatla(self, deger):
        try:
            temiz = str(deger).replace('.', '').replace(',', '.').replace(' TL', '').strip()
            sayi = float(temiz)
            return f"{sayi:,.2f} TL".replace(',', 'X').replace('.', ',').replace('X', '.')
        except (ValueError, TypeError):
            return str(deger)

    def search_ihaleler_api(self, keyword=""):
        try:
            # -1 HATASININ ÇÖZÜMÜ: API'nin istediği güncel tarih formatını geri koyduk.
            bugun_str = datetime.now().strftime("%Y-%m-%dT00:00:00")
            search_payload = {
                "searchText": keyword,
                "filterType": None,
                "ikNdeAra": True,
                "ihaleAdindaAra": True,
                "searchType": "GirdigimGibi",
                "paginationSkip": 0,
                "paginationTake": 100,
                "ihaleTarihiBaslangic": bugun_str,
                "ihaleTarihBaslangic": bugun_str
            }
            response = self.session.post(
                f"{self.base_url}/GetListByParameters",
                json=search_payload,
                timeout=20
            )
            if response.status_code == 200:
                data = response.json()
                return self.parse_api_response(data, keyword)
            return []
        except Exception:
            return []

    def search_ihaleler(self):
        all_results = []
        for kw in self.search_keywords:
            print(f"🔍 Taranıyor: {kw}")
            results = self.search_ihaleler_api(kw)
            all_results.extend(results)
            time.sleep(1)

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
            
            # --- GEÇMİŞ TARİH FİLTRESİ (ESKİLERİ ÇÖPE ATAR) ---
            try:
                if 'T' in raw_tarih:
                    ihale_tarihi = datetime.strptime(raw_tarih.split('T')[0], "%Y-%m-%d")
                elif ' ' in raw_tarih:
                    ihale_tarihi = datetime.strptime(raw_tarih.split(' ')[0], "%d.%m.%Y")
                else:
                    ihale_tarihi = bugun
                
                # İhale tarihi bugünden daha eskiyse, listeye eklemeden atla!
                if ihale_tarihi < bugun:
                    continue
            except Exception:
                pass
            # --------------------------------------------------

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
                'ihale_no': ikn,
                'ihale_adi': ihale_adi,
                'kurum': item.get('idareAdi', 'N/A'),
                'ihale_tarihi': raw_tarih.replace('T', ' ')[:16] if 'T' in raw_tarih else raw_tarih,
                'ihale_url': guvenli_url,
                'ihale_id': str(item.get('id', '')),
                'ihale_tutari': item.get('yaklasikMaliyet', ''),
                'ihale_turu': tur_adi,
                'ihale_usulu': usul_adi,
                'aranan_kelime': keyword
            })

        return ihaleler
        ihaleler = []
        if 'list' not in data: return ihaleler

        for item in data['list']:
            raw_tarih = item.get('ihaleTarihSaat', '')
            
            # SESSİZ KATİL İMHA EDİLDİ! 
            # (Burada "tarih geçmişse atla" diyen kod vardı, onu tamamen sildik. Artık EKAP'tan gelen her şey havuza girecek)

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
                'ihale_no': ikn,
                'ihale_adi': ihale_adi,
                'kurum': item.get('idareAdi', 'N/A'),
                'ihale_tarihi': raw_tarih.replace('T', ' ')[:16] if 'T' in raw_tarih else raw_tarih,
                'ihale_url': guvenli_url,
                'ihale_id': str(item.get('id', '')),
                'ihale_tutari': item.get('yaklasikMaliyet', ''),
                'ihale_turu': tur_adi,
                'ihale_usulu': usul_adi,
                'aranan_kelime': keyword
            })

        return ihaleler