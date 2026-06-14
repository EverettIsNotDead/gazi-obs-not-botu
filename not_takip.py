import time
import json
import os
import re
import platform
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Ayarlar
LOGIN_URL = 'https://obs.gazi.edu.tr/oibs/std/login.aspx'
URL = 'https://obs.gazi.edu.tr/oibs/std/not_listesi_op.aspx'
DATA_FILE = 'notlar_durumu.json'

# Varsayılan süre
KONTROL_PERIYODU = 60  

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://obs.gazi.edu.tr/oibs/std/index.aspx?curOp=0',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'iframe',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
}

# Dinamik olarak doldurulacak çerezler
COOKIES = {}

def periyot_ayarini_al():
    while True:
        try:
            print("\n" + "-"*40)
            girdi = input("Notlar kaç saniyede bir kontrol edilsin? (60 veya daha yüksek önerilir): ").strip()
            süre = int(girdi)
            
            if süre <= 0:
                print("HATA: Süre 0 veya daha küçük olamaz.")
                continue
                
            if süre < 60:
                print("\n[Dikkat]")
                print("60 saniyenin altındaki süreler OBS sisteminin bot korumasına")
                print("takılmanıza neden olabilir!")
                
                onay = input("Riskleri kabul edip devam etmek istiyor musunuz? (e/h): ").strip().lower()
                if onay in ['e', 'evet', 'y', 'yes']:
                    return süre
                else:
                    print("İşlem iptal edildi. Daha kısa bir süre girin.")
                    continue
            return süre
        except ValueError:
            print("HATA: Lütfen sadece tam sayı bir değer girin.")

def tarayicidan_cerezleri_al():
    print("\nTarayıcı başlatılıyor... Lütfen açılan pencereden giriş yapın.")
    print("Giriş yapıp sisteme ulaştığınızda bu pencere otomatik kapanacaktır.")
    
    global COOKIES
    with sync_playwright() as p:
        # tarayıcı algılama
        tarayici_tipleri = [
            {"name": "chromium", "channel": "chrome"},
            {"name": "chromium", "channel": "msedge"},
            {"name": "firefox", "channel": None},
            {"name": "chromium", "channel": None}
        ]
        
        browser = None
        for t in tarayici_tipleri:
            try:
                launch_args = {"headless": False}
                if t["channel"]:
                    launch_args["channel"] = t["channel"]
                
                browser = getattr(p, t["name"]).launch(**launch_args)
                break
            except Exception:
                continue
                
        if not browser:
            print("Uygun bir tarayıcı motoru bulunamadı. Lütfen 'playwright install' komutunu çalıştırıp tarayıcı motorlarını indirin.")
            return False

        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.goto(LOGIN_URL)

        giris_basarili = False
        timeout_sayaci = 0
        
        # Giriş bekleme
        while timeout_sayaci < 300:
            try:
                playwright_cookies = context.cookies()
                gecici_cookies = {c['name']: c['value'] for c in playwright_cookies}
                mevcut_url = page.url
                
                # Giriş başarılıysa
                if "ASP.NET_SessionId" in gecici_cookies and "login.aspx" not in mevcut_url:
                    # Çerezlerin oturması için bekleme suresi ekldim
                    time.sleep(3)
                    
                    playwright_cookies = context.cookies()
                    COOKIES = {c['name']: c['value'] for c in playwright_cookies}
                    HEADERS['User-Agent'] = page.evaluate("navigator.userAgent")
                    
                    print("Oturum çerezleri alındı, kontrole başlanıyor.")
                    giris_basarili = True
                    break
            except Exception as e:
                print(f"Tarayıcı kapatıldı veya beklenmeyen bir durum oluştu: {e}")
                break
                
            time.sleep(1)
            timeout_sayaci += 1

        browser.close()
        return giris_basarili

def ses_cal():
    print("\a")  # Standart terminal zili
    sistem = platform.system()
    try:
        if sistem == "Windows":
            import winsound
            winsound.Beep(1000, 1000)
        elif sistem == "Darwin":  # macOS darwin olarak geciyomus, oyle de bir bilgi
            os.system("say 'Yeni not açıklandı' &")
            os.system("afplay /System/Library/Sounds/Glass.aiff &")
        elif sistem == "Linux":
            os.system("paplay /usr/share/sounds/gnome/default/alerts/glass.ogg &> /dev/null &")
    except Exception:
        pass

def notlari_ayristir(html_icerik):
    soup = BeautifulSoup(html_icerik, 'html.parser')
    notlar_sozlugu = {}
    
    ders_kodlari = soup.find_all('span', id=re.compile(r'^grd_not_listesi_lblDersKod_'))
    
    for span in ders_kodlari:
        tr = span.find_parent('tr')
        if not tr:
            continue
            
        tds = tr.find_all('td')
        if len(tds) >= 5:
            ders_kodu = tds[1].get_text(strip=True)
            ders_adi = tds[2].get_text(strip=True)
            durum = tds[3].get_text(strip=True)
            
            notlar_text = tds[4].get_text(" ", strip=True)
            notlar_text = re.sub(r'\s+', ' ', notlar_text.replace('\xa0', ' ')).strip()
            
            notlar_sozlugu[ders_kodu] = {
                "ders_adi": ders_adi,
                "durum": durum,
                "notlar": notlar_text
            }
            
    return notlar_sozlugu

def verileri_yukle():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def verileri_kaydet(veriler):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(veriler, f, ensure_ascii=False, indent=4)

def degisiklik_kontrol_et(eski, yeni):
    degisim_var = False
    
    for ders_kodu, yeni_veri in yeni.items():
        if ders_kodu not in eski:
            print(f"\n[Yeni Ders ALgılandı] {ders_kodu} - {yeni_veri['ders_adi']}")
            print(f"   Durum: {yeni_veri['durum']} | Notlar: {yeni_veri['notlar']}")
            degisim_var = True
        else:
            eski_veri = eski[ders_kodu]
            baslik_basildi = False
            
            def baslik_goster():
                nonlocal baslik_basildi
                if not baslik_basildi:
                    print(f"\n[Değişim Algılandı] {ders_kodu} - {yeni_veri['ders_adi']}")
                    baslik_basildi = True

            if eski_veri['durum'] != yeni_veri['durum']:
                baslik_goster()
                print(f"   Durum Değişimi: {eski_veri['durum']} ➔  {yeni_veri['durum']}")
                degisim_var = True
                
            if eski_veri['notlar'] != yeni_veri['notlar']:
                baslik_goster()
                print(f"   Not Değişimi: {eski_veri['notlar']} ➔  {yeni_veri['notlar']}")
                degisim_var = True
                
    return degisim_var

def ana_dongu():
    global KONTROL_PERIYODU
    
    print("="*60)
    print(" Gazi Üniversitesi OBS Not Takip Yazılımı (Abdulkadir Ustaoğlu tarafından) ")
    print("="*60)
    
    KONTROL_PERIYODU = periyot_ayarini_al()
    
    print("\n" + "="*60)
    print(f"Sistem Başlatıldı. Kontrol periyodu: {KONTROL_PERIYODU} saniye.")
    print("="*60)
    
    # Tarayıcı acma
    if not tarayicidan_cerezleri_al():
        print("Giriş başarısız oldu veya tarayıcı kapatıldı. Program sonlandırılıyor.")
        return
    
    while True:
        zaman_damgasi = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            response = requests.get(URL, headers=HEADERS, cookies=COOKIES, timeout=15)
            
            # Oturum kontrolü
            if response.status_code != 200 or "login.aspx" in response.url or "Giriş" in response.text:
                print(f"[{zaman_damgasi}] Oturumunuz sonlandı, başka bir yerden giriş yapmış olabilirsiniz. Yeniden giriş penceresi açılıyor...")
                if not tarayicidan_cerezleri_al():
                    print(f"Giriş yenilenemedi, {KONTROL_PERIYODU} saniye sonra tekrar denenecek.")
                    time.sleep(KONTROL_PERIYODU)
                    continue
                else:
                    response = requests.get(URL, headers=HEADERS, cookies=COOKIES, timeout=15)

            guncel_notlar = notlari_ayristir(response.text)
            
            if not guncel_notlar:
                print(f"[{zaman_damgasi}] Not listesi sayfasından veri ayrıştırılamadı. Oturum tazeleniyor...")
                tarayicidan_cerezleri_al()
                continue
                
            eski_notlar = verileri_yukle()
            
            if not eski_notlar:
                print(f"[{zaman_damgasi}] İlk tarama başarılı. Mevcut notlar kaydedildi. Takip ediliyor...")
                verileri_kaydet(guncel_notlar)
            else:
                if degisiklik_kontrol_et(eski_notlar, guncel_notlar):
                    ses_cal()
                    verileri_kaydet(guncel_notlar)
                else:
                    print(f"[{zaman_damgasi}] Notlar Kontrol edildi: Değişiklik yok.")
                    
        except requests.exceptions.RequestException as e:
            print(f"[{zaman_damgasi}] Bağlantı hatası oluştu (OBS yanıt vermiyor olabilir). Hata: {e}")
            
        time.sleep(KONTROL_PERIYODU)

if __name__ == '__main__':
    ana_dongu()
