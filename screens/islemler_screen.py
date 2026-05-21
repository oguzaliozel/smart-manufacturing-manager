import customtkinter as ctk
from tema import Renkler, Fontlar
import database

class IslemlerScreen(ctk.CTkFrame):
    def __init__(self, master, current_user):
        super().__init__(master, fg_color=Renkler.BG_LIGHT)
        self.current_user = current_user
        self.db = database.Database()
        
        self.secili_islem_id = None
        
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # ── ÜST BAŞLIK ALANI ──────────────────────────────────────────────────
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(30, 15))
        
        ctk.CTkLabel(
            self.header_frame, 
            text="İşlemler & Makineler", 
            font=Fontlar.H1, 
            text_color=Renkler.TEXT_DARK
        ).pack(side="left")

        # Arama Kutusu
        self.entry_ara = ctk.CTkEntry(self.header_frame, placeholder_text="İşlem veya Makine Ara...", width=220, font=Fontlar.SMALL)
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
        
        ctk.CTkLabel(self.table_header, text="İşlem / Makine Adı", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_GRAY).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(self.table_header, text="Saatlik Maliyet", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_GRAY).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(self.table_header, text="Varsayılan Fire (%)", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_GRAY).grid(row=0, column=2, sticky="w")
        
        ctk.CTkFrame(self.left_card, fg_color=Renkler.BORDER, height=1).pack(fill="x", padx=15)

        # Kaydırılabilir Liste
        self.list_scroll = ctk.CTkScrollableFrame(self.left_card, fg_color="transparent")
        self.list_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # ── SAĞ: EKLE / DÜZENLE FORMU ─────────────────────────────────────────
        self.right_card = ctk.CTkFrame(self.content_frame, fg_color=Renkler.CARD_BG, corner_radius=10)
        self.right_card.grid(row=0, column=1, sticky="nsew")
        
        self.lbl_form_title = ctk.CTkLabel(self.right_card, text="Yeni İşlem Ekle", font=Fontlar.H3, text_color=Renkler.TEXT_DARK)
        self.lbl_form_title.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Kaydırılabilir Form Gövdesi
        self.form_scroll = ctk.CTkScrollableFrame(self.right_card, fg_color="transparent")
        self.form_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.entry_ad = self.create_form_input(self.form_scroll, "İşlem / Makine Adı:")
        self.entry_maliyet = self.create_form_input(self.form_scroll, "Saatlik Makine Maliyeti (₺):")
        self.entry_fire = self.create_form_input(self.form_scroll, "Varsayılan Fire Oranı (%):")
        self.entry_aciklama = self.create_form_input(self.form_scroll, "Açıklama / Notlar:")
        
        # Butonlar Paneli
        self.btn_panel = ctk.CTkFrame(self.right_card, fg_color="transparent")
        self.btn_panel.pack(fill="x", padx=20, pady=20, side="bottom")
        
        self.btn_kaydet = ctk.CTkButton(self.btn_panel, text="Kaydet", font=Fontlar.BODY_BOLD, fg_color=Renkler.PRIMARY, hover_color=Renkler.PRIMARY_HOVER, command=self.kaydet)
        self.btn_kaydet.pack(fill="x", pady=4)
        
        self.btn_sil = ctk.CTkButton(self.btn_panel, text="Sil", font=Fontlar.BODY_BOLD, fg_color=Renkler.ERROR, hover_color="#DC2626", command=self.sil)
        
        self.btn_temizle = ctk.CTkButton(self.btn_panel, text="Yeni İşlem (Formu Temizle)", font=Fontlar.SMALL_BOLD, fg_color="transparent", text_color=Renkler.TEXT_GRAY, hover_color=Renkler.BORDER, command=self.form_temizle)
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
                SELECT * FROM islemler 
                WHERE kullanici_id = ? AND islem_adi LIKE ?
                ORDER BY islem_adi ASC
            """, (self.current_user["id"], f"%{arama_kelimesi}%"))
        else:
            cursor.execute("SELECT * FROM islemler WHERE kullanici_id = ? ORDER BY islem_adi ASC", (self.current_user["id"],))
            
        islemler = cursor.fetchall()
        conn.close()
        
        if not islemler:
            ctk.CTkLabel(self.list_scroll, text="Kayıtlı işlem bulunamadı.", font=Fontlar.BODY, text_color=Renkler.TEXT_GRAY).pack(pady=40)
            return
            
        for i in islemler:
            satir = ctk.CTkFrame(self.list_scroll, fg_color="transparent")
            satir.pack(fill="x", pady=2, padx=5)
            satir.grid_columnconfigure((0, 1, 2), weight=1)
            
            btn_ad = ctk.CTkButton(
                satir, 
                text=i["islem_adi"], 
                font=Fontlar.SMALL, 
                fg_color="transparent", 
                text_color=Renkler.TEXT_DARK, 
                hover_color=Renkler.BORDER,
                anchor="w",
                command=lambda op=dict(i): self.islem_sec(op)
            )
            btn_ad.grid(row=0, column=0, sticky="ew")
            
            lbl_maliyet = ctk.CTkLabel(satir, text=f"{i['saatlik_makine_maliyeti'] or 0.0:.2f} ₺ / Saat", font=Fontlar.SMALL, text_color=Renkler.TEXT_DARK, anchor="w")
            lbl_maliyet.grid(row=0, column=1, sticky="w", padx=10)
            
            lbl_fire = ctk.CTkLabel(satir, text=f"% {i['varsayilan_fire_orani'] or 0}", font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY, anchor="w")
            lbl_fire.grid(row=0, column=2, sticky="w", padx=10)
            
            ctk.CTkFrame(self.list_scroll, fg_color=Renkler.BORDER, height=1).pack(fill="x", pady=2)

    def islem_sec(self, islem):
        self.secili_islem_id = islem["id"]
        self.lbl_form_title.configure(text="İşlemi Düzenle")
        
        self.entry_ad.delete(0, "end")
        self.entry_ad.insert(0, islem["islem_adi"] or "")
        
        self.entry_maliyet.delete(0, "end")
        self.entry_maliyet.insert(0, str(islem["saatlik_makine_maliyeti"] or 0.0))
        
        self.entry_fire.delete(0, "end")
        self.entry_fire.insert(0, str(islem["varsayilan_fire_orani"] or 0))
        
        self.entry_aciklama.delete(0, "end")
        self.entry_aciklama.insert(0, islem["aciklama"] or "")
        
        self.btn_sil.pack(fill="x", pady=4, before=self.btn_temizle)

    def form_temizle(self):
        self.secili_islem_id = None
        self.lbl_form_title.configure(text="Yeni İşlem Ekle")
        
        self.entry_ad.delete(0, "end")
        self.entry_maliyet.delete(0, "end")
        self.entry_fire.delete(0, "end")
        self.entry_aciklama.delete(0, "end")
        
        self.btn_sil.pack_forget()

    def kaydet(self):
        ad = self.entry_ad.get().strip()
        maliyet = self.entry_maliyet.get().strip() or "0"
        fire = self.entry_fire.get().strip() or "0"
        aciklama = self.entry_aciklama.get().strip()
        
        if not ad:
            return
            
        try:
            maliyet = float(maliyet)
            fire = int(fire)
        except ValueError:
            return
            
        conn = self.db.connect()
        cursor = conn.cursor()
        
        if self.secili_islem_id:
            cursor.execute("""
                UPDATE islemler 
                SET islem_adi = ?, saatlik_makine_maliyeti = ?, varsayilan_fire_orani = ?, aciklama = ?
                WHERE id = ? AND kullanici_id = ?
            """, (ad, maliyet, fire, aciklama, self.secili_islem_id, self.current_user["id"]))
        else:
            cursor.execute("""
                INSERT INTO islemler (kullanici_id, islem_adi, saatlik_makine_maliyeti, varsayilan_fire_orani, aciklama)
                VALUES (?, ?, ?, ?, ?)
            """, (self.current_user["id"], ad, maliyet, fire, aciklama))
            
        conn.commit()
        conn.close()
        
        self.form_temizle()
        self.load_data()

    def sil(self):
        if not self.secili_islem_id:
            return
            
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM islemler WHERE id = ? AND kullanici_id = ?", (self.secili_islem_id, self.current_user["id"]))
        conn.commit()
        conn.close()
        
        self.form_temizle()
        self.load_data()
