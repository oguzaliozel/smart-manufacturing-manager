<div align="center">
  <img src="assets/logo.png" alt="Logo" width="100" height="100">
  <h1 align="center">Smart Manufacturing Manager</h1>
  <p align="center">
    Atölye Süreçleri için Akıllı Maliyet Hesaplama, Geri Kazanım ve Kar Takip ERP Platformu
    <br />
    <a href="https://github.com/oguzaliozel/smart-manufacturing-manager"><strong>Repo Sayfası</strong></a>
    ·
    <a href="mailto:oguzaliozel@gmail.com"><strong>Destek Al</strong></a>
  </p>
</div>

---

### 📌 Proje Hakkında (About The Project)

**Smart Manufacturing Manager**, imalat süreçlerindeki malzeme, makine ve operasyonel maliyetleri hesaplamanın ötesine geçerek; üretimdeki fire oranlarını ve hurda değerlerini analiz eden, atölyede kalacak gizli kazancı (hurda kârı) ortaya çıkararak teklifleri en kârlı şekilde sunmanızı sağlayan modern bir masaüstü yazılımıdır.

*   🎨 **Çift Tema Desteği:** Sistem veya kullanıcı ayarlarına göre anlık Açık/Koyu mod geçişi.
*   💱 **Canlı TCMB Döviz Widget'ı:** Arayüzü dondurmayan asenkron thread mimarisi ile canlı kur takibi.
*   📈 **Dinamik Grafikler:** Temayla uyumlu Matplotlib donut ve çizgi grafik analiz panelleri.
*   📄 **Profesyonel Raporlama:** Excel (openpyxl) ve Türkçe karakter destekli PDF (ReportLab) döküm motorları.
*   🔐 **Güvenli Erişim:** Kullanıcı şifrelerinin SHA-256 hash algoritmasıyla özetlenerek saklanması.

### 🛠️ Kullanılan Teknolojiler (Built With)

*   **GUI:** Python & [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
*   **Database:** [SQLite](https://www.sqlite.org/) (ACID uyumlu ilişkisel db)
*   **Visuals:** [Matplotlib](https://matplotlib.org/) & [Pillow](https://python-pillow.org/)
*   **Exporters:** [ReportLab](https://www.reportlab.com/) (PDF) & [openpyxl](https://openpyxl.readthedocs.io/) (Excel)

---

### 📸 Ekran Görüntüleri (Screenshots)

#### 🔐 Giriş Paneli (Login Screen)
*Gelişmiş split-panel arayüzü, şifreli kimlik doğrulama ve kullanıcı tercihleri (JSON).*
![Giriş Ekranı](assets/screenshots/00_login_light.png)

#### 📊 Panel Özeti (Dashboard)
*Gerçek zamanlı KPI kartları, asenkron TCMB döviz widget'ı ve dinamik grafikler.*
*   **Koyu Tema (Dark Mode):**
    ![Koyu Tema](assets/screenshots/01_dashboard_dark.png)
*   **Açık Tema (Light Mode):**
    ![Açık Tema](assets/screenshots/01_dashboard_light.png)

#### 📋 Teklif ve Maliyet Sihirbazı (Proposal Wizard)
*Malzeme, işçilik ve operasyonel giderlerin hesaplandığı otomatik teklif oluşturucu.*
![Teklif Listesi](assets/screenshots/02_teklifler.png)
![Teklif Sihirbazı](assets/screenshots/03_yeni_teklif.png)

#### 📅 Üretim Takvimi & Raporlama (Scheduler & Reporting)
*Termin tarihli takvim iş akışı ve çok boyutlu rapor analizleri.*
![Takvim](assets/screenshots/06_takvim.png)
![Raporlar](assets/screenshots/05_raporlar.png)

---

### 🚀 Kurulum ve Çalıştırma (Getting Started)

#### Gereksinimler (Prerequisites)
Projenin çalışması için Python 3.10+ sürümünün ve gerekli kütüphanelerin yüklü olması gerekir:
```bash
pip install customtkinter matplotlib pillow openpyxl reportlab
```

#### Çalıştırma (Execution)
Projeyi klonladıktan sonra ana dizinde terminalden şu komutla başlatabilirsiniz:
```bash
python main.py
```

*   **Varsayılan Giriş Bilgileri:**
    *   **Kullanıcı Adı:** `admin`
    *   **Şifre:** `1234`

---

### 🛡️ Lisans ve İletişim (License & Contact)

*   **Lisans:** MIT License
*   **Geliştirici:** Oğuz Ali Özel - [oguzaliozel@gmail.com](mailto:oguzaliozel@gmail.com)
