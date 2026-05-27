import customtkinter as ctk
from tema import Renkler, Fontlar
import database

class MusterilerScreen(ctk.CTkFrame):
    def __init__(self, master, current_user):
        super().__init__(master, fg_color=Renkler.BG_LIGHT)
        self.current_user = current_user
        self.db = database.Database()
        self._needs_refresh = False
        
        # Seçili olan müşterinin ID'sini tutar (düzenleme/silme için)
        self.secili_musteri_id = None
        
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # ── ÜST BAŞLIK ALANI ──────────────────────────────────────────────────
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(30, 15))
        
        ctk.CTkLabel(
            self.header_frame, 
            text="Müşteri Yönetimi", 
            font=Fontlar.H1, 
            text_color=Renkler.TEXT_DARK
        ).pack(side="left")

        # Arama Kutusu
        self.entry_ara = ctk.CTkEntry(self.header_frame, placeholder_text="Firma veya Yetkili Ara...", width=220, font=Fontlar.SMALL)
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
        self.table_header.grid_columnconfigure((0, 1, 2), weight=1)
        
        ctk.CTkLabel(self.table_header, text="Firma Adı", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_GRAY).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(self.table_header, text="Yetkili Kişi", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_GRAY).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(self.table_header, text="Telefon", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_GRAY).grid(row=0, column=2, sticky="w")
        
        ctk.CTkFrame(self.left_card, fg_color=Renkler.BORDER, height=1).pack(fill="x", padx=15)

        # Kaydırılabilir Liste
        self.list_scroll = ctk.CTkScrollableFrame(self.left_card, fg_color="transparent")
        self.list_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # ── SAĞ: EKLE / DÜZENLE FORMU ─────────────────────────────────────────
        self.right_card = ctk.CTkFrame(self.content_frame, fg_color=Renkler.CARD_BG, corner_radius=10)
        self.right_card.grid(row=0, column=1, sticky="nsew")
        
        self.lbl_form_title = ctk.CTkLabel(self.right_card, text="Yeni Müşteri Ekle", font=Fontlar.H3, text_color=Renkler.TEXT_DARK)
        self.lbl_form_title.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Kaydırılabilir Form Gövdesi (Form sığmazsa taşmasın)
        self.form_scroll = ctk.CTkScrollableFrame(self.right_card, fg_color="transparent")
        self.form_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.entry_firma = self.create_form_input(self.form_scroll, "Firma Adı:")
        self.entry_yetkili = self.create_form_input(self.form_scroll, "Yetkili Kişi:")
        self.entry_telefon = self.create_form_input(self.form_scroll, "Telefon:")
        self.entry_mail = self.create_form_input(self.form_scroll, "E-Posta:")
        self.entry_vergi = self.create_form_input(self.form_scroll, "Vergi No:")
        self.entry_adres = self.create_form_input(self.form_scroll, "Adres:")
        self.entry_notlar = self.create_form_input(self.form_scroll, "Notlar:")
        
        # Butonlar Paneli
        self.btn_panel = ctk.CTkFrame(self.right_card, fg_color="transparent")
        self.btn_panel.pack(fill="x", padx=20, pady=20, side="bottom")
        
        self.btn_kaydet = ctk.CTkButton(self.btn_panel, text="Kaydet", font=Fontlar.BODY_BOLD, fg_color=Renkler.PRIMARY, hover_color=Renkler.PRIMARY_HOVER, command=self.kaydet)
        self.btn_kaydet.pack(fill="x", pady=4)
        
        self.btn_sil = ctk.CTkButton(self.btn_panel, text="Sil", font=Fontlar.BODY_BOLD, fg_color=Renkler.ERROR, hover_color="#DC2626", command=self.sil)
        # Başlangıçta sil butonu gizli/aktif değil, sadece düzenleme modunda görünecek
        
        self.btn_temizle = ctk.CTkButton(self.btn_panel, text="Yeni Müşteri (Formu Temizle)", font=Fontlar.SMALL_BOLD, fg_color="transparent", text_color=Renkler.TEXT_GRAY, hover_color=Renkler.BORDER, command=self.form_temizle)
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
        # Sol listeyi temizle
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
            
        arama_kelimesi = self.entry_ara.get().strip()
        
        conn = self.db.connect()
        cursor = conn.cursor()
        
        if arama_kelimesi:
            cursor.execute("""
                SELECT * FROM musteriler 
                WHERE kullanici_id = ? AND (firma_adi LIKE ? OR yetkili_kisi LIKE ?)
                ORDER BY firma_adi ASC
            """, (self.current_user["id"], f"%{arama_kelimesi}%", f"%{arama_kelimesi}%"))
        else:
            cursor.execute("SELECT * FROM musteriler WHERE kullanici_id = ? ORDER BY firma_adi ASC", (self.current_user["id"],))
            
        musteriler = cursor.fetchall()
        conn.close()
        
        if not musteriler:
            ctk.CTkLabel(self.list_scroll, text="Kayıtlı müşteri bulunamadı.", font=Fontlar.BODY, text_color=Renkler.TEXT_GRAY).pack(pady=40)
            return
            
        for m in musteriler:
            satir = ctk.CTkFrame(self.list_scroll, fg_color="transparent")
            satir.pack(fill="x", pady=2, padx=5)
            satir.grid_columnconfigure((0, 1, 2), weight=1)
            
            # Satıra tıklanınca bilgileri forma dolduracak buton simülasyonu
            btn_firma = ctk.CTkButton(
                satir, 
                text=m["firma_adi"], 
                font=Fontlar.SMALL, 
                fg_color="transparent", 
                text_color=Renkler.TEXT_DARK, 
                hover_color=Renkler.BORDER,
                anchor="w",
                command=lambda cust=dict(m): self.musteri_sec(cust)
            )
            btn_firma.grid(row=0, column=0, sticky="ew")
            
            lbl_yetkili = ctk.CTkLabel(satir, text=m["yetkili_kisi"] or "-", font=Fontlar.SMALL, text_color=Renkler.TEXT_DARK, anchor="w")
            lbl_yetkili.grid(row=0, column=1, sticky="w", padx=10)
            
            lbl_tel = ctk.CTkLabel(satir, text=m["telefon"] or "-", font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY, anchor="w")
            lbl_tel.grid(row=0, column=2, sticky="w", padx=10)
            
            # İnce ayırıcı çizgi
            ctk.CTkFrame(self.list_scroll, fg_color=Renkler.BORDER, height=1).pack(fill="x", pady=2)

    def musteri_sec(self, musteri):
        self.secili_musteri_id = musteri["id"]
        self.lbl_form_title.configure(text="Müşteriyi Düzenle")
        
        # Formu doldur
        self.entry_firma.delete(0, "end")
        self.entry_firma.insert(0, musteri["firma_adi"] or "")
        
        self.entry_yetkili.delete(0, "end")
        self.entry_yetkili.insert(0, musteri["yetkili_kisi"] or "")
        
        self.entry_telefon.delete(0, "end")
        self.entry_telefon.insert(0, musteri["telefon"] or "")
        
        self.entry_mail.delete(0, "end")
        self.entry_mail.insert(0, musteri["mail"] or "")
        
        self.entry_vergi.delete(0, "end")
        self.entry_vergi.insert(0, musteri["vergi_no"] or "")
        
        self.entry_adres.delete(0, "end")
        self.entry_adres.insert(0, musteri["adres"] or "")
        
        self.entry_notlar.delete(0, "end")
        self.entry_notlar.insert(0, musteri["notlar"] or "")
        
        # Sil butonunu göster
        self.btn_sil.pack(fill="x", pady=4, before=self.btn_temizle)

    def form_temizle(self):
        self.secili_musteri_id = None
        self.lbl_form_title.configure(text="Yeni Müşteri Ekle")
        
        self.entry_firma.delete(0, "end")
        self.entry_yetkili.delete(0, "end")
        self.entry_telefon.delete(0, "end")
        self.entry_mail.delete(0, "end")
        self.entry_vergi.delete(0, "end")
        self.entry_adres.delete(0, "end")
        self.entry_notlar.delete(0, "end")
        
        # Sil butonunu gizle
        self.btn_sil.pack_forget()

    def kaydet(self):
        firma = self.entry_firma.get().strip()
        yetkili = self.entry_yetkili.get().strip()
        tel = self.entry_telefon.get().strip()
        mail = self.entry_mail.get().strip()
        vergi = self.entry_vergi.get().strip()
        adres = self.entry_adres.get().strip()
        notlar = self.entry_notlar.get().strip()
        
        if not firma:
            # Boş firma adı kaydedilemez
            return
            
        conn = self.db.connect()
        cursor = conn.cursor()
        
        if self.secili_musteri_id:
            # Düzenleme (Update)
            cursor.execute("""
                UPDATE musteriler 
                SET firma_adi = ?, yetkili_kisi = ?, telefon = ?, mail = ?, adres = ?, vergi_no = ?, notlar = ?
                WHERE id = ? AND kullanici_id = ?
            """, (firma, yetkili, tel, mail, adres, vergi, notlar, self.secili_musteri_id, self.current_user["id"]))
        else:
            # Yeni Kayıt (Insert)
            cursor.execute("""
                INSERT INTO musteriler (kullanici_id, firma_adi, yetkili_kisi, telefon, mail, adres, vergi_no, notlar)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (self.current_user["id"], firma, yetkili, tel, mail, adres, vergi, notlar))
            
        conn.commit()
        conn.close()
        
        self.form_temizle()
        self.load_data()

    def sil(self):
        if not self.secili_musteri_id:
            return
            
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM musteriler WHERE id = ? AND kullanici_id = ?", (self.secili_musteri_id, self.current_user["id"]))
        conn.commit()
        conn.close()
        
        self.form_temizle()
        self.load_data()

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
