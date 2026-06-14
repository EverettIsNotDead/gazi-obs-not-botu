# Gazi Üniversitesi OBS Not Takip Scripti

Bu script Gazi Üniversitesi OBS sistemini belirlediğiniz saniye aralıklarıyla kontrol eder. Sistemde bir not/harf durumu değiştiğinde size **sesli uyarı** verir ve **terminalde gösterir**. F5 tuşunu eskitmekten kurtarır.

## Kurulum

Scripti çalıştırmak için bilgisayarınızda **Python** kurulu olmalıdır.

1. Bu projeyi bilgisayarınıza indirin.

2. Terminali (veya Komut İstemini) açın ve projenin bulunduğu klasöre gidin.

3. Gerekli Python kütüphanelerini kurmak için şu komutu çalıştırın:

   ```
   pip install -r requirements.txt
   ```

4. Tarayıcı motorlarını indirin:

   ```
   playwright install
   ```

## Kullanım

1. Yazılımı başlatın:

   ```
   python not_takip.py
   ```

   ya da (kullandığınız sürüme göre)

   ```
   python3 not_takip.py
   ```

2. Program size notların kaç saniyede bir kontrol edileceğini soracak. (Tavsiye edilen: 60 saniye. Daha altı süreler OBS tarafından bot olarak algılanıp ban yemenize sebep olabilir).

3. Süreyi girdikten sonra ekranda otomatik olarak bir tarayıcı açılır, bilgilerinizi girerek sisteme giriş yapın.

4. Yazılım gerekli değerleri okuyup tarayıcıyı kapatacak, tamamen arka planda çalışır.

5. Not değişimlerini terminalden izleyebilirsiniz, değişim olduğunda sesli uyarı alacaksınız.



## Önemli Uyarılar ve Bilinmesi Gerekenler

### Güvenlik: 
Kod tamamen sizin bilgisayarınızda (yerelde) çalışır. Şifreniz veya çerezleriniz hiçbir yere gönderilmez. Sadece OBS'ye bağlanır.

### Oturum Düşmesi: 
OBS sistemi belli aralıklarla veya başka bir cihazdan (telefondan vb.) giriş yaptığınızda oturumunuzu sonlandırabilir. Bu durumda program bunu fark eder ve giriş yapmanız için tarayıcıyı tekrar açar.

### Sesli Uyarı: 
Not girildiğinde bilgisayarınızdan bir uyarı sesi gelir. Hoparlörünüzün açık olduğundan emin olun.

### Not:
Sınav sonrası hızlıca hazırladığım bir programdır, uzun vadeli geliştirme sağlamayı planlamıyorum, isteyen kişiler sormaksızın veya referans vermeksizin diledikleri gibi kullanabilirler, geliştirebilirler ve yayabilirler.

**Geliştirici: Abdulkadir Ustaoğlu**
