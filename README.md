# 🔧 Smart Manufacturing Manager (Akıllı Atölye ve Üretim Yönetim ERP Sistemi)

> **Masaüstü Tabanlı, Çift Tema Destekli, Gerçek Zamanlı Veri Analitikli ve Güvenli Atölye Yönetim Platformu**  
> Bu proje; imalat süreçlerindeki malzeme, makine ve operasyonel maliyetleri hesaplamanın ötesine geçerek; üretimdeki fire oranlarını ve geri kazanılabilir hurda değerlerini analiz eden, atölyede kalacak gizli kazancı (hurda kârı) ortaya çıkararak teklifleri en kârlı şekilde sunmanızı sağlayan akademik standartlarda geliştirilmiş kurumsal bir masaüstü ERP yazılımıdır.

---

## 📸 Ekran Görüntüleri ve Teknik Detayları

### 🔐 1. Gelişmiş Giriş Ekranı (Authentication Module)
Akademik sunum standartlarına uygun, sade, güvenli ve kurumsal split-panel kullanıcı giriş paneli.
*   **Görsel Arayüz:**
    ![Giriş Ekranı](assets/screenshots/00_login_light.png)
*   **Teknik Özellikler:**
    *   **Kriptografik Güvenlik:** Kullanıcı şifreleri veritabanında düz metin olarak değil, **SHA-256** hash algoritmasıyla özetlenerek saklanır.
    *   **JSON Tabanlı Tercih Yönetimi:** "Beni Hatırla" seçeneği işaretlendiğinde, kullanıcı tercihleri yerel bir ayar dosyasında (JSON) saklanır ve uygulama açılışında otomatik yüklenir.
    *   **Şifre Görünürlük Kontrolü:** Dinamik durum güncellemesiyle maskelenmiş şifre alanı.
    *   **Dinamik Hata Yönetimi:** Yanlış girişlerde veya eksik alanlarda kullanıcıyı engellemeden uyaran dinamik modal diyaloglar.

### 📊 2. Panel Özeti (Dashboard - Çift Tema Desteği)
Atölyenin finansal ve operasyonel durumunu gerçek zamanlı özetleyen merkezi kontrol paneli.
*   **Koyu Tema Görünümü (Dark Mode):**
    ![Koyu Tema Panel Özeti](assets/screenshots/01_dashboard_dark.png)
*   **Açık Tema Görünümü (Light Mode):**
    ![Açık Tema Panel Özeti](assets/screenshots/01_dashboard_light.png)
*   **Teknik Özellikler:**
    *   **TCMB Asenkron API Entegrasyonu:** Sağ üstte yer alan canlı döviz kurları (USD/EUR), arayüz döngüsünü engellememesi (UI Freezing yaşanmaması) için arka planda çalışan ayrı bir **Thread (İş Parçacığı)** üzerinden `today.xml` API'sinden asenkron olarak çekilir. İnternet kesintilerinde "Çevrimdışı" durumuna geçen hata toleransı (`Graceful Degradation`) entegredir.
    *   **Dinamik Tema Adaptasyonlu Matplotlib Grafikleri:** Grafiklerin arayüze gömülmesi `FigureCanvasTkAgg` ile sağlanmıştır. Tema değiştiğinde grafiklerin arka planı, ızgaraları ve yazı renkleri anlık olarak koyu/açık mod renk paletine (`#1E293B` / `white`) uyum sağlar.
    *   **Gerçek Zamanlı KPI Kartları:** Onaylanmış siparişlerden üretilen ciro, net maliyet ve brüt kar hesaplamaları anlık veritabanı sorgularıyla güncellenir.

### 📋 3. Teklif Yönetimi ve Hızlı Hesaplama Sihirbazı
Malzeme ve makine giderlerini, fire oranlarını ve işçilik sürelerini birleştirerek detaylı teklif oluşturan maliyet motoru.
*   **Görsel Arayüz:**
    ![Teklif Yönetimi](assets/screenshots/02_teklifler.png)
    ![Yeni Teklif Sihirbazı](assets/screenshots/03_yeni_teklif.png)
*   **Teklif Hesaplama Algoritması:**
    $$\text{Net Maliyet} = \sum (\text{Malzeme Maliyeti} \times \text{Miktar}) + \sum (\text{Saatlik Makine Ücreti} \times \text{Süre}) + \text{Ek Giderler}$$
    $$\text{Teklif Tutarı} = \left( \text{Net Maliyet} \times \left(1 + \frac{\text{Kar Oranı}}{100}\right) \right) - \text{Uygulanan İndirim}$$
    $$\text{Hurda Kazancı} = \text{Toplam Fire Miktarı} \times \text{Hurda Birim Fiyatı}$$

### 📅 4. Akıllı Üretim Takvimi
Termin tarihlerini ve iş akışını görselleştiren takvim modülü.
*   **Görsel Arayüz:**
    ![Üretim Takvimi](assets/screenshots/06_takvim.png)
*   **Teknik Özellikler:**
    *   Tekliflerin teslim tarihlerine göre renklendirilmiş (Onaylandı: Yeşil, Beklemede: Sarı, İptal: Gri) dinamik gün kutuları.
    *   Sıkışık günlerin ve iş yoğunluğunun tek bakışta analiz edilmesini sağlayan kapasite kontrolü.

### 📈 5. Gelişmiş Raporlama ve Dışa Aktarım Modülü
Filtreleme kriterlerine göre ciro, kar-zarar, müşteri hacmi ve malzeme tüketim raporları üreten analiz ekranı.
*   **Görsel Arayüz:**
    ![Raporlama](assets/screenshots/05_raporlar.png)
*   **Teknik Özellikler:**
    *   **Çok Boyutlu SQL Analizleri:** Tarih aralığı, müşteri, işlem türü ve teklif durumuna göre dinamik SQL sorguları üretilir.
    *   **Zebra Grid Tablolar:** Arayüzdeki veriler, okunabilirliği artırmak amacıyla alternatif satır renklendirmeli tablolarda listelenir.
    *   **ReportLab PDF Rapor Motoru:** Türkçe karakter desteği için sistemdeki Arial yazı tipi (`arial.ttf`) projeye dinamik olarak kaydedilir. Üretilen raporlar kurumsal renkler, grid çizgileri ve PDF standartlarında başlıklarla süslenir.
    *   **openpyxl Excel Rapor Motoru:** Raporları çoklu sekmeler (Özet, Müşteriler, İşlemler, Malzemeler) halinde ve para birimi biçimlendirmeleriyle Excel dosyasına aktarır.

---

## 🛠️ Teknik Altyapı ve Yazılım Mimarisi

*   **Programlama Dili:** Python 3.10+
*   **GUI Framework:** CustomTkinter (Modern masaüstü bileşenleri sunan Tkinter sarmalayıcısı)
*   **Veritabanı Katmanı:** SQLite (`data/app.db`)
    *   **İlişkisel Şema:** Bire-Çok (1-to-Many) tablolar arası ilişkiler ve veri bütünlüğünü koruyan `ON DELETE CASCADE` kısıtları.
*   **Veri Görselleştirme:** Matplotlib (Arayüze entegre gömülü grafik motoru)
*   **Raporlama Kütüphaneleri:** ReportLab (PDF), openpyxl (Excel)
*   **Güvenlik Modülü:** hashlib (SHA-256 Password Hashing)

---

## ⚙️ Güvenlik ve Performans Optimizasyonları

1.  **Bellek Yönetimi (Memory Cleanup):**
    CustomTkinter tabanlı ekran geçişlerinde, kullanılmayan eski ekran nesneleri `destroy()` edilerek RAM üzerindeki gereksiz widget yükü temizlenir.
2.  **Thread Safety (İş Parçacığı Güvenliği):**
    TCMB döviz kuru çeken arka plan işçi thread'i (worker thread), ana GUI bileşenlerine doğrudan erişmez. Bunun yerine verileri çekip arayüze `root.after()` metodu üzerinden paslar. Bu, işletim sistemi düzeyinde yaşanabilecek arayüz çökmelerini engeller.
3.  **SQL Enjeksiyon Koruması:**
    Tüm sorgular, parametreli SQL (prepared statements) yöntemiyle çalıştırılarak SQL Injection saldırılarına karşı tam koruma sağlar:
    ```python
    cursor.execute("SELECT * FROM teklifler WHERE kullanici_id = ?", (user_id,))
    ```

---

## 🚀 Başlangıç ve Kurulum

### Gerekli Kütüphaneler
Uygulamayı çalıştırmadan önce sisteminizde Python'ın kurulu olduğundan emin olun ve aşağıdaki bağımlılıkları terminalden yükleyin:
```bash
pip install customtkinter matplotlib pillow openpyxl reportlab
```

### Uygulamayı Çalıştırma
Ana proje dizininde terminali açıp şu komutu yürüterek programı başlatabilirsiniz:
```bash
python main.py
```

*   **Varsayılan Yönetici Giriş Bilgileri:**
    *   **Kullanıcı Adı:** `admin`
    *   **Şifre:** `1234`
