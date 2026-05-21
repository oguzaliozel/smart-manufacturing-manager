import sqlite3
import os

class Database:
    def __init__(self, db_path="data/app.db"):
        # Veritabanı klasörü yoksa oluştur
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        conn = self.connect()
        cursor = conn.cursor()

        # 1. kullanicilar tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad_soyad TEXT,
            kullanici_adi TEXT UNIQUE,
            sifre TEXT,
            rol TEXT,
            tema TEXT DEFAULT 'Açık',
            dil TEXT DEFAULT 'tr'
        )
        ''')

        # 2. musteriler tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS musteriler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_id INTEGER,
            firma_adi TEXT,
            yetkili_kisi TEXT,
            telefon TEXT,
            mail TEXT,
            adres TEXT,
            vergi_no TEXT,
            notlar TEXT,
            FOREIGN KEY (kullanici_id) REFERENCES kullanicilar (id)
        )
        ''')

        # 3. malzemeler tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS malzemeler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_id INTEGER,
            malzeme_adi TEXT,
            birim TEXT,
            birim_fiyat REAL,
            hurda_birim_fiyati REAL,
            varsayilan_fire_orani REAL,
            aciklama TEXT,
            aktif INTEGER DEFAULT 1,
            FOREIGN KEY (kullanici_id) REFERENCES kullanicilar (id)
        )
        ''')
        
        # Eski veritabanlarında 'aktif' kolonu yoksa ekle
        try:
            cursor.execute("ALTER TABLE malzemeler ADD COLUMN aktif INTEGER DEFAULT 1")
        except sqlite3.OperationalError:
            pass # Kolon zaten varsa hata verir, görmezden geliyoruz

        # 4. islemler tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS islemler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_id INTEGER,
            islem_adi TEXT,
            saatlik_makine_maliyeti REAL,
            varsayilan_fire_orani REAL,
            aciklama TEXT,
            FOREIGN KEY (kullanici_id) REFERENCES kullanicilar (id)
        )
        ''')

        # 5. teklifler tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS teklifler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_id INTEGER,
            musteri_id INTEGER,
            teklif_no TEXT,
            baslik TEXT,
            durum TEXT,
            para_birimi TEXT,
            malzeme_maliyeti REAL,
            makine_maliyeti REAL,
            ek_gider REAL,
            net_maliyet REAL,
            kar_tipi TEXT,
            kar_orani REAL,
            sabit_kar REAL,
            kar_tutari REAL,
            teklif_tutari REAL,
            tahmini_hurda_degeri REAL,
            manuel_indirim REAL,
            son_tutar REAL,
            olusturma_tarihi TEXT,
            gecerlilik_tarihi TEXT,
            teslim_tarihi TEXT,
            notlar TEXT,
            FOREIGN KEY (kullanici_id) REFERENCES kullanicilar (id),
            FOREIGN KEY (musteri_id) REFERENCES musteriler (id)
        )
        ''')

        # 6. teklif_kalemleri tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS teklif_kalemleri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teklif_id INTEGER,
            malzeme_id INTEGER,
            islem_id INTEGER,
            malzeme_adi TEXT,
            islem_adi TEXT,
            miktar REAL,
            birim TEXT,
            birim_fiyat REAL,
            fire_orani REAL,
            fire_miktari REAL,
            hurda_birim_fiyati REAL,
            tahmini_hurda_degeri REAL,
            makine_suresi REAL,
            makine_saat_ucreti REAL,
            malzeme_maliyeti REAL,
            makine_maliyeti REAL,
            kalem_maliyeti REAL,
            FOREIGN KEY (teklif_id) REFERENCES teklifler (id),
            FOREIGN KEY (malzeme_id) REFERENCES malzemeler (id),
            FOREIGN KEY (islem_id) REFERENCES islemler (id)
        )
        ''')

        # 7. hurda_hareketleri tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS hurda_hareketleri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_id INTEGER,
            teklif_id INTEGER,
            malzeme_adi TEXT,
            fire_miktari REAL,
            birim TEXT,
            hurda_birim_fiyati REAL,
            tahmini_hurda_degeri REAL,
            durum TEXT,
            tarih TEXT,
            FOREIGN KEY (kullanici_id) REFERENCES kullanicilar (id),
            FOREIGN KEY (teklif_id) REFERENCES teklifler (id)
        )
        ''')

        # 8. takvim_isleri tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS takvim_isleri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_id INTEGER,
            teklif_id INTEGER,
            baslik TEXT,
            aciklama TEXT,
            baslangic_tarihi TEXT,
            teslim_tarihi TEXT,
            saat TEXT DEFAULT '12:00',
            renk TEXT DEFAULT '#3B82F6',
            durum TEXT,
            FOREIGN KEY (kullanici_id) REFERENCES kullanicilar (id),
            FOREIGN KEY (teklif_id) REFERENCES teklifler (id)
        )
        ''')

        # Geriye dönük kolon eklemeleri
        try:
            cursor.execute("ALTER TABLE takvim_isleri ADD COLUMN saat TEXT DEFAULT '12:00'")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE takvim_isleri ADD COLUMN renk TEXT DEFAULT '#3B82F6'")
        except sqlite3.OperationalError:
            pass

        conn.commit()
        conn.close()

    def create_default_user(self):
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = 'admin'")
            if not cursor.fetchone():
                cursor.execute('''
                INSERT INTO kullanicilar (ad_soyad, kullanici_adi, sifre, rol)
                VALUES (?, ?, ?, ?)
                ''', ('Sistem Yöneticisi', 'admin', '1234', 'Yönetici'))
                conn.commit()
        except sqlite3.Error as e:
            print("Kullanıcı oluşturma hatası:", e)
        finally:
            conn.close()
            
    def login(self, username, password):
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = ? AND sifre = ?", (username, password))
            user = cursor.fetchone()
            return dict(user) if user else None
        except sqlite3.Error as e:
            print("Giriş hatası:", e)
            return None
        finally:
            conn.close()

    def malzeme_sil(self, malzeme_id, kullanici_id):
        """
        Malzemeyi siler veya teklifte kullanılmışsa pasif (aktif=0) yapar.
        Geriye: (durum_kodu, mesaj) döner.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Tekliflerde kullanılmış mı kontrol et (kalemlerden bakıyoruz)
            cursor.execute("SELECT COUNT(*) FROM teklif_kalemleri WHERE malzeme_id = ?", (malzeme_id,))
            kullanim_sayisi = cursor.fetchone()[0]
            
            if kullanim_sayisi > 0:
                # Geçmiş tekliflerde var, pasif yapıyoruz
                cursor.execute("UPDATE malzemeler SET aktif = 0 WHERE id = ? AND kullanici_id = ?", (malzeme_id, kullanici_id))
                conn.commit()
                return "pasif", "Bu malzeme geçmiş tekliflerde kullanıldığı için silinemiyor.\nBunun yerine sistemde pasif (arşiv) durumuna getirildi."
            else:
                # Kullanılmamış, direkt sil
                cursor.execute("DELETE FROM malzemeler WHERE id = ? AND kullanici_id = ?", (malzeme_id, kullanici_id))
                conn.commit()
                return "silindi", "Malzeme başarıyla veritabanından silindi."
        except sqlite3.Error as e:
            return "hata", f"İşlem sırasında veritabanı hatası oluştu: {e}"
        finally:
            conn.close()

    def teklif_durum_guncelle(self, teklif_id, yeni_durum, kullanici_id):
        """
        Teklifin durumunu günceller. Sadece ilgili kullanıcının teklifini günceller.
        İşlem başarılıysa True, hata durumunda False döner.
        Onaylanan tekliflerin hurda/fire kalemlerini otomatik olarak Hurda Deposuna aktarır.
        """
        try:
            from datetime import datetime
            conn = self.connect()
            cursor = conn.cursor()
            
            # Önce eski durumu kontrol edelim
            cursor.execute("SELECT durum FROM teklifler WHERE id = ? AND kullanici_id = ?", (teklif_id, kullanici_id))
            eski_durum_row = cursor.fetchone()
            if not eski_durum_row:
                conn.close()
                return False
            eski_durum = eski_durum_row["durum"]
            
            # Durumu güncelle
            cursor.execute(
                "UPDATE teklifler SET durum = ? WHERE id = ? AND kullanici_id = ?",
                (yeni_durum, teklif_id, kullanici_id)
            )
            
            # Durum "Onaylandı"ya döndüyse ve eskiden "Onaylandı" değilse, hurda girişlerini ekle
            if yeni_durum == "Onaylandı" and eski_durum != "Onaylandı":
                cursor.execute("""
                    SELECT malzeme_adi, fire_miktari, birim, hurda_birim_fiyati, tahmini_hurda_degeri
                    FROM teklif_kalemleri
                    WHERE teklif_id = ? AND tahmini_hurda_degeri > 0
                """, (teklif_id,))
                kalemler = cursor.fetchall()
                
                bugun = datetime.now().strftime("%Y-%m-%d")
                for k in kalemler:
                    cursor.execute("""
                        INSERT INTO hurda_hareketleri (kullanici_id, teklif_id, malzeme_adi, fire_miktari, birim, hurda_birim_fiyati, tahmini_hurda_degeri, durum, tarih)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 'Depoda', ?)
                    """, (kullanici_id, teklif_id, k["malzeme_adi"], k["fire_miktari"], k["birim"], k["hurda_birim_fiyati"], k["tahmini_hurda_degeri"], bugun))
                    
            # Durum "Onaylandı"dan başka bir şeye döndüyse, bu teklifle ilişkili olan ve henüz satılmamış (durum='Depoda') hurdaları temizle
            elif yeni_durum != "Onaylandı" and eski_durum == "Onaylandı":
                cursor.execute("""
                    DELETE FROM hurda_hareketleri 
                    WHERE teklif_id = ? AND kullanici_id = ? AND durum = 'Depoda'
                """, (teklif_id, kullanici_id))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print("Teklif durum güncelleme hatası:", e)
            return False
        finally:
            conn.close()