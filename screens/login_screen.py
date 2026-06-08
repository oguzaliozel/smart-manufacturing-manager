import customtkinter as ctk
from tema import Renkler, Fontlar
from dil import t
import database

class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        # Arka plan rengini #F8FAFC yapıyoruz
        super().__init__(master, fg_color="#F8FAFC")
        self.master = master
        self.on_login_success = on_login_success
        self.db = database.Database()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Sol (Koyu Bilgilendirme) ve Sağ (Giriş) paneller için sütun yapılandırması
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=40, uniform="cols") # Sol panel %40
        self.grid_columnconfigure(1, weight=60, uniform="cols") # Sağ panel %60
        
        # ==========================================
        # SOL PANEL: Koyu Kurumsal Bilgi Alanı
        # ==========================================
        self.left_panel = ctk.CTkFrame(
            self, 
            fg_color="#0F172A", # Kurumsal Koyu Lacivert/Antrasit
            corner_radius=0
        )
        self.left_panel.grid(row=0, column=0, sticky="nsew")
        
        # Sol panel iç marj çerçevesi
        self.left_content = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.left_content.pack(expand=True, fill="both", padx=45, pady=60)
        
        # Sol Üst Köşe: Sade Endüstriyel/Gears İkonu ve Sistem İsmi
        self.icon_frame = ctk.CTkFrame(self.left_content, fg_color="transparent")
        self.icon_frame.pack(anchor="w", pady=(0, 40))
        
        self.icon_gear = ctk.CTkLabel(
            self.icon_frame,
            text="🏭", # Sade fabrika simgesi
            font=ctk.CTkFont(size=24),
            text_color="#FFFFFF"
        )
        self.icon_gear.pack(side="left", padx=(0, 10))
        
        self.lbl_system = ctk.CTkLabel(
            self.icon_frame,
            text="ERP / MRP v1.4",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#64748B"
        )
        self.lbl_system.pack(side="left")
        
        # Ana Başlık: ATÖLYE YÖNETİM SİSTEMİ
        self.lbl_logo = ctk.CTkLabel(
            self.left_content,
            text="ATÖLYE YÖNETİM\nSİSTEMİ",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color="#FFFFFF",
            justify="left",
            anchor="w"
        )
        self.lbl_logo.pack(anchor="w", pady=(0, 10))
        
        # Alt Başlık
        self.lbl_subtitle = ctk.CTkLabel(
            self.left_content,
            text="Üretim planlama, maliyet analizi ve sipariş yönetimi platformu",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#94A3B8",
            anchor="w",
            justify="left"
        )
        self.lbl_subtitle.pack(anchor="w", pady=(0, 45))
        
        # Özellikler Listesi (Sade ve Kurumsal)
        features = [
            ("📊", "Maliyet Analizi", "Malzeme, işçilik ve genel gider hesaplamaları"),
            ("📋", "Sipariş Takibi", "Aktif siparişlerin durum yönetimi"),
            ("📅", "Üretim Planlama", "Üretim süreçleri ve teslim tarihleri takibi"),
            ("📦", "Stok Yönetimi", "Malzeme ve yarı mamul kontrolü")
        ]
        
        for emoji, title, desc in features:
            f_row = ctk.CTkFrame(self.left_content, fg_color="transparent")
            f_row.pack(anchor="w", fill="x", pady=12)
            
            icon_lbl = ctk.CTkLabel(f_row, text=emoji, font=ctk.CTkFont(size=18))
            icon_lbl.pack(side="left", padx=(0, 15), anchor="n")
            
            txt_frame = ctk.CTkFrame(f_row, fg_color="transparent")
            txt_frame.pack(side="left", fill="both")
            
            lbl_f_title = ctk.CTkLabel(
                txt_frame, text=title, 
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color="#F8FAFC"
            )
            lbl_f_title.pack(anchor="w")
            
            lbl_f_desc = ctk.CTkLabel(
                txt_frame, text=desc, 
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color="#64748B"
            )
            lbl_f_desc.pack(anchor="w")
            
        # Sol Panel En Alt: Akademik Versiyon Bilgisi
        self.lbl_version = ctk.CTkLabel(
            self.left_content,
            text="Tüm hakları saklıdır © 2026",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#475569"
        )
        self.lbl_version.pack(side="bottom", anchor="w", pady=(20, 0))
        
        # ==========================================
        # SAĞ PANEL: Giriş Yapılan Bölüm
        # ==========================================
        self.right_panel = ctk.CTkFrame(
            self, 
            fg_color="#F8FAFC", # Açık kurumsal arka plan
            corner_radius=0
        )
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        
        # Sağ Panel İçerikleri Dikey Sıralama
        self.right_content = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.right_content.place(relx=0.5, rely=0.5, anchor="center")
        
        # Giriş Kartı (Daha dengeli ve sade, beyaz zemin, ince gri çerçeve)
        self.form_card = ctk.CTkFrame(
            self.right_content,
            fg_color="#FFFFFF",
            corner_radius=8,
            border_width=1,
            border_color="#E2E8F0",
            width=430,
            height=470
        )
        self.form_card.pack(pady=(0, 20))
        self.form_card.pack_propagate(False)
        
        # Kart Üstü Başlık
        self.lbl_form_title = ctk.CTkLabel(
            self.form_card, 
            text="Sisteme Giriş", 
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"), 
            text_color="#0F172A"
        )
        self.lbl_form_title.pack(pady=(45, 5))
        
        self.lbl_form_desc = ctk.CTkLabel(
            self.form_card, 
            text="Lütfen kullanıcı bilgilerinizi giriniz.", 
            font=ctk.CTkFont(family="Segoe UI", size=12), 
            text_color="#64748B"
        )
        self.lbl_form_desc.pack(pady=(0, 35))
        
        # Kullanıcı Adı
        self.entry_username = ctk.CTkEntry(
            self.form_card, 
            placeholder_text=t("username"), 
            font=Fontlar.BODY, 
            height=40, 
            corner_radius=6,
            fg_color="#FFFFFF",
            border_color="#E2E8F0",
            text_color="#0F172A",
            placeholder_text_color="#94A3B8"
        )
        self.entry_username.pack(pady=(0, 15), padx=45, fill="x")
        
        # Şifre
        self.entry_password = ctk.CTkEntry(
            self.form_card, 
            placeholder_text=t("password"), 
            show="*", 
            font=Fontlar.BODY, 
            height=40, 
            corner_radius=6,
            fg_color="#FFFFFF",
            border_color="#E2E8F0",
            text_color="#0F172A",
            placeholder_text_color="#94A3B8"
        )
        self.entry_password.pack(pady=(0, 8), padx=45, fill="x")
        
        # Beni Hatırla & Şifremi Unuttum Satırı
        self.options_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        self.options_frame.pack(fill="x", padx=45, pady=(5, 12))
        
        self.cb_remember = ctk.CTkCheckBox(
            self.options_frame,
            text="Beni Hatırla",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#64748B",
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            border_width=1.5,
            corner_radius=4,
            checkbox_width=16,
            checkbox_height=16
        )
        self.cb_remember.pack(side="left")
        
        self.lbl_forgot = ctk.CTkLabel(
            self.options_frame,
            text="Şifremi Unuttum",
            font=ctk.CTkFont(family="Segoe UI", size=11, underline=True),
            text_color="#64748B",
            cursor="hand2"
        )
        self.lbl_forgot.pack(side="right")
        self.lbl_forgot.bind("<Button-1>", lambda e: self.forgot_password_clicked())
        
        # Hata / Doğrulama Durum Mesajı
        self.lbl_error = ctk.CTkLabel(
            self.form_card, 
            text="", 
            font=Fontlar.SMALL, 
            text_color=Renkler.ERROR
        )
        self.lbl_error.pack(pady=(0, 10))
        
        # İlerleme Çubuğu (Doğrulama esnasında görünür olacak)
        self.prog_bar = ctk.CTkProgressBar(
            self.form_card,
            mode="indeterminate",
            width=200,
            height=4,
            fg_color="#F1F5F9",
            progress_color="#2563EB"
        )
        
        # Giriş Yap Butonu
        self.btn_login = ctk.CTkButton(
            self.form_card, 
            text=t("login_btn"), 
            font=Fontlar.BODY_BOLD, 
            height=42, 
            corner_radius=6,
            fg_color="#2563EB", 
            hover_color="#1D4ED8", 
            text_color="#FFFFFF",
            command=self.handle_login
        )
        self.btn_login.pack(padx=45, fill="x")
        
        # Enter bind
        self.entry_password.bind("<Return>", lambda e: self.handle_login())
        self.entry_username.bind("<Return>", lambda e: self.handle_login())
        
        # Kart Altındaki Akademik Metin
        self.lbl_academic = ctk.CTkLabel(
            self.right_content,
            text="Balıkesir Üniversitesi\nBilgisayar Mühendisliği • Nesne Tabanlı Programlama Projesi",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#64748B",
            justify="center"
        )
        self.lbl_academic.pack()
        
    def handle_login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        
        if not username or not password:
            self.lbl_error.configure(text_color=Renkler.ERROR, text=t("login_error_empty"))
            return
            
        user = self.db.login(username, password)
        if user:
            # Giriş başarılı - Doğrulama durumunu göster
            self.lbl_error.configure(text_color="#2563EB", text="Kullanıcı doğrulanıyor...")
            
            # Alanları devre dışı bırak
            self.entry_username.configure(state="disabled")
            self.entry_password.configure(state="disabled")
            self.btn_login.configure(state="disabled")
            
            # İlerleme çubuğunu göster ve animasyonu başlat
            self.prog_bar.pack(before=self.btn_login, pady=(0, 15))
            self.prog_bar.start()
            
            # 1.5 saniye sonra ana sayfayı aç
            self.after(1500, lambda: self.finish_login(user))
        else:
            self.lbl_error.configure(text_color=Renkler.ERROR, text=t("login_error_invalid"))
            
    def finish_login(self, user):
        self.prog_bar.stop()
        self.on_login_success(user)
        
    def forgot_password_clicked(self):
        info_win = ctk.CTkToplevel(self)
        info_win.title("Şifre Sıfırlama")
        info_win.geometry("360x170")
        info_win.resizable(False, False)
        info_win.configure(fg_color="#FFFFFF")
        info_win.transient(self)
        info_win.grab_set()
        
        # Ekranı ortala
        info_win.update_idletasks()
        x = self.winfo_screenwidth() // 2 - 180
        y = self.winfo_screenheight() // 2 - 85
        info_win.geometry(f"+{x}+{y}")
        
        lbl = ctk.CTkLabel(
            info_win,
            text="Güvenlik nedeniyle şifre sıfırlama işlemleri\nyalnızca sistem yöneticisi tarafından yapılabilir.\n\nLütfen atölye yöneticiniz ile iletişime geçiniz.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#0F172A",
            justify="center"
        )
        lbl.pack(pady=(25, 15))
        
        btn = ctk.CTkButton(
            info_win,
            text="Tamam",
            font=Fontlar.SMALL_BOLD,
            width=100,
            height=32,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=info_win.destroy
        )
        btn.pack()