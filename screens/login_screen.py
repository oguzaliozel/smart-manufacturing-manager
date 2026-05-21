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
        # Ekranı ortalamak için bir grid yapısı kullanıyoruz
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Merkez Konteyner Kartı
        self.container = ctk.CTkFrame(
            self, 
            fg_color=Renkler.CARD_BG, 
            corner_radius=15, 
            width=400, 
            height=500
        )
        self.container.grid(row=0, column=0)
        self.container.grid_propagate(False) # Sabit boyut
        
        # Başlık
        self.lbl_title = ctk.CTkLabel(
            self.container, 
            text=t("login_title"), 
            font=Fontlar.H2, 
            text_color=Renkler.TEXT_DARK
        )
        self.lbl_title.pack(pady=(50, 40))
        
        # Kullanıcı Adı
        self.entry_username = ctk.CTkEntry(
            self.container, 
            placeholder_text=t("username"), 
            font=Fontlar.BODY, 
            height=45, 
            corner_radius=8
        )
        self.entry_username.pack(pady=(0, 15), padx=40, fill="x")
        
        # Şifre
        self.entry_password = ctk.CTkEntry(
            self.container, 
            placeholder_text=t("password"), 
            show="*", 
            font=Fontlar.BODY, 
            height=45, 
            corner_radius=8
        )
        self.entry_password.pack(pady=(0, 10), padx=40, fill="x")
        
        # Hata Mesajı
        self.lbl_error = ctk.CTkLabel(
            self.container, 
            text="", 
            font=Fontlar.SMALL, 
            text_color=Renkler.ERROR
        )
        self.lbl_error.pack(pady=(0, 10))
        
        # Giriş Butonu
        self.btn_login = ctk.CTkButton(
            self.container, 
            text=t("login_btn"), 
            font=Fontlar.BODY_BOLD, 
            height=45, 
            corner_radius=8,
            fg_color=Renkler.PRIMARY,
            hover_color=Renkler.PRIMARY_HOVER,
            command=self.handle_login
        )
        self.btn_login.pack(padx=40, fill="x")
        
        # Enter tuşu ile giriş
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