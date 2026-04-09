import time
import re
from datetime import datetime
from config import SEARCH_KEYWORDS, NEGATIF_KELIMELER
from playwright.sync_api import sync_playwright

class EKAPAPI:
    def __init__(self):
        self.base_url = "https://ekapv2.kik.gov.tr/b_ihalearama/api/Ihale"
        self.search_keywords = SEARCH_KEYWORDS
        self.ihale_cache = {}  # İKN'leri aklında tutması için hafıza
        self.fiyat_cache = {}  # Gizli fiyatları aklında tutması için hafıza

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
                if deger >= 5000000:  # 5 MİLYON TL
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

    def _fiyat_formatla(self, deger):
        try:
            temiz = str(deger).replace('.', '').replace(',', '.').replace(' TL', '').strip()
            sayi = float(temiz)
            return f"{sayi:,.2f} TL".replace(',', 'X').replace('.', ',').replace('X', '.')
        except (ValueError, TypeError):
            return str(deger)

    # 🕵️‍♂️ POPUP DEDEKTİFİ: Tıklamayı simüle edip API'den dönen GetById isteğini havada yakalar
    def get_ihale_detail(self, ihale_id):
        ikn = self.ihale_cache.get(str(ihale_id))

        if not ikn or ikn == 'N/A':
            return {
                'son_teklif': 'Belirtilmemiş',
                'ihale_durumu': 'Sistemden Çekilemedi',
                'isin_yeri': 'Sistemden Çekilemedi',
                'ihale_yeri': 'Sistemden Çekilemedi'
            }
            
        print(f"\n🕵️‍♂️ [POPUP DEDEKTİFİ] {ikn} ihaleye tıklanıyor...")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(viewport={'width': 1920, 'height': 1080})
                page = context.new_page()
                
                # Siteye gir
                page.goto("https://ekapv2.kik.gov.tr/ekap/search", wait_until="domcontentloaded", timeout=60000)
                time.sleep(2)
                
                # Kutuya sadece o ihalenin İKN'sini yaz ve Enter'a bas
                search_input = page.locator("input[placeholder='Ara']:visible").first
                search_input.fill(ikn)
                
                with page.expect_response(lambda r: "GetListByParameters" in r.url, timeout=15000):
                    search_input.press("Enter")
                
                time.sleep(3) # Tablonun güncellenmesi için nefes
                
                # HEDEF: İlgili İKN'ye tıkla ve arka planda çalışan GetById isteğini yakala
                with page.expect_response(lambda r: "GetById" in r.url, timeout=15000) as detail_res_info:
                    page.locator(".dx-datagrid").get_by_text(ikn, exact=False).first.click(force=True)
                
                detail_response = detail_res_info.value
                if detail_response.status == 200:
                    detail = detail_response.json()
                    
                    # 🎉 Tıklamışken gizli bütçeyi de alıp hafızaya atıyoruz
                    detay_fiyat = detail.get('yaklasikMaliyet') or detail.get('yaklasikMaliyetTL') or detail.get('tahminiMaliyet')
                    if detay_fiyat:
                        self.fiyat_cache[str(ihale_id)] = self._fiyat_formatla(detay_fiyat)
                    
                    son_teklif = detail.get('teklifVermeGunSaat') or detail.get('ihaleTarihSaat') or 'Belirtilmemiş'
                    ihale_durumu = detail.get('ihaleDurum') or detail.get('ihaleDurumu') or detail.get('ihaleDurumuAciklama') or 'Sistemde Görünmüyor'
                    isin_yeri = detail.get('isinYapilacagiYer') or detail.get('isYapilacagiYer') or 'Sistemde Görünmüyor'
                    ihale_yeri = detail.get('ihaleYeri') or detail.get('ihaleninYapilacagiYer') or 'Sistemde Görünmüyor'
                    
                    browser.close()
                    print(f"✅ Popup verileri çalındı: {ikn}")
                    return {
                        'son_teklif': str(son_teklif),
                        'ihale_durumu': str(ihale_durumu),
                        'isin_yeri': str(isin_yeri),
                        'ihale_yeri': str(ihale_yeri)
                    }
                else:
                    print(f"⚠️ Popup Hatası: {detail_response.status}")
                browser.close()
                
        except Exception as e:
            print(f"❌ Tıklama Hatası ({ikn}): {e}")
            
        return {
            'son_teklif': 'Belirtilmemiş',
            'ihale_durumu': 'Sistemden Çekilemedi',
            'isin_yeri': 'Sistemden Çekilemedi',
            'ihale_yeri': 'Sistemden Çekilemedi'
        }

    def get_ihale_fiyat(self, ihale_id, liste_fiyati):
        if liste_fiyati and str(liste_fiyati) not in ('', 'None', 'Sistemde Görünmüyor'):
            return self._fiyat_formatla(liste_fiyati)
            
        if str(ihale_id) in self.fiyat_cache:
            return self.fiyat_cache[str(ihale_id)]
            
        return 'Sistemde Görünmüyor'

    # ANA ARAMA MOTORU
    def search_ihaleler(self):
        all_results = []
        print("\n🤖 Hayalet Tarayıcı (Playwright) Başlatılıyor...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            try:
                print("🌐 EKAP Arama Sayfasına Giriliyor...")
                page.goto("https://ekapv2.kik.gov.tr/ekap/search", wait_until="domcontentloaded", timeout=60000)
                time.sleep(2)
            except Exception as e:
                print(f"❌ EKAP sitesine ulaşılamadı: {e}")
                browser.close()
                return []

            for kw in self.search_keywords:
                print(f"\n🔍 Taranıyor: {kw}")
                try:
                    search_input = page.locator("input[placeholder='Ara']:visible").first
                    search_input.fill(kw)

                    with page.expect_response(lambda response: "GetListByParameters" in response.url, timeout=15000) as response_info:
                        search_input.press("Enter")

                    response = response_info.value
                    if response.status == 200:
                        data = response.json()
                        total = data.get('totalCount', 'Bilinmiyor')
                        print(f"🕵️ [{kw}] Toplam {total} ihale var.")
                        results = self.parse_api_response(data, kw)
                        all_results.extend(results)
                    else:
                        print(f"⚠️ [{kw}] Hata: {response.status}")

                except Exception as e:
                    print(f"❌ [{kw}] Aranırken zaman aşımı: {e}")
                    page.reload(wait_until="domcontentloaded", timeout=60000)
                    time.sleep(2)

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
                else:
                    ihale_tarihi = bugun
                
                if ihale_tarihi < bugun:
                    continue
            except Exception:
                pass

            ikn = item.get('ikn', 'N/A')
            ihale_id = str(item.get('id', ''))
            
            # HAFIZAYA KAYIT: Popup dedektifi için İKN'leri kaydediyoruz!
            if ihale_id and ikn != 'N/A':
                self.ihale_cache[ihale_id] = ikn

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
