import customtkinter as ctk
from tema import Renkler, Fontlar
import database
from tkinter import messagebox

class KullanicilarScreen(ctk.CTkFrame):
    def __init__(self, master, current_user):
        super().__init__(master, fg_color=Renkler.BG_LIGHT)
        self.current_user = current_user
        self.db = database.Database()
        self._needs_refresh = False
        
        self.secili_kullanici_id = None
        
        # Yetki kontrolü
        if self.current_user.get("rol") != "Yönetici":
            self.create_access_denied_widgets()
        else:
            self.create_widgets()
            self.load_data()

    def create_access_denied_widgets(self):
        # Yetki yoksa gösterilecek kilit ekranı
        card = ctk.CTkFrame(self, fg_color=Renkler.CARD_BG, corner_radius=12, width=400, height=250)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)
        
        lbl_icon = ctk.CTkLabel(card, text="🔒", font=(Fontlar.FAMILY, 48))
        lbl_icon.pack(pady=(35, 10))
        
        lbl_title = ctk.CTkLabel(card, text="Erişim Reddedildi", font=Fontlar.H2, text_color=Renkler.ERROR)
        lbl_title.pack(pady=5)
        
        lbl_msg = ctk.CTkLabel(
            card, 
            text="Bu ekrana yalnızca Yönetici yetkisine\nsahip kullanıcılar erişebilir.", 
            font=Fontlar.SMALL, 
            text_color=Renkler.TEXT_GRAY,
            justify="center"
        )
        lbl_msg.pack(pady=5)

    def create_widgets(self):
        # ── ÜST BAŞLIK ALANI ──────────────────────────────────────────────────
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(30, 15))
        
        ctk.CTkLabel(
            self.header_frame, 
            text="Kullanıcı Yönetimi", 
            font=Fontlar.H1, 
            text_color=Renkler.TEXT_DARK
        ).pack(side="left")

        # Arama Kutusu
        self.entry_ara = ctk.CTkEntry(
            self.header_frame, 
            placeholder_text="Ad Soyad veya Kullanıcı Adı Ara...", 
            width=260, 
            font=Fontlar.SMALL
        )
        self.entry_ara.pack(side="right", padx=10)
        self.entry_ara.bind("<KeyRelease>", lambda e: self.load_data())

        # ── ANA İÇERİK ALANI (BÖLÜNMÜŞ DÜZEN) ─────────────────────────────────
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        self.content_frame.grid_columnconfigure(0, weight=6) # Sol Liste
        self.content_frame.grid_columnconfigure(1, weight=4) # Sağ Form
        self.content_frame.grid_rowconfigure(0, weight=1)

        # ── SOL: LİSTE KARTI ──────────────────────────────────────────────────
        self.left_card = ctk.CTkFrame(self.content_frame, fg_color=Renkler.CARD_BG, corner_radius=10)
        self.left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        # Tablo Başlıkları
        self.table_header = ctk.CTkFrame(self.left_card, fg_color="transparent")
        self.table_header.pack(fill="x", padx=15, pady=10)
        self.table_header.grid_columnconfigure(0, weight=4) # Ad Soyad
        self.table_header.grid_columnconfigure(1, weight=3) # Kullanıcı Adı
        self.table_header.grid_columnconfigure(2, weight=3) # Rol
        
        ctk.CTkLabel(self.table_header, text="Ad Soyad", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_GRAY, anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(self.table_header, text="Kullanıcı Adı", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_GRAY, anchor="w").grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(self.table_header, text="Sistem Rolü", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_GRAY, anchor="w").grid(row=0, column=2, sticky="w")
        
        ctk.CTkFrame(self.left_card, fg_color=Renkler.BORDER, height=1).pack(fill="x", padx=15)

        # Kaydırılabilir Liste
        self.list_scroll = ctk.CTkScrollableFrame(self.left_card, fg_color="transparent")
        self.list_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # ── SAĞ: EKLE / DÜZENLE FORMU ─────────────────────────────────────────
        self.right_card = ctk.CTkFrame(self.content_frame, fg_color=Renkler.CARD_BG, corner_radius=10)
        self.right_card.grid(row=0, column=1, sticky="nsew")
        
        self.lbl_form_title = ctk.CTkLabel(self.right_card, text="Yeni Kullanıcı Tanımla", font=Fontlar.H3, text_color=Renkler.TEXT_DARK)
        self.lbl_form_title.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Kaydırılabilir Gövde
        self.form_scroll = ctk.CTkScrollableFrame(self.right_card, fg_color="transparent")
        self.form_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.entry_ad_soyad = self.create_form_input(self.form_scroll, "Ad Soyad:")
        self.entry_kullanici_adi = self.create_form_input(self.form_scroll, "Kullanıcı Adı:")
        self.entry_sifre = self.create_form_input(self.form_scroll, "Şifre (Giriş Şifresi):")
        
        # Rol Seçimi
        lbl_role_text = ctk.CTkLabel(self.form_scroll, text="Sistem Rolü:", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK)
        lbl_role_text.pack(anchor="w", padx=15, pady=(6, 2))
        
        self.combo_rol = ctk.CTkComboBox(
            self.form_scroll, 
            values=["Yönetici", "Kullanıcı", "Personel"], 
            font=Fontlar.SMALL, 
            height=35
        )
        self.combo_rol.pack(fill="x", padx=15, pady=(0, 6))
        self.combo_rol.set("Kullanıcı")

        # Butonlar
        self.btn_panel = ctk.CTkFrame(self.right_card, fg_color="transparent")
        self.btn_panel.pack(fill="x", padx=20, pady=20, side="bottom")
        
        self.btn_kaydet = ctk.CTkButton(
            self.btn_panel, 
            text="Kaydet", 
            font=Fontlar.BODY_BOLD, 
            fg_color=Renkler.PRIMARY, 
            hover_color=Renkler.PRIMARY_HOVER, 
            command=self.kaydet
        )
        self.btn_kaydet.pack(fill="x", pady=4)
        
        self.btn_sil = ctk.CTkButton(
            self.btn_panel, 
            text="Kullanıcıyı Sil", 
            font=Fontlar.BODY_BOLD, 
            fg_color=Renkler.ERROR, 
            hover_color="#DC2626", 
            command=self.sil
        )
        
        self.btn_temizle = ctk.CTkButton(
            self.btn_panel, 
            text="Formu Temizle", 
            font=Fontlar.SMALL_BOLD, 
            fg_color="transparent", 
            text_color=Renkler.TEXT_GRAY, 
            hover_color=Renkler.BORDER, 
            command=self.form_temizle
        )
        self.btn_temizle.pack(fill="x", pady=4)

    def create_form_input(self, parent, label_text):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=6)
        
        ctk.CTkLabel(frame, text=label_text, font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK).pack(anchor="w", pady=(0, 2))
        entry = ctk.CTkEntry(frame, font=Fontlar.SMALL, height=35)
        entry.pack(fill="x")
        return entry

    def load_data(self):
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
            
        arama_kelimesi = self.entry_ara.get().strip()
        
        conn = self.db.connect()
        cursor = conn.cursor()
        
        if arama_kelimesi:
            cursor.execute("""
                SELECT id, ad_soyad, kullanici_adi, rol FROM kullanicilar 
                WHERE ad_soyad LIKE ? OR kullanici_adi LIKE ?
                ORDER BY ad_soyad ASC
            """, (f"%{arama_kelimesi}%", f"%{arama_kelimesi}%"))
        else:
            cursor.execute("SELECT id, ad_soyad, kullanici_adi, rol FROM kullanicilar ORDER BY ad_soyad ASC")
            
        kullanicilar = cursor.fetchall()
        conn.close()
        
        for k in kullanicilar:
            satir = ctk.CTkFrame(self.list_scroll, fg_color="transparent")
            satir.pack(fill="x", pady=2, padx=5)
            satir.grid_columnconfigure((0, 1, 2), weight=1)
            
            btn_ad = ctk.CTkButton(
                satir, 
                text=k["ad_soyad"], 
                font=Fontlar.SMALL_BOLD, 
                fg_color="transparent", 
                text_color=Renkler.TEXT_DARK, 
                hover_color=Renkler.BORDER,
                anchor="w",
                command=lambda item=dict(k): self.sec_kullanici(item)
            )
            btn_ad.grid(row=0, column=0, sticky="ew")
            
            lbl_kadi = ctk.CTkLabel(satir, text=k["kullanici_adi"], font=Fontlar.SMALL, text_color=Renkler.TEXT_DARK, anchor="w")
            lbl_kadi.grid(row=0, column=1, sticky="w", padx=10)
            
            lbl_rol = ctk.CTkLabel(satir, text=k["rol"], font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY, anchor="w")
            lbl_rol.grid(row=0, column=2, sticky="w", padx=10)
            
            ctk.CTkFrame(self.list_scroll, fg_color=Renkler.BORDER, height=1).pack(fill="x", pady=2)

    def sec_kullanici(self, k):
        self.secili_kullanici_id = k["id"]
        self.lbl_form_title.configure(text="Kullanıcıyı Düzenle")
        
        self.entry_ad_soyad.delete(0, "end")
        self.entry_ad_soyad.insert(0, k["ad_soyad"] or "")
        
        self.entry_kullanici_adi.delete(0, "end")
        self.entry_kullanici_adi.insert(0, k["kullanici_adi"] or "")
        
        # Düzenleme modunda şifreyi boş getiriyoruz (Değişmeyecekse boş bırakılır)
        self.entry_sifre.delete(0, "end")
        self.entry_sifre.configure(placeholder_text="Değiştirmek istemiyorsanız boş bırakın")
        
        self.combo_rol.set(k["rol"])
        
        # Kendi hesabını silemesin
        if k["id"] != self.current_user["id"]:
            self.btn_sil.pack(fill="x", pady=4, before=self.btn_temizle)
        else:
            self.btn_sil.pack_forget()

    def form_temizle(self):
        self.secili_kullanici_id = None
        self.lbl_form_title.configure(text="Yeni Kullanıcı Tanımla")
        
        self.entry_ad_soyad.delete(0, "end")
        self.entry_kullanici_adi.delete(0, "end")
        self.entry_sifre.delete(0, "end")
        self.entry_sifre.configure(placeholder_text="")
        self.combo_rol.set("Kullanıcı")
        
        self.btn_sil.pack_forget()

    def kaydet(self):
        ad_soyad = self.entry_ad_soyad.get().strip()
        k_adi = self.entry_kullanici_adi.get().strip()
        sifre = self.entry_sifre.get().strip()
        rol = self.combo_rol.get()
        
        if not ad_soyad or not k_adi:
            messagebox.showwarning("Uyarı", "Lütfen Ad Soyad ve Kullanıcı Adı alanlarını doldurun.")
            return
            
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            if self.secili_kullanici_id:
                # Düzenleme
                if sifre:
                    # Şifre de değişecek
                    cursor.execute("""
                        UPDATE kullanicilar 
                        SET ad_soyad = ?, kullanici_adi = ?, sifre = ?, rol = ?
                        WHERE id = ?
                    """, (ad_soyad, k_adi, sifre, rol, self.secili_kullanici_id))
                else:
                    # Şifre aynı kalacak
                    cursor.execute("""
                        UPDATE kullanicilar 
                        SET ad_soyad = ?, kullanici_adi = ?, rol = ?
                        WHERE id = ?
                    """, (ad_soyad, k_adi, rol, self.secili_kullanici_id))
            else:
                # Yeni Ekleme
                if not sifre:
                    messagebox.showwarning("Uyarı", "Yeni kullanıcılar için şifre girmek zorunludur.")
                    conn.close()
                    return
                cursor.execute("""
                    INSERT INTO kullanicilar (ad_soyad, kullanici_adi, sifre, rol)
                    VALUES (?, ?, ?, ?)
                """, (ad_soyad, k_adi, sifre, rol))
                
            conn.commit()
            messagebox.showinfo("Başarılı", "Kullanıcı kaydı başarıyla kaydedildi.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Hata", "Bu kullanıcı adı zaten başka bir kullanıcı tarafından kullanılıyor.")
        finally:
            conn.close()
            
        self.form_temizle()
        self.load_data()

    def sil(self):
        if not self.secili_kullanici_id:
            return
            
        if self.secili_kullanici_id == self.current_user["id"]:
            messagebox.showwarning("Hata", "Kendi hesabınızı buradan silemezsiniz.")
            return
            
        if not messagebox.askyesno("Onay", "Bu kullanıcıyı ve sisteme bağlı tüm verilerini silmek istediğinize emin misiniz?"):
            return
            
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM kullanicilar WHERE id = ?", (self.secili_kullanici_id,))
        conn.commit()
        conn.close()
        
        self.form_temizle()
        self.load_data()

    def apply_theme(self):
        self.configure(fg_color=Renkler.BG_LIGHT)
        try:
            if hasattr(self, 'left_card'):
                self.left_card.configure(fg_color=Renkler.CARD_BG)
            if hasattr(self, 'right_card'):
                self.right_card.configure(fg_color=Renkler.CARD_BG)
            if hasattr(self, 'lbl_form_title'):
                self.lbl_form_title.configure(text_color=Renkler.TEXT_DARK)
        except Exception:
            pass
        self._needs_refresh = True
        is_active = (hasattr(self.master, "master") and getattr(self.master.master, "current_screen", None) == self)
        if is_active and self.current_user.get("rol") == "Yönetici":
            self.load_data()
