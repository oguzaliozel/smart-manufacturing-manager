import customtkinter as ctk
from tema import Renkler, Fontlar
from dil import t
import database

class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color=Renkler.BG_LIGHT)
        self.master = master
        self.on_login_success = on_login_success
        self.db = database.Database()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Sol ve Sağ panel için iki ana sütun oluşturuyoruz
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=45, uniform="columns") # Sol Visual Panel (%45)
        self.grid_columnconfigure(1, weight=55, uniform="columns") # Sağ Login Panel (%55)
        
        # ==========================================
        # SOL PANEL: Görsel ve Tanıtım Alanı (Dark Premium)
        # ==========================================
        self.left_panel = ctk.CTkFrame(
            self, 
            fg_color="#0B1220", # Derin Gece Mavisi / Antrasit
            corner_radius=0
        )
        self.left_panel.grid(row=0, column=0, sticky="nsew")
        
        # İçerikleri ortalamak ve boşluklar için pack yapısı kullanıyoruz
        self.left_content = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.left_content.pack(expand=True, fill="both", padx=40, pady=50)
        
        # Mini Etiket (Badge)
        self.badge = ctk.CTkLabel(
            self.left_content,
            text="SMART MANUFACTURING MANAGER",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#3B82F6", # Neon Mavi
        )
        self.badge.pack(anchor="w", pady=(20, 10))
        
        # Ana Logo/Başlık
        self.lbl_logo = ctk.CTkLabel(
            self.left_content,
            text="ATÖLYE YÖNETİM",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        self.lbl_logo.pack(anchor="w", pady=(0, 5))
        
        # Alt Başlık
        self.lbl_subtitle = ctk.CTkLabel(
            self.left_content,
            text="Gelişmiş Maliyet Hesaplama ve Akıllı Üretim Planlama Platformu",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#94A3B8",
            anchor="w",
            justify="left"
        )
        self.lbl_subtitle.pack(anchor="w", pady=(0, 40))
        
        # Özellikler Listesi (Features list)
        features = [
            ("⚙️", "Hızlı Maliyet Hesaplama", "Malzeme, makine ve ek gider analizleri"),
            ("📈", "Gerçek Zamanlı Raporlama", "Onaylı siparişlerin anlık finansal takibi"),
            ("📅", "Akıllı Üretim Takvimi", "Termin ve teslimat tarihleri görselleştirme"),
            ("♻️", "Hurda Depo Kontrolü", "Atölye içi fire malzemelerinin takibi")
        ]
        
        for emoji, title, desc in features:
            f_row = ctk.CTkFrame(self.left_content, fg_color="transparent")
            f_row.pack(anchor="w", fill="x", pady=10)
            
            icon_lbl = ctk.CTkLabel(f_row, text=emoji, font=ctk.CTkFont(size=20))
            icon_lbl.pack(side="left", padx=(0, 15))
            
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
            
        # Alt Bilgi / Sürüm
        self.lbl_ver = ctk.CTkLabel(
            self.left_content,
            text="Sürüm 1.4.0 • Kararlı Sürüm",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#475569"
        )
        self.lbl_ver.pack(side="bottom", anchor="w", pady=(40, 0))
        
        # ==========================================
        # SAĞ PANEL: Giriş Formu
        # ==========================================
        self.right_panel = ctk.CTkFrame(
            self, 
            fg_color=Renkler.BG_LIGHT, 
            corner_radius=0
        )
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        
        # Form Konteyneri (Sayfa merkezinde duracak şık kart)
        self.form_container = ctk.CTkFrame(
            self.right_panel,
            fg_color=Renkler.CARD_BG,
            corner_radius=15,
            border_width=1,
            border_color=Renkler.BORDER,
            width=420,
            height=480
        )
        self.form_container.place(relx=0.5, rely=0.5, anchor="center")
        self.form_container.grid_propagate(False)
        
        # Üst Simge (Opsiyonel kilit ikonu)
        self.icon_lock = ctk.CTkLabel(
            self.form_container,
            text="🔐",
            font=ctk.CTkFont(size=36)
        )
        self.icon_lock.pack(pady=(40, 10))
        
        # Başlık
        self.lbl_form_title = ctk.CTkLabel(
            self.form_container, 
            text=t("login_title"), 
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"), 
            text_color=Renkler.TEXT_DARK
        )
        self.lbl_form_title.pack(pady=(0, 5))
        
        self.lbl_form_desc = ctk.CTkLabel(
            self.form_container, 
            text="Devam etmek için hesabınıza giriş yapın.", 
            font=ctk.CTkFont(family="Segoe UI", size=12), 
            text_color=Renkler.TEXT_GRAY
        )
        self.lbl_form_desc.pack(pady=(0, 30))
        
        # Kullanıcı Adı Girişi
        self.entry_username = ctk.CTkEntry(
            self.form_container, 
            placeholder_text=t("username"), 
            font=Fontlar.BODY, 
            height=45, 
            corner_radius=8,
            fg_color=Renkler.INPUT_BG,
            border_color=Renkler.INPUT_BORDER
        )
        self.entry_username.pack(pady=(0, 15), padx=40, fill="x")
        
        # Şifre Girişi
        self.entry_password = ctk.CTkEntry(
            self.form_container, 
            placeholder_text=t("password"), 
            show="*", 
            font=Fontlar.BODY, 
            height=45, 
            corner_radius=8,
            fg_color=Renkler.INPUT_BG,
            border_color=Renkler.INPUT_BORDER
        )
        self.entry_password.pack(pady=(0, 8), padx=40, fill="x")
        
        # Hata Mesajı
        self.lbl_error = ctk.CTkLabel(
            self.form_container, 
            text="", 
            font=Fontlar.SMALL, 
            text_color=Renkler.ERROR
        )
        self.lbl_error.pack(pady=(0, 10))
        
        # Giriş Butonu
        self.btn_login = ctk.CTkButton(
            self.form_container, 
            text=t("login_btn"), 
            font=Fontlar.BODY_BOLD, 
            height=45, 
            corner_radius=8,
            fg_color=Renkler.PRIMARY,
            hover_color=Renkler.PRIMARY_HOVER,
            command=self.handle_login
        )
        self.btn_login.pack(padx=40, fill="x")
        
        # Enter tuşu ile giriş bind
        self.entry_password.bind("<Return>", lambda e: self.handle_login())
        self.entry_username.bind("<Return>", lambda e: self.handle_login())
        
    def handle_login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        
        if not username or not password:
            self.lbl_error.configure(text=t("login_error_empty"))
            return
            
        user = self.db.login(username, password)
        if user:
            self.lbl_error.configure(text="")
            self.on_login_success(user)
        else:
            self.lbl_error.configure(text=t("login_error_invalid"))