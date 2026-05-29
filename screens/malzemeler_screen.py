import customtkinter as ctk
from tema import Renkler, Fontlar
import database
from tkinter import messagebox

class MalzemelerScreen(ctk.CTkFrame):
    def __init__(self, master, current_user):
        super().__init__(master, fg_color=Renkler.BG_LIGHT)
        self.current_user = current_user
        self.db = database.Database()
        self._needs_refresh = False
        
        self.secili_malzeme_id = None
        
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # ── ÜST BAŞLIK ALANI ──────────────────────────────────────────────────
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(30, 15))
        
        ctk.CTkLabel(
            self.header_frame, 
            text="Malzeme Deposu", 
            font=Fontlar.H1, 
            text_color=Renkler.TEXT_DARK
        ).pack(side="left")

        # Arama Kutusu
        self.entry_ara = ctk.CTkEntry(self.header_frame, placeholder_text="Malzeme Ara...", width=220, font=Fontlar.SMALL)
        self.entry_ara.pack(side="right", padx=10)
        self.entry_ara.bind("<KeyRelease>", lambda e: self.load_data())

        # ── ANA İÇERİK ALANI (BÖLÜNMÜŞ DÜZEN) ─────────────────────────────────
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        self.content_frame.grid_columnconfigure(0, weight=6) # Sol Liste
        self.content_frame.grid_columnconfigure(1, weight=4) # Sağ Form
        self.content_frame.grid_rowconfigure(0, weight=1)

        # ── SOL: TABLO / LİSTE KARTI ──────────────────────────────────────────
        self.left_card = ctk.CTkFrame(self.content_frame, fg_color=Renkler.CARD_BG, corner_radius=10)
        self.left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        # Tablo Başlıkları
        self.table_header = ctk.CTkFrame(self.left_card, fg_color="transparent")
        self.table_header.pack(fill="x", padx=15, pady=10)
        self.table_header.grid_columnconfigure((0, 1, 2, 3), weight=2)
        self.table_header.grid_columnconfigure(4, weight=1)
        
        ctk.CTkLabel(self.table_header, text="Malzeme Adı", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_GRAY).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(self.table_header, text="Birim Fiyat", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_GRAY).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(self.table_header, text="Hurda Fiyatı", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_GRAY).grid(row=0, column=2, sticky="w")
        ctk.CTkLabel(self.table_header, text="D. Fire (%)", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_GRAY).grid(row=0, column=3, sticky="w")
        ctk.CTkLabel(self.table_header, text="İşlemler", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_GRAY).grid(row=0, column=4, sticky="e")
        
        ctk.CTkFrame(self.left_card, fg_color=Renkler.BORDER, height=1).pack(fill="x", padx=15)

        # Kaydırılabilir Liste
        self.list_scroll = ctk.CTkScrollableFrame(self.left_card, fg_color="transparent")
        self.list_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # ── SAĞ: EKLE / DÜZENLE FORMU ─────────────────────────────────────────
        self.right_card = ctk.CTkFrame(self.content_frame, fg_color=Renkler.CARD_BG, corner_radius=10)
        self.right_card.grid(row=0, column=1, sticky="nsew")
        
        self.lbl_form_title = ctk.CTkLabel(self.right_card, text="Yeni Malzeme Ekle", font=Fontlar.H3, text_color=Renkler.TEXT_DARK)
        self.lbl_form_title.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Kaydırılabilir Form Gövdesi
        self.form_scroll = ctk.CTkScrollableFrame(self.right_card, fg_color="transparent")
        self.form_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.entry_ad = self.create_form_input(self.form_scroll, "Malzeme Adı:")
        
        # Birim (ComboBox)
        unit_frame = ctk.CTkFrame(self.form_scroll, fg_color="transparent")
        unit_frame.pack(fill="x", padx=15, pady=6)
        ctk.CTkLabel(unit_frame, text="Birim:", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK).pack(anchor="w", pady=(0, 2))
        self.combo_birim = ctk.CTkComboBox(unit_frame, values=["kg", "metre", "m²", "m³", "boy", "adet", "litre", "plaka"], font=Fontlar.SMALL, height=35)
        self.combo_birim.pack(fill="x")
        
        self.entry_fiyat = self.create_form_input(self.form_scroll, "Birim Fiyatı (₺):")
        self.entry_hurda_fiyat = self.create_form_input(self.form_scroll, "Hurda Birim Fiyatı (₺):")
        self.entry_fire = self.create_form_input(self.form_scroll, "Varsayılan Fire Oranı (%):")
        self.entry_aciklama = self.create_form_input(self.form_scroll, "Açıklama:")
        
        # Butonlar Paneli
        self.btn_panel = ctk.CTkFrame(self.right_card, fg_color="transparent")
        self.btn_panel.pack(fill="x", padx=20, pady=20, side="bottom")
        
        self.btn_kaydet = ctk.CTkButton(self.btn_panel, text="Kaydet", font=Fontlar.BODY_BOLD, fg_color=Renkler.PRIMARY, hover_color=Renkler.PRIMARY_HOVER, command=self.kaydet)
        self.btn_kaydet.pack(fill="x", pady=4)
        
        self.btn_sil = ctk.CTkButton(self.btn_panel, text="Sil", font=Fontlar.BODY_BOLD, fg_color=Renkler.ERROR, hover_color="#DC2626", command=self.sil)
        
        self.btn_temizle = ctk.CTkButton(self.btn_panel, text="Yeni Malzeme (Formu Temizle)", font=Fontlar.SMALL_BOLD, fg_color="transparent", text_color=Renkler.TEXT_GRAY, hover_color=Renkler.BORDER, command=self.form_temizle)
        self.btn_temizle.pack(fill="x", pady=4)

    def create_form_input(self, parent, label_text):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=6)
        
        ctk.CTkLabel(frame, text=label_text, font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK).pack(anchor="w", pady=(0, 2))
        entry = ctk.CTkEntry(frame, font=Fontlar.SMALL, height=35)
        entry.pack(fill="x")
        return entry

    # ── VERİ İŞLEMLERİ ───────────────────────────────────────────────────────

    def load_data(self):
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
            
        arama_kelimesi = self.entry_ara.get().strip()
        
        conn = self.db.connect()
        cursor = conn.cursor()
        
        if arama_kelimesi:
            cursor.execute("""
                SELECT * FROM malzemeler 
                WHERE kullanici_id = ? AND aktif = 1 AND malzeme_adi LIKE ?
                ORDER BY malzeme_adi ASC
            """, (self.current_user["id"], f"%{arama_kelimesi}%"))
        else:
            cursor.execute("SELECT * FROM malzemeler WHERE kullanici_id = ? AND aktif = 1 ORDER BY malzeme_adi ASC", (self.current_user["id"],))
            
        malzemeler = cursor.fetchall()
        conn.close()
        
        if not malzemeler:
            ctk.CTkLabel(self.list_scroll, text="Kayıtlı malzeme bulunamadı.", font=Fontlar.BODY, text_color=Renkler.TEXT_GRAY).pack(pady=40)
            return
            
        for m in malzemeler:
            satir = ctk.CTkFrame(self.list_scroll, fg_color="transparent")
            satir.pack(fill="x", pady=2, padx=5)
            
            # Sol bilgi bloğu
            info_frame = ctk.CTkFrame(satir, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True)
            info_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
            
            lbl_ad = ctk.CTkLabel(info_frame, text=m["malzeme_adi"], font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK, anchor="w")
            lbl_ad.grid(row=0, column=0, sticky="w")
            
            lbl_fiyat = ctk.CTkLabel(info_frame, text=f"{m['birim_fiyat'] or 0.0:.2f} ₺ / {m['birim']}", font=Fontlar.SMALL, text_color=Renkler.TEXT_DARK, anchor="w")
            lbl_fiyat.grid(row=0, column=1, sticky="w", padx=10)
            
            lbl_hurda = ctk.CTkLabel(info_frame, text=f"{m['hurda_birim_fiyati'] or 0.0:.2f} ₺", font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY, anchor="w")
            lbl_hurda.grid(row=0, column=2, sticky="w", padx=10)
            
            lbl_fire = ctk.CTkLabel(info_frame, text=f"% {m['varsayilan_fire_orani'] or 0}", font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY, anchor="w")
            lbl_fire.grid(row=0, column=3, sticky="w", padx=10)
            
            # Sağ buton bloğu (pack ile, her zaman görünür)
            btn_frame = ctk.CTkFrame(satir, fg_color="transparent")
            btn_frame.pack(side="right", padx=5)
            
            btn_edit = ctk.CTkButton(
                btn_frame, 
                text="Düzenle", 
                font=Fontlar.SMALL, 
                fg_color=Renkler.PRIMARY, 
                hover_color=Renkler.PRIMARY_HOVER,
                width=65,
                height=26,
                command=lambda mat=dict(m): self.malzeme_sec(mat)
            )
            btn_edit.pack(side="left", padx=2)
            
            btn_delete = ctk.CTkButton(
                btn_frame, 
                text="Sil", 
                font=Fontlar.SMALL_BOLD, 
                fg_color=Renkler.ERROR, 
                hover_color="#DC2626",
                width=45,
                height=26,
                command=lambda mat=dict(m): self.sil_onayla(mat)
            )
            btn_delete.pack(side="left", padx=2)
            
            ctk.CTkFrame(self.list_scroll, fg_color=Renkler.BORDER, height=1).pack(fill="x", pady=1)

    def malzeme_sec(self, malzeme):
        self.secili_malzeme_id = malzeme["id"]
        self.lbl_form_title.configure(text="Malzemeyi Düzenle")
        
        self.entry_ad.delete(0, "end")
        self.entry_ad.insert(0, malzeme["malzeme_adi"] or "")
        
        self.combo_birim.set(malzeme["birim"] or "kg")
        
        self.entry_fiyat.delete(0, "end")
        self.entry_fiyat.insert(0, str(malzeme["birim_fiyat"] or 0.0))
        
        self.entry_hurda_fiyat.delete(0, "end")
        self.entry_hurda_fiyat.insert(0, str(malzeme["hurda_birim_fiyati"] or 0.0))
        
        self.entry_fire.delete(0, "end")
        self.entry_fire.insert(0, str(malzeme["varsayilan_fire_orani"] or 0))
        
        self.entry_aciklama.delete(0, "end")
        self.entry_aciklama.insert(0, malzeme["aciklama"] or "")
        
        self.btn_sil.pack(fill="x", pady=4, before=self.btn_temizle)

    def form_temizle(self):
        self.secili_malzeme_id = None
        self.lbl_form_title.configure(text="Yeni Malzeme Ekle")
        
        self.entry_ad.delete(0, "end")
        self.combo_birim.set("kg")
        self.entry_fiyat.delete(0, "end")
        self.entry_hurda_fiyat.delete(0, "end")
        self.entry_fire.delete(0, "end")
        self.entry_aciklama.delete(0, "end")
        
        self.btn_sil.pack_forget()

    def kaydet(self):
        ad = self.entry_ad.get().strip()
        birim = self.combo_birim.get()
        fiyat = self.entry_fiyat.get().strip() or "0"
        hurda_fiyat = self.entry_hurda_fiyat.get().strip() or "0"
        fire = self.entry_fire.get().strip() or "0"
        aciklama = self.entry_aciklama.get().strip()
        
        if not ad:
            return
            
        try:
            fiyat = float(fiyat)
            hurda_fiyat = float(hurda_fiyat)
            fire = int(fire)
        except ValueError:
            return
            
        conn = self.db.connect()
        cursor = conn.cursor()
        
        if self.secili_malzeme_id:
            cursor.execute("""
                UPDATE malzemeler 
                SET malzeme_adi = ?, birim = ?, birim_fiyat = ?, hurda_birim_fiyati = ?, varsayilan_fire_orani = ?, aciklama = ?
                WHERE id = ? AND kullanici_id = ?
            """, (ad, birim, fiyat, hurda_fiyat, fire, aciklama, self.secili_malzeme_id, self.current_user["id"]))
        else:
            cursor.execute("""
                INSERT INTO malzemeler (kullanici_id, malzeme_adi, birim, birim_fiyat, hurda_birim_fiyati, varsayilan_fire_orani, aciklama, aktif)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, (self.current_user["id"], ad, birim, fiyat, hurda_fiyat, fire, aciklama))
            
        conn.commit()
        conn.close()
        
        self.form_temizle()
        self.load_data()
        
        # Diğer sayfaların önbelleklerini tetikle
        self.tetikle_sayfa_guncellemeleri()

    def sil_onayla(self, malzeme):
        confirm = messagebox.askyesno(
            "Silme Onayı", 
            f"'{malzeme['malzeme_adi']}' malzemesini silmek istediğinize emin misiniz?"
        )
        if confirm:
            self.sil_islemi(malzeme["id"])

    def sil(self):
        if not self.secili_malzeme_id:
            return
        # Seçili malzemeyi veritabanından sorgulayıp bilgilerini alalım
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM malzemeler WHERE id = ?", (self.secili_malzeme_id,))
        m = cursor.fetchone()
        conn.close()
        if m:
            self.sil_onayla(dict(m))

    def sil_islemi(self, malzeme_id):
        try:
            durum, mesaj = self.db.malzeme_sil(malzeme_id, self.current_user["id"])
            
            if durum == "hata":
                messagebox.showerror("Hata", mesaj)
            else:
                messagebox.showinfo("Başarılı", mesaj)
                
            self.form_temizle()
            self.load_data()
            self.tetikle_sayfa_guncellemeleri()
            
        except Exception as e:
            messagebox.showerror("Sistem Hatası", f"Beklenmeyen bir hata oluştu: {e}")

    def tetikle_sayfa_guncellemeleri(self):
        # Dashboard ve Yeni Teklif sayfalarının önbelleğelerini de aninda tazeleyelim
        if hasattr(self.master.master, 'screens'):
            screens = self.master.master.screens
            if "dashboard" in screens and hasattr(screens["dashboard"], "_needs_refresh"):
                screens["dashboard"]._needs_refresh = True
            if "yeni_teklif" in screens and hasattr(screens["yeni_teklif"], "_needs_refresh"):
                screens["yeni_teklif"]._needs_refresh = True

    def apply_theme(self):
        """Tema değişiminde ana renkleri günceller."""
        self.configure(fg_color=Renkler.BG_LIGHT)
        try:
            self.left_card.configure(fg_color=Renkler.CARD_BG)
            self.right_card.configure(fg_color=Renkler.CARD_BG)
            self.lbl_form_title.configure(text_color=Renkler.TEXT_DARK)
        except Exception:
            pass
        self._needs_refresh = True
        is_active = (hasattr(self.master, "master") and getattr(self.master.master, "current_screen", None) == self)
        if is_active:
            self.load_data()
