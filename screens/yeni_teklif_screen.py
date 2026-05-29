import customtkinter as ctk
from tema import Renkler, Fontlar
import database
from hesaplama import Hesaplayici
from datetime import datetime

class YeniTeklifScreen(ctk.CTkFrame):
    def __init__(self, master, current_user):
        super().__init__(master, fg_color=Renkler.BG_LIGHT)
        self.current_user = current_user
        self.db = database.Database()
        
        # Seçim listeleri için verileri tutacak değişkenler
        self.musteriler = []
        self.malzemeler = []
        self.islemler = []
        
        self.edit_teklif_id = None # Düzenlenen teklifin ID'si (None ise yeni teklif)
        self._needs_refresh = False
        
        self.create_widgets()
        self.load_combobox_data()
        
    def load_data(self):
        self.load_combobox_data()
        
    def create_widgets(self):
        # Başlık ve Geri Butonu
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(40, 20))
        
        self.btn_geri = ctk.CTkButton(self.header_frame, text="< Geri", width=60, fg_color="transparent", text_color=Renkler.TEXT_GRAY, hover_color=Renkler.BORDER, command=self.geri_don)
        self.btn_geri.pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(self.header_frame, text="Yeni Teklif Oluştur", font=Fontlar.H1, text_color=Renkler.TEXT_DARK).pack(side="left")
        
        # İçerik Alanı (Sol Form, Sağ Özet)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        self.content_frame.grid_columnconfigure(0, weight=6) # Sol form daha geniş
        self.content_frame.grid_columnconfigure(1, weight=4) # Sağ özet
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # SOL FORM ALANI (Scrollable)
        self.form_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color=Renkler.CARD_BG, corner_radius=10)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        self.build_form(self.form_frame)
        
        # SAĞ ÖZET ALANI
        self.summary_frame = ctk.CTkFrame(self.content_frame, fg_color=Renkler.CARD_BG, corner_radius=10)
        self.summary_frame.grid(row=0, column=1, sticky="nsew")
        self.build_summary(self.summary_frame)
        
    def build_form(self, parent):
        padding = {"padx": 20, "pady": (10, 5), "sticky": "w"}
        parent.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        ctk.CTkLabel(parent, text="Teklif Başlığı:", font=Fontlar.BODY_BOLD).grid(row=row, column=0, **padding)
        self.entry_baslik = ctk.CTkEntry(parent, font=Fontlar.BODY)
        self.entry_baslik.grid(row=row, column=1, sticky="ew", padx=20, pady=(10, 5))
        
        row += 1
        ctk.CTkLabel(parent, text="Teslimat Tarihi:", font=Fontlar.BODY_BOLD).grid(row=row, column=0, **padding)
        self.entry_teslim_tarihi = ctk.CTkEntry(parent, font=Fontlar.BODY, placeholder_text="GG/AA/YYYY (Örn: 30/05/2026)")
        self.entry_teslim_tarihi.grid(row=row, column=1, sticky="ew", padx=20, pady=(10, 5))
        self.entry_teslim_tarihi.bind("<KeyRelease>", self.format_date_input)
        
        row += 1
        ctk.CTkLabel(parent, text="Müşteri:", font=Fontlar.BODY_BOLD).grid(row=row, column=0, **padding)
        self.combo_musteri = ctk.CTkComboBox(parent, font=Fontlar.BODY, values=["Seçiniz..."])
        self.combo_musteri.grid(row=row, column=1, sticky="ew", padx=20, pady=(10, 5))
        
        row += 1
        ctk.CTkLabel(parent, text="Malzeme:", font=Fontlar.BODY_BOLD).grid(row=row, column=0, **padding)
        self.combo_malzeme = ctk.CTkComboBox(parent, font=Fontlar.BODY, values=["Seçiniz..."], command=self.malzeme_secildi)
        self.combo_malzeme.grid(row=row, column=1, sticky="ew", padx=20, pady=(10, 5))
        
        row += 1
        ctk.CTkLabel(parent, text="Miktar:", font=Fontlar.BODY_BOLD).grid(row=row, column=0, **padding)
        self.entry_miktar = ctk.CTkEntry(parent, font=Fontlar.BODY)
        self.entry_miktar.insert(0, "1")
        self.entry_miktar.grid(row=row, column=1, sticky="ew", padx=20, pady=(10, 5))
        
        row += 1
        ctk.CTkLabel(parent, text="İşlem (Makine):", font=Fontlar.BODY_BOLD).grid(row=row, column=0, **padding)
        self.combo_islem = ctk.CTkComboBox(parent, font=Fontlar.BODY, values=["Seçiniz..."])
        self.combo_islem.grid(row=row, column=1, sticky="ew", padx=20, pady=(10, 5))
        
        row += 1
        ctk.CTkLabel(parent, text="Makine Süresi (Saat):", font=Fontlar.BODY_BOLD).grid(row=row, column=0, **padding)
        self.entry_sure = ctk.CTkEntry(parent, font=Fontlar.BODY)
        self.entry_sure.insert(0, "1")
        self.entry_sure.grid(row=row, column=1, sticky="ew", padx=20, pady=(10, 5))
        
        row += 1
        ctk.CTkLabel(parent, text="Fire Oranı (%):", font=Fontlar.BODY_BOLD).grid(row=row, column=0, **padding)
        self.entry_fire = ctk.CTkEntry(parent, font=Fontlar.BODY)
        self.entry_fire.insert(0, "0")
        self.entry_fire.grid(row=row, column=1, sticky="ew", padx=20, pady=(10, 5))
        
        row += 1
        ctk.CTkLabel(parent, text="Kar Tipi:", font=Fontlar.BODY_BOLD).grid(row=row, column=0, **padding)
        self.combo_kar_tipi = ctk.CTkComboBox(parent, font=Fontlar.BODY, values=["Yüzdesel", "Sabit"])
        self.combo_kar_tipi.grid(row=row, column=1, sticky="ew", padx=20, pady=(10, 5))
        
        row += 1
        ctk.CTkLabel(parent, text="Kar Değeri:", font=Fontlar.BODY_BOLD).grid(row=row, column=0, **padding)
        self.entry_kar = ctk.CTkEntry(parent, font=Fontlar.BODY)
        self.entry_kar.insert(0, "20")
        self.entry_kar.grid(row=row, column=1, sticky="ew", padx=20, pady=(10, 5))
        
        row += 1
        ctk.CTkLabel(parent, text="Manuel İndirim (₺):", font=Fontlar.BODY_BOLD).grid(row=row, column=0, **padding)
        self.entry_indirim = ctk.CTkEntry(parent, font=Fontlar.BODY)
        self.entry_indirim.insert(0, "0")
        self.entry_indirim.grid(row=row, column=1, sticky="ew", padx=20, pady=(10, 5))
        
        row += 1
        ctk.CTkLabel(parent, text="Ek Gider (₺):", font=Fontlar.BODY_BOLD).grid(row=row, column=0, **padding)
        self.entry_ekgider = ctk.CTkEntry(parent, font=Fontlar.BODY)
        self.entry_ekgider.insert(0, "0")
        self.entry_ekgider.grid(row=row, column=1, sticky="ew", padx=20, pady=(10, 5))

        row += 1
        self.btn_hesapla = ctk.CTkButton(parent, text="Hesapla ve Görüntüle", font=Fontlar.BODY_BOLD, fg_color=Renkler.INFO, hover_color=Renkler.PRIMARY_HOVER, command=self.hesapla)
        self.btn_hesapla.grid(row=row, column=0, columnspan=2, sticky="ew", padx=20, pady=30)

    def format_date_input(self, event):
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Up", "Down", "Tab", "Shift_L", "Shift_R", "Control_L", "Control_R"):
            return
            
        text = self.entry_teslim_tarihi.get()
        digits = "".join([c for c in text if c.isdigit()])
        
        formatted = ""
        if len(digits) > 0:
            formatted += digits[:2]
        if len(digits) > 2:
            formatted += "/" + digits[2:4]
        if len(digits) > 4:
            formatted += "/" + digits[4:8]
            
        if text != formatted:
            cursor_idx = self.entry_teslim_tarihi.index("insert")
            self.entry_teslim_tarihi.delete(0, "end")
            self.entry_teslim_tarihi.insert(0, formatted)
            
            if len(text) < len(formatted):
                self.entry_teslim_tarihi.icursor(cursor_idx + 1)
            else:
                self.entry_teslim_tarihi.icursor(cursor_idx)

    def build_summary(self, parent):
        ctk.CTkLabel(parent, text="Hesap Özeti", font=Fontlar.H2, text_color=Renkler.TEXT_DARK).pack(pady=(30, 20))
        
        self.lbl_malzeme_maliyeti = self.add_summary_row(parent, "Malzeme Maliyeti:")
        self.lbl_makine_maliyeti = self.add_summary_row(parent, "Makine Maliyeti:")
        self.lbl_net_maliyet = self.add_summary_row(parent, "Net Maliyet:", bold=True)
        self.add_divider(parent)
        
        self.lbl_kar_tutari = self.add_summary_row(parent, "Kar Tutarı:")
        self.lbl_teklif_tutari = self.add_summary_row(parent, "Teklif Tutarı:", bold=True)
        self.lbl_indirim = self.add_summary_row(parent, "Manuel İndirim:")
        self.add_divider(parent)
        
        self.lbl_son_tutar = self.add_summary_row(parent, "Son Teklif Tutarı:", color=Renkler.PRIMARY, size=Fontlar.H2)
        
        self.add_divider(parent)
        self.lbl_hurda = self.add_summary_row(parent, "Tahmini Hurda Değeri:", color=Renkler.WARNING)
        
        self.btn_kaydet = ctk.CTkButton(parent, text="Teklifi Kaydet (Beklemede)", font=Fontlar.BODY_BOLD, fg_color=Renkler.SUCCESS, hover_color="#059669", height=45, command=self.teklif_kaydet)
        self.btn_kaydet.pack(fill="x", padx=20, pady=(30, 20), side="bottom")
        
    def add_summary_row(self, parent, label_text, bold=False, color=Renkler.TEXT_DARK, size=Fontlar.BODY):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=8)
        
        font = Fontlar.BODY_BOLD if bold else Fontlar.BODY
        if size != Fontlar.BODY: font = size
        
        ctk.CTkLabel(frame, text=label_text, font=Fontlar.BODY, text_color=Renkler.TEXT_GRAY).pack(side="left")
        val_label = ctk.CTkLabel(frame, text="0.00 ₺", font=font, text_color=color)
        val_label.pack(side="right")
        return val_label
        
    def add_divider(self, parent):
        ayrac = ctk.CTkFrame(parent, fg_color=Renkler.BORDER, height=1)
        ayrac.pack(fill="x", padx=20, pady=15)
        
    def load_combobox_data(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        user_id = self.current_user["id"]
        
        # Müşteriler
        cursor.execute("SELECT id, firma_adi FROM musteriler WHERE kullanici_id = ?", (user_id,))
        self.musteriler = [{"id": r["id"], "ad": r["firma_adi"]} for r in cursor.fetchall()]
        musteri_vals = [m["ad"] for m in self.musteriler] if self.musteriler else ["Müşteri Yok"]
        self.combo_musteri.configure(values=musteri_vals)
        if self.musteriler: self.combo_musteri.set(musteri_vals[0])
        
        # Malzemeler
        cursor.execute("SELECT * FROM malzemeler WHERE kullanici_id = ? AND aktif = 1", (user_id,))
        self.malzemeler = [dict(r) for r in cursor.fetchall()]
        malzeme_vals = [m["malzeme_adi"] for m in self.malzemeler] if self.malzemeler else ["Malzeme Yok"]
        self.combo_malzeme.configure(values=malzeme_vals)
        if self.malzemeler: self.combo_malzeme.set(malzeme_vals[0])
        
        # İşlemler
        cursor.execute("SELECT * FROM islemler WHERE kullanici_id = ?", (user_id,))
        self.islemler = [dict(r) for r in cursor.fetchall()]
        islem_vals = [i["islem_adi"] for i in self.islemler] if self.islemler else ["İşlem Yok"]
        self.combo_islem.configure(values=islem_vals)
        if self.islemler: self.combo_islem.set(islem_vals[0])
        
        conn.close()

    def get_selected_malzeme(self):
        secili = self.combo_malzeme.get()
        for m in self.malzemeler:
            if m["malzeme_adi"] == secili: return m
        return None

    def get_selected_islem(self):
        secili = self.combo_islem.get()
        for i in self.islemler:
            if i["islem_adi"] == secili: return i
        return None

    def malzeme_secildi(self, choice):
        m = self.get_selected_malzeme()
        if m:
            self.entry_fire.delete(0, "end")
            self.entry_fire.insert(0, str(m.get("varsayilan_fire_orani") or 0))

    def hesapla(self):
        try:
            miktar = float(self.entry_miktar.get() or 0)
            sure = float(self.entry_sure.get() or 0)
            fire_orani = float(self.entry_fire.get() or 0)
            kar_degeri = float(self.entry_kar.get() or 0)
            indirim = float(self.entry_indirim.get() or 0)
            ek_gider = float(self.entry_ekgider.get() or 0)
            kar_tipi = self.combo_kar_tipi.get()
            
            malzeme = self.get_selected_malzeme()
            islem = self.get_selected_islem()
            
            m_fiyat = malzeme["birim_fiyat"] if malzeme else 0
            h_fiyat = malzeme["hurda_birim_fiyati"] if malzeme else 0
            i_fiyat = islem["saatlik_makine_maliyeti"] if islem else 0
            
            malzeme_maliyeti = Hesaplayici.malzeme_maliyeti_hesapla(miktar, m_fiyat)
            makine_maliyeti = Hesaplayici.makine_maliyeti_hesapla(sure, i_fiyat)
            hurda_degeri = Hesaplayici.hurda_degeri_hesapla(miktar, fire_orani, h_fiyat)
            
            sonuclar = Hesaplayici.teklif_hesapla(
                malzeme_maliyeti=malzeme_maliyeti,
                makine_maliyeti=makine_maliyeti,
                ek_gider=ek_gider,
                kar_tipi=kar_tipi,
                kar_degeri=kar_degeri,
                manuel_indirim=indirim
            )
            
            self.lbl_malzeme_maliyeti.configure(text=f"{malzeme_maliyeti:,.2f} ₺")
            self.lbl_makine_maliyeti.configure(text=f"{makine_maliyeti:,.2f} ₺")
            self.lbl_net_maliyet.configure(text=f"{sonuclar['net_maliyet']:,.2f} ₺")
            self.lbl_kar_tutari.configure(text=f"{sonuclar['kar_tutari']:,.2f} ₺")
            self.lbl_teklif_tutari.configure(text=f"{sonuclar['teklif_tutari']:,.2f} ₺")
            self.lbl_indirim.configure(text=f"{indirim:,.2f} ₺")
            self.lbl_son_tutar.configure(text=f"{sonuclar['son_tutar']:,.2f} ₺")
            self.lbl_hurda.configure(text=f"{hurda_degeri:,.2f} ₺")
            
            return {
                "malzeme_maliyeti": malzeme_maliyeti,
                "makine_maliyeti": makine_maliyeti,
                "net_maliyet": sonuclar['net_maliyet'],
                "kar_tutari": sonuclar['kar_tutari'],
                "teklif_tutari": sonuclar['teklif_tutari'],
                "son_tutar": sonuclar['son_tutar'],
                "hurda_degeri": hurda_degeri,
                "kar_tipi": kar_tipi,
                "kar_orani": kar_degeri if kar_tipi == "Yüzdesel" else 0,
                "sabit_kar": kar_degeri if kar_tipi == "Sabit" else 0,
                "indirim": indirim,
                "ek_gider": ek_gider,
                "miktar": miktar,
                "sure": sure,
                "fire": fire_orani,
                "malzeme": malzeme,
                "islem": islem
            }
            
        except ValueError:
            print("Hata: Sayısal değerleri doğru giriniz.")
            return None

    def reset_form(self):
        self.edit_teklif_id = None
        if hasattr(self, 'lbl_title'):
            self.lbl_title.configure(text="Yeni Teklif Oluştur")
        if hasattr(self, 'btn_kaydet'):
            self.btn_kaydet.configure(text="Teklifi Kaydet (Beklemede)")
            
        self.entry_baslik.delete(0, "end")
        self.entry_teslim_tarihi.delete(0, "end")
        self.entry_miktar.delete(0, "end")
        self.entry_miktar.insert(0, "1")
        self.entry_sure.delete(0, "end")
        self.entry_sure.insert(0, "1")
        self.entry_fire.delete(0, "end")
        self.entry_fire.insert(0, "0")
        self.entry_kar.delete(0, "end")
        self.entry_kar.insert(0, "20")
        self.entry_indirim.delete(0, "end")
        self.entry_indirim.insert(0, "0")
        self.entry_ekgider.delete(0, "end")
        self.entry_ekgider.insert(0, "0")
        self.combo_kar_tipi.set("Yüzdesel")
        
        if self.musteriler: self.combo_musteri.set(self.musteriler[0]["ad"])
        if self.malzemeler: self.combo_malzeme.set(self.malzemeler[0]["malzeme_adi"])
        if self.islemler: self.combo_islem.set(self.islemler[0]["islem_adi"])
        
        self.hesapla()

    def load_teklif_for_edit(self, teklif_id):
        self.edit_teklif_id = teklif_id
        self.lbl_title.configure(text="Teklifi Düzenle")
        self.btn_kaydet.configure(text="Teklifi Güncelle")
        
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teklifler WHERE id = ?", (teklif_id,))
        t = cursor.fetchone()
        
        cursor.execute("SELECT * FROM teklif_kalemleri WHERE teklif_id = ?", (teklif_id,))
        k = cursor.fetchone()
        conn.close()
        
        if not t: return
        
        self.entry_baslik.delete(0, "end")
        self.entry_baslik.insert(0, t["baslik"] or "")
        
        self.entry_teslim_tarihi.delete(0, "end")
        if t["teslim_tarihi"]:
            try:
                dt = datetime.strptime(t["teslim_tarihi"], "%Y-%m-%d")
                self.entry_teslim_tarihi.insert(0, dt.strftime("%d/%m/%Y"))
            except Exception:
                self.entry_teslim_tarihi.insert(0, t["teslim_tarihi"] or "")
        else:
            self.entry_teslim_tarihi.insert(0, "")
        
        for m in self.musteriler:
            if m["id"] == t["musteri_id"]:
                self.combo_musteri.set(m["ad"])
                break
                
        if k:
            for mat in self.malzemeler:
                if mat["id"] == k["malzeme_id"]:
                    self.combo_malzeme.set(mat["malzeme_adi"])
                    break
            for op in self.islemler:
                if op["id"] == k["islem_id"]:
                    self.combo_islem.set(op["islem_adi"])
                    break
                    
            self.entry_miktar.delete(0, "end")
            self.entry_miktar.insert(0, str(k["miktar"]))
            
            self.entry_sure.delete(0, "end")
            self.entry_sure.insert(0, str(k["makine_suresi"]))
            
            self.entry_fire.delete(0, "end")
            self.entry_fire.insert(0, str(k["fire_orani"]))
            
        self.combo_kar_tipi.set(t["kar_tipi"])
        self.entry_kar.delete(0, "end")
        self.entry_kar.insert(0, str(t["kar_orani"] if t["kar_tipi"] == "Yüzdesel" else t["sabit_kar"]))
        
        self.entry_indirim.delete(0, "end")
        self.entry_indirim.insert(0, str(t["manuel_indirim"] or 0))
        
        self.entry_ekgider.delete(0, "end")
        self.entry_ekgider.insert(0, str(t["ek_gider"] or 0))
        
        self.hesapla()

    def teklif_kaydet(self):
        baslik = self.entry_baslik.get().strip()
        secili_musteri_adi = self.combo_musteri.get()
        
        teslim_tarihi_val = self.entry_teslim_tarihi.get().strip()
        if not teslim_tarihi_val:
            teslim_tarihi_val = None
        else:
            try:
                if "/" in teslim_tarihi_val:
                    parsed_date = datetime.strptime(teslim_tarihi_val, "%d/%m/%Y")
                elif "." in teslim_tarihi_val:
                    parsed_date = datetime.strptime(teslim_tarihi_val, "%d.%m.%Y")
                else:
                    parsed_date = datetime.strptime(teslim_tarihi_val, "%Y-%m-%d")
                teslim_tarihi_val = parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                from tkinter import messagebox
                messagebox.showerror("Hata", "Lütfen teslimat tarihini doğru formatta girin (Örn: 30/05/2026)")
                return

        musteri_id = None
        for m in self.musteriler:
            if m["ad"] == secili_musteri_adi:
                musteri_id = m["id"]
                break
                
        if not baslik or not musteri_id:
            return
            
        hesap = self.hesapla()
        if not hesap: return
        
        conn = self.db.connect()
        cursor = conn.cursor()
        
        if self.edit_teklif_id:
            # Düzenleme modu: UPDATE yap
            cursor.execute('''
                UPDATE teklifler SET
                    musteri_id = ?, baslik = ?,
                    malzeme_maliyeti = ?, makine_maliyeti = ?, ek_gider = ?, net_maliyet = ?,
                    kar_tipi = ?, kar_orani = ?, sabit_kar = ?, kar_tutari = ?, teklif_tutari = ?,
                    tahmini_hurda_degeri = ?, manuel_indirim = ?, son_tutar = ?, teslim_tarihi = ?
                WHERE id = ? AND kullanici_id = ?
            ''', (
                musteri_id, baslik,
                hesap["malzeme_maliyeti"], hesap["makine_maliyeti"], hesap["ek_gider"], hesap["net_maliyet"],
                hesap["kar_tipi"], hesap["kar_orani"], hesap["sabit_kar"], hesap["kar_tutari"], hesap["teklif_tutari"],
                hesap["hurda_degeri"], hesap["indirim"], hesap["son_tutar"], teslim_tarihi_val,
                self.edit_teklif_id, self.current_user["id"]
            ))
            
            cursor.execute("DELETE FROM teklif_kalemleri WHERE teklif_id = ?", (self.edit_teklif_id,))
            teklif_id = self.edit_teklif_id
        else:
            # Yeni kayıt modu: INSERT yap
            tarih_str = datetime.now().strftime("%Y%m%d%H%M")
            teklif_no = f"TEK-{tarih_str}"
            bugun = datetime.now().strftime("%Y-%m-%d")
            
            cursor.execute('''
                INSERT INTO teklifler (
                    kullanici_id, musteri_id, teklif_no, baslik, durum, para_birimi,
                    malzeme_maliyeti, makine_maliyeti, ek_gider, net_maliyet,
                    kar_tipi, kar_orani, sabit_kar, kar_tutari, teklif_tutari,
                    tahmini_hurda_degeri, manuel_indirim, son_tutar, olusturma_tarihi, teslim_tarihi
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.current_user["id"], musteri_id, teklif_no, baslik, "Beklemede", "TRY",
                hesap["malzeme_maliyeti"], hesap["makine_maliyeti"], hesap["ek_gider"], hesap["net_maliyet"],
                hesap["kar_tipi"], hesap["kar_orani"], hesap["sabit_kar"], hesap["kar_tutari"], hesap["teklif_tutari"],
                hesap["hurda_degeri"], hesap["indirim"], hesap["son_tutar"], bugun, teslim_tarihi_val
            ))
            teklif_id = cursor.lastrowid
        
        if hesap["malzeme"] and hesap["islem"]:
            cursor.execute('''
                INSERT INTO teklif_kalemleri (
                    teklif_id, malzeme_id, islem_id, malzeme_adi, islem_adi,
                    miktar, birim, birim_fiyat, fire_orani, fire_miktari,
                    hurda_birim_fiyati, tahmini_hurda_degeri, makine_suresi,
                    makine_saat_ucreti, malzeme_maliyeti, makine_maliyeti, kalem_maliyeti
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                teklif_id, hesap["malzeme"]["id"], hesap["islem"]["id"], 
                hesap["malzeme"]["malzeme_adi"], hesap["islem"]["islem_adi"],
                hesap["miktar"], hesap["malzeme"]["birim"], hesap["malzeme"]["birim_fiyat"],
                hesap["fire"], hesap["miktar"] * (hesap["fire"]/100),
                hesap["malzeme"]["hurda_birim_fiyati"], hesap["hurda_degeri"],
                hesap["sure"], hesap["islem"]["saatlik_makine_maliyeti"],
                hesap["malzeme_maliyeti"], hesap["makine_maliyeti"], hesap["net_maliyet"]
            ))
            
        conn.commit()
        conn.close()
        
        self.reset_form()
        self.geri_don()

    def geri_don(self):
        if hasattr(self.master.master, 'show_screen'):
            self.master.master.show_screen("teklifler")

    def apply_theme(self):
        self.configure(fg_color=Renkler.BG_LIGHT)
        try:
            self.form_frame.configure(fg_color=Renkler.CARD_BG)
            self.summary_frame.configure(fg_color=Renkler.CARD_BG)
        except Exception:
            pass
        self._needs_refresh = True
        is_active = (hasattr(self.master, "master") and getattr(self.master.master, "current_screen", None) == self)
        if is_active:
            self.load_data()
