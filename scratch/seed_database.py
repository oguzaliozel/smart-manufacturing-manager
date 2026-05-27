import sqlite3
import random
from datetime import datetime, timedelta

def seed_db(db_path="data/app.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # ── 1. KULLANICI BUL VEYA OLUŞTUR ──────────────────────────────────────────
    cursor.execute("SELECT id FROM kullanicilar WHERE kullanici_adi = 'admin'")
    user_row = cursor.fetchone()
    if user_row:
        user_id = user_row["id"]
    else:
        cursor.execute("INSERT INTO kullanicilar (ad_soyad, kullanici_adi, sifre, rol) VALUES ('Sistem Yöneticisi', 'admin', '1234', 'Yönetici')")
        user_id = cursor.lastrowid
        
    # Mevcut test verilerini temizle (kullanıcıyı koruyoruz)
    cursor.execute("DELETE FROM musteriler WHERE kullanici_id = ?", (user_id,))
    cursor.execute("DELETE FROM malzemeler WHERE kullanici_id = ?", (user_id,))
    cursor.execute("DELETE FROM islemler WHERE kullanici_id = ?", (user_id,))
    cursor.execute("DELETE FROM teklifler WHERE kullanici_id = ?", (user_id,))
    cursor.execute("DELETE FROM teklif_kalemleri WHERE teklif_id NOT IN (SELECT id FROM teklifler)")
    cursor.execute("DELETE FROM hurda_hareketleri WHERE kullanici_id = ?", (user_id,))
    cursor.execute("DELETE FROM takvim_isleri WHERE kullanici_id = ?", (user_id,))
    
    # ── 2. MALZEMELER (Gerçekçi Fiyat ve Hurda Oranları) ─────────────────────
    malzemeler_data = [
        # (malzeme_adi, birim, birim_fiyat, hurda_birim_fiyati, varsayilan_fire_orani, aciklama)
        ("Alüminyum 6061 T6", "kg", 185.0, 65.0, 0.15, "Havacılık ve makine parçaları için yüksek mukavemetli alüminyum."),
        ("Paslanmaz Çelik 304", "kg", 210.0, 75.0, 0.12, "Gıda, kimya ve genel amaçlı korozyona dayanıklı paslanmaz çelik."),
        ("Paslanmaz Çelik 316L", "kg", 270.0, 95.0, 0.10, "Denizcilik ve yüksek asit direnci gerektiren yerler için premium çelik."),
        ("Demir St37 (Karbon Çeliği)", "kg", 85.0, 20.0, 0.10, "Genel yapısal parçalar, şasiler ve profiller için yaygın malzeme."),
        ("Sarı Pirinç MS58", "kg", 340.0, 165.0, 0.08, "CNC talaşlı imalata uygun, kolay işlenebilir pirinç alaşımı."),
        ("Elektrolitik Bakır Levha", "kg", 460.0, 240.0, 0.07, "Elektrik iletkenliği yüksek saf bakır levha."),
        ("Delrin (POM-C) Plastik", "kg", 145.0, 0.0, 0.15, "Mühendislik plastiği, yüksek boyutsal kararlılık, hurda değeri yoktur."),
        ("Teflon (PTFE) Çubuk", "kg", 320.0, 0.0, 0.12, "Sıcaklık ve kimyasal dayanımlı mühendislik plastiği."),
        ("Titanyum Gr5", "kg", 1250.0, 420.0, 0.20, "Medikal ve havacılık için ultra hafif ve dayanıklı alaşım."),
        ("Döküm Pik Demir", "kg", 95.0, 28.0, 0.05, "Piston ve motor gövdeleri için pik döküm demir.")
    ]
    
    inserted_malzemeler = []
    for m in malzemeler_data:
        cursor.execute("""
            INSERT INTO malzemeler (kullanici_id, malzeme_adi, birim, birim_fiyat, hurda_birim_fiyati, varsayilan_fire_orani, aciklama, aktif)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (user_id, m[0], m[1], m[2], m[3], m[4], m[5]))
        inserted_malzemeler.append({
            "id": cursor.lastrowid,
            "ad": m[0],
            "birim": m[1],
            "fiyat": m[2],
            "hurda_fiyat": m[3],
            "fire": m[4]
        })
        
    # ── 3. İŞLEMLER / MAKİNELER ───────────────────────────────────────────────
    islemler_data = [
        # (islem_adi, saatlik_makine_maliyeti, varsayilan_fire_orani, aciklama)
        ("CNC Freze (5 Eksen)", 450.0, 0.04, "Hassas yüzey işleme ve kompleks geometriler."),
        ("CNC Torna (Y eksenli)", 320.0, 0.03, "Silindirik parça işleme ve tornalama."),
        ("Lazer Kesim (4kW Fiber)", 240.0, 0.05, "Hızlı levha sac kesim işlemleri."),
        ("Abkant CNC Büküm", 160.0, 0.02, "Sac bükme ve şekillendirme."),
        ("Gazaltı Kaynağı (MIG/MAG)", 140.0, 0.01, "Çelik ve alüminyum kaynak işçiliği."),
        ("TIG Kaynağı (Argon)", 180.0, 0.01, "Hassas paslanmaz ve alüminyum kaynağı."),
        ("Elektrostatik Toz Boya", 200.0, 0.03, "Koruyucu ve dekoratif fırınlı boyama."),
        ("Tel Erezyon Kesim", 190.0, 0.01, "Kalıp çeliği ve sert metal hassas kesim.")
    ]
    
    inserted_islemler = []
    for i in islemler_data:
        cursor.execute("""
            INSERT INTO islemler (kullanici_id, islem_adi, saatlik_makine_maliyeti, varsayilan_fire_orani, aciklama)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, i[0], i[1], i[2], i[3]))
        inserted_islemler.append({
            "id": cursor.lastrowid,
            "ad": i[0],
            "ucret": i[1],
            "fire": i[2]
        })

    # ── 4. MÜŞTERİLER ──────────────────────────────────────────────────────────
    musteriler_data = [
        ("Aselsan Savunma A.Ş.", "Mustafa Yılmaz", "03123849090", "info@aselsan.com.tr", "Ankara Macunköy Tesisleri", "1234567890", "Savunma sanayi projeleri."),
        ("Roketsan A.Ş.", "Canan Demir", "03128601010", "procurement@roketsan.com.tr", "Elmadağ, Ankara", "9876543210", "Roket ve füze komponentleri."),
        ("TUSAŞ Havacılık", "Özgür Kaya", "03128111800", "subcontract@tusas.com", "Kahramankazan, Ankara", "4567890123", "Havacılık yapısalları imalatı."),
        ("Ford Otosan A.Ş.", "Bülent Avcı", "02623155000", "bavci@ford.com.tr", "Gölcük Tesisleri, Kocaeli", "5566778899", "Otomotiv yedek parça ve prototipler."),
        ("Baykar Teknoloji", "Selim Bayraktar", "02128670900", "tedarik@baykar.com", "Hadımköy, İstanbul", "1122334455", "İHA/SİHA mekanik parçaları."),
        ("FNSS Savunma Sistemleri", "Hakan Şen", "03124974300", "hakan.sen@fnss.com.tr", "Gölbaşı, Ankara", "6677889900", "Zırhlı araç alt gövde kaynak işleri."),
        ("Arçelik A.Ş.", "Derya Çelik", "02123143434", "derya.celik@arcelik.com", "Tuzla Tesisleri, İstanbul", "9900112233", "Plastik kalıp ve prototip imalatı.")
    ]
    
    inserted_musteriler = []
    for cust in musteriler_data:
        cursor.execute("""
            INSERT INTO musteriler (kullanici_id, firma_adi, yetkili_kisi, telefon, mail, adres, vergi_no, notlar)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, cust[0], cust[1], cust[2], cust[3], cust[4], cust[5], cust[6]))
        inserted_musteriler.append({
            "id": cursor.lastrowid,
            "firma": cust[0]
        })

    # ── 5. TEKLİFLER VE KALEMLER (28 Adet Teklif) ─────────────────────────────
    teklif_basliklari = [
        "Özel Miller ve Redüktör Dişlisi", "Havacılık Sensör Muhafazası", "Zırhlı Araç Taban Braketi",
        "Sac Panel Lazer Kesim & Büküm", "Paslanmaz Yakıt Deposu Kaynağı", "Alüminyum Soğutucu Blok",
        "Teflon Conta ve Yataklama Grubu", "CNC Boy çıkarma Aparatı", "Boru Şasi Kaynaklı İmalat",
        "Boyalı Dış Kapak Montajı", "Elektrik Kontrol Kutusu Şasisi", "Titanyum Flanj Takımı",
        "Piston Kolu ve Burçlar", "Delrin Kayar Yatak Parçası", "Paslanmaz Çelik Rekor Grubu",
        "Sarı Pirinç Vana Gövdesi", "Robot Kolu Mekanik Eklem", "Konveyör Ayak Şasisi",
        "Fırınlı Boyalı Kapak Takımı", "Abkant Bükümlü Destek Sacları", "Lazerle Kesilmiş Braketler",
        "CNC Torna Milleri", "Frezelenmiş Montaj Tablası", "Özel Kilit Mekanizması",
        "Bakır Bara ve İletken Levha", "Demir Profil Karkas", "Döküm Gövde Tornalama",
        "Havacılık Test Kabini Sacları"
    ]
    
    durumlar = ["Onaylandı"] * 11 + ["Beklemede"] * 8 + ["Reddedildi"] * 5 + ["İptal"] * 4
    random.shuffle(durumlar)
    
    bugun_dt = datetime.now()
    
    for i in range(28):
        teklif_no = f"TEK-{ (bugun_dt - timedelta(days=i)).strftime('%Y%m%d') }{i:04d}"
        baslik = teklif_basliklari[i]
        durum = durumlar[i]
        musteri = random.choice(inserted_musteriler)
        
        # Günler
        olusturma_dt = bugun_dt - timedelta(days=random.randint(10, 30))
        gecerlilik_dt = olusturma_dt + timedelta(days=30)
        teslim_dt = olusturma_dt + timedelta(days=random.randint(25, 40))
        
        olusturma_str = olusturma_dt.strftime("%Y-%m-%d")
        gecerlilik_str = gecerlilik_dt.strftime("%Y-%m-%d")
        teslim_str = teslim_dt.strftime("%Y-%m-%d")
        
        para_birimi = "₺"
        
        # Kalemleri oluştur
        num_kalemler = random.randint(1, 3)
        malzeme_maliyeti = 0.0
        makine_maliyeti = 0.0
        tahmini_hurda_degeri = 0.0
        
        kalemler_to_insert = []
        for _ in range(num_kalemler):
            malzeme = random.choice(inserted_malzemeler)
            islem = random.choice(inserted_islemler)
            
            miktar = random.randint(10, 100)
            makine_suresi = random.uniform(2.0, 15.0)
            
            # Hesaplamalar
            kalem_malzeme_maliyeti = miktar * malzeme["fiyat"] * (1 + malzeme["fire"])
            fire_miktari = miktar * malzeme["fire"]
            kalem_hurda_degeri = fire_miktari * malzeme["hurda_fiyat"]
            
            kalem_makine_maliyeti = makine_suresi * islem["ucret"] * (1 + islem["fire"])
            kalem_maliyeti = kalem_malzeme_maliyeti + kalem_makine_maliyeti
            
            malzeme_maliyeti += kalem_malzeme_maliyeti
            makine_maliyeti += kalem_makine_maliyeti
            tahmini_hurda_degeri += kalem_hurda_degeri
            
            kalemler_to_insert.append({
                "malzeme_id": malzeme["id"],
                "islem_id": islem["id"],
                "malzeme_adi": malzeme["ad"],
                "islem_adi": islem["ad"],
                "miktar": miktar,
                "birim": malzeme["birim"],
                "birim_fiyat": malzeme["fiyat"],
                "fire_orani": malzeme["fire"],
                "fire_miktari": fire_miktari,
                "hurda_birim_fiyati": malzeme["hurda_fiyat"],
                "tahmini_hurda_degeri": kalem_hurda_degeri,
                "makine_suresi": makine_suresi,
                "makine_saat_ucreti": islem["ucret"],
                "malzeme_maliyeti": kalem_malzeme_maliyeti,
                "makine_maliyeti": kalem_makine_maliyeti,
                "kalem_maliyeti": kalem_maliyeti
            })
            
        ek_gider = random.uniform(100, 800)
        net_maliyet = malzeme_maliyeti + makine_maliyeti + ek_gider
        
        kar_tipi = "Oran"
        kar_orani = random.randint(20, 35)
        kar_tutari = net_maliyet * (kar_orani / 100.0)
        
        teklif_tutari = net_maliyet + kar_tutari
        manuel_indirim = random.choice([0.0, 0.0, 100.0, 250.0, 500.0])
        son_tutar = teklif_tutari - manuel_indirim
        
        # 1. Teklifi Kaydet
        cursor.execute("""
            INSERT INTO teklifler (
                kullanici_id, musteri_id, teklif_no, baslik, durum, para_birimi,
                malzeme_maliyeti, makine_maliyeti, ek_gider, net_maliyet, kar_tipi,
                kar_orani, sabit_kar, kar_tutari, teklif_tutari, tahmini_hurda_degeri,
                manuel_indirim, son_tutar, olusturma_tarihi, gecerlilik_tarihi, teslim_tarihi, notlar
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0.0, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, musteri["id"], teklif_no, baslik, durum, para_birimi,
            malzeme_maliyeti, makine_maliyeti, ek_gider, net_maliyet, kar_tipi,
            kar_orani, kar_tutari, teklif_tutari, tahmini_hurda_degeri,
            manuel_indirim, son_tutar, olusturma_str, gecerlilik_str, teslim_str, f"{baslik} üretimi için teknik çizimler alındı."
        ))
        teklif_id = cursor.lastrowid
        
        # 2. Kalemleri Kaydet
        for k in kalemler_to_insert:
            cursor.execute("""
                INSERT INTO teklif_kalemleri (
                    teklif_id, malzeme_id, islem_id, malzeme_adi, islem_adi, miktar, birim,
                    birim_fiyat, fire_orani, fire_miktari, hurda_birim_fiyati, tahmini_hurda_degeri,
                    makine_suresi, makine_saat_ucreti, malzeme_maliyeti, makine_maliyeti, kalem_maliyeti
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                teklif_id, k["malzeme_id"], k["islem_id"], k["malzeme_adi"], k["islem_adi"],
                k["miktar"], k["birim"], k["birim_fiyat"], k["fire_orani"], k["fire_miktari"],
                k["hurda_birim_fiyati"], k["tahmini_hurda_degeri"], k["makine_suresi"],
                k["makine_saat_ucreti"], k["malzeme_maliyeti"], k["makine_maliyeti"], k["kalem_maliyeti"]
            ))
            
        # 3. Hurda Hareketlerini Tetikle (Durum Onaylandı ise)
        if durum == "Onaylandı":
            for k in kalemler_to_insert:
                if k["tahmini_hurda_degeri"] > 0:
                    # Bazılarını satıldı, çoğunu depoda yapalım
                    hurda_durumu = random.choice(["Depoda", "Depoda", "Depoda", "Satıldı"])
                    cursor.execute("""
                        INSERT INTO hurda_hareketleri (kullanici_id, teklif_id, malzeme_adi, fire_miktari, birim, hurda_birim_fiyati, tahmini_hurda_degeri, durum, tarih)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (user_id, teklif_id, k["malzeme_adi"], k["fire_miktari"], k["birim"], k["hurda_birim_fiyati"], k["tahmini_hurda_degeri"], hurda_durumu, olusturma_str))
                    
            # 4. Takvim İşi Ekle (Durum Onaylandı ise teslimat takvime eklenir)
            saatler = ["09:30", "11:00", "14:00", "15:30", "17:00"]
            renkler = ["#10B981", "#3B82F6", "#F59E0B", "#EF4444", "#8B5CF6"]
            cursor.execute("""
                INSERT INTO takvim_isleri (kullanici_id, teklif_id, baslik, aciklama, baslangic_tarihi, teslim_tarihi, saat, renk, durum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Bekliyor')
            """, (
                user_id, teklif_id, f"Teslimat: {teklif_no}",
                f"{musteri['firma']} firmasına {baslik} teslimatı yapılacaktır.",
                olusturma_str, teslim_str, random.choice(saatler), random.choice(renkler)
            ))
            
    # ── 6. EKSTRA TAKVİM GÖREVLERİ (Manuel Planlama Görevleri) ──────────────────
    # Bugün civarına planlanmış işler ekleyelim
    bugun_str = bugun_dt.strftime("%Y-%m-%d")
    yarin_str = (bugun_dt + timedelta(days=1)).strftime("%Y-%m-%d")
    dun_str = (bugun_dt - timedelta(days=1)).strftime("%Y-%m-%d")
    
    manuel_takvim_isleri = [
        ("CNC Makine Bakımı", "5 Eksen CNC Freze makinesinin yıllık periyodik mil ve kızak yağlaması yapılacaktır.", dun_str, dun_str, "09:00", "#EF4444"), # Kırmızı (Önemli/Hata)
        ("Tedarikçi Görüşmesi", "Alüminyum levha tedarikçisi Metal Sanayi ile fiyat revizyonu toplantısı.", bugun_str, bugun_str, "14:30", "#F59E0B"), # Turuncu
        ("Aselsan Tasarım Revizyonu", "Aselsan projesi kapsamında sensör kapağındaki vida delikleri revizyonu değerlendirilecek.", bugun_str, bugun_str, "16:00", "#3B82F6"), # Mavi
        ("Sevkiyat Hazırlığı", "Roketsan parçalarının paketlenmesi ve sevk irsaliyelerinin yazdırılması.", yarin_str, yarin_str, "10:30", "#10B981"), # Yeşil
        ("Atölye Temizliği ve İş Güvenliği", "Haftalık genel temizlik ve iş güvenliği ekipman kontrolleri.", yarin_str, yarin_str, "16:30", "#8B5CF6") # Mor
    ]
    
    for gorev in manuel_takvim_isleri:
        cursor.execute("""
            INSERT INTO takvim_isleri (kullanici_id, teklif_id, baslik, aciklama, baslangic_tarihi, teslim_tarihi, saat, renk, durum)
            VALUES (?, NULL, ?, ?, ?, ?, ?, ?, 'Bekliyor')
        """, (user_id, gorev[0], gorev[1], gorev[2], gorev[3], gorev[4], gorev[5]))
        
    conn.commit()
    conn.close()
    print("Database successfully seeded with realistic manufacturing data!")

if __name__ == '__main__':
    seed_db()
