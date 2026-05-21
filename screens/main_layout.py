import customtkinter as ctk
from tema import Renkler, Fontlar
from screens.dashboard_screen import DashboardScreen
from screens.teklifler_screen import TekliflerScreen

class MainLayout(ctk.CTkFrame):
    def __init__(self, master, current_user, on_logout):
        super().__init__(master, fg_color=Renkler.BG_LIGHT)
        self.master = master
        self.current_user = current_user
        self.on_logout = on_logout
        
        # İçinde gösterilecek ekranların (sayfaların) tutulduğu sözlük
        self.screens = {}
        self.current_screen = None
        
        self.create_sidebar()
        self.create_content_area()
        
        # Uygulama açıldığında ilk olarak Dashboard'u göster
        self.show_screen("dashboard")
        
    def create_sidebar(self):
        # Sidebar çerçevesi
        self.sidebar = ctk.CTkFrame(self, fg_color=Renkler.SIDEBAR_BG, corner_radius=0, width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False) # Genişliği sabit tut
        
        # Logo ve Başlık
        self.lbl_logo = ctk.CTkLabel(
            self.sidebar, 
            text="ATÖLYE\nYÖNETİM", 
            font=Fontlar.H2, 
            text_color=Renkler.SIDEBAR_TEXT,
            justify="center"
        )
        self.lbl_logo.pack(pady=(40, 30))
        
        # Kaydırılabilir menü alanı (ileride çok menü olursa sığması için)
        self.menu_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", bg_color="transparent")
        self.menu_scroll.pack(fill="both", expand=True)
        
        self.menus = []
        
        # Kategoriler ve Menüler
        self.add_category("GENEL")
        self.add_menu_btn("Dashboard", "dashboard")
        self.add_menu_btn("Takvim", "takvim")
        self.add_menu_btn("Raporlar", "raporlar")
        
        self.add_category("TEKLİF YÖNETİMİ")
        self.add_menu_btn("Teklifler", "teklifler")
        self.add_menu_btn("Proformalar", "proformalar")
        self.add_menu_btn("Müşteriler", "musteriler")
        
        self.add_category("ÜRETİM")
        self.add_menu_btn("Malzemeler", "malzemeler")
        self.add_menu_btn("İşlemler / Makineler", "islemler")
        self.add_menu_btn("Hurda Deposu", "hurda")
        
        self.add_category("SİSTEM")
        self.add_menu_btn("Kullanıcılar", "kullanicilar")
        self.add_menu_btn("Ayarlar", "ayarlar")
        
        # Alt Kısım: Kullanıcı Paneli
        self.user_panel = ctk.CTkFrame(self.sidebar, fg_color=Renkler.SIDEBAR_BG, corner_radius=0)
        self.user_panel.pack(side="bottom", fill="x", pady=20, padx=20)
        
        self.lbl_user = ctk.CTkLabel(
            self.user_panel, 
            text=self.current_user['ad_soyad'], 
            font=Fontlar.BODY_BOLD, 
            text_color=Renkler.SIDEBAR_TEXT
        )
        self.lbl_user.pack(anchor="w")
        
        self.lbl_role = ctk.CTkLabel(
            self.user_panel, 
            text=self.current_user['rol'], 
            font=Fontlar.SMALL, 
            text_color=Renkler.TEXT_GRAY
        )
        self.lbl_role.pack(anchor="w")
        
        self.btn_logout = ctk.CTkButton(
            self.user_panel, 
            text="Çıkış Yap", 
            font=Fontlar.SMALL_BOLD, 
            fg_color="transparent", 
            hover_color=Renkler.SIDEBAR_HOVER, 
            border_color=Renkler.ERROR, 
            border_width=1, 
            command=self.on_logout
        )
        self.btn_logout.pack(anchor="w", pady=(15, 0), fill="x")

    def add_category(self, title):
        lbl = ctk.CTkLabel(
            self.menu_scroll, 
            text=title, 
            font=Fontlar.SMALL_BOLD, 
            text_color=Renkler.TEXT_GRAY, 
            anchor="w"
        )
        lbl.pack(fill="x", padx=15, pady=(20, 5))
        
    def add_menu_btn(self, text, screen_name):
        btn = ctk.CTkButton(
            self.menu_scroll, 
            text=text, 
            font=Fontlar.BODY, 
            fg_color="transparent", 
            text_color=Renkler.SIDEBAR_TEXT,
            hover_color=Renkler.SIDEBAR_HOVER,
            anchor="w",
            corner_radius=8,
            command=lambda: self.show_screen(screen_name)
        )
        btn.pack(fill="x", padx=10, pady=2)
        self.menus.append({"btn": btn, "name": screen_name})

    def create_content_area(self):
        # Sağ taraftaki değişen içerik alanı
        self.content_area = ctk.CTkFrame(self, fg_color=Renkler.BG_LIGHT, corner_radius=0)
        self.content_area.pack(side="right", fill="both", expand=True)
        
    def show_screen(self, screen_name):
        # Butonların aktiflik durumunu görsel olarak ayarla
        for menu in self.menus:
            if menu["name"] == screen_name:
                menu["btn"].configure(fg_color=Renkler.PRIMARY) # Aktif buton rengi
            else:
                menu["btn"].configure(fg_color="transparent")
                
        # Eğer ekranda bir sayfa varsa gizle
        if self.current_screen:
            self.current_screen.pack_forget()
            
        # İstenen sayfa henüz bellekte oluşturulmadıysa oluştur
        if screen_name not in self.screens:
            if screen_name == "dashboard":
                self.screens[screen_name] = DashboardScreen(self.content_area, self.current_user)
            elif screen_name == "teklifler":
                self.screens[screen_name] = TekliflerScreen(self.content_area, self.current_user)
            elif screen_name == "takvim":
                from screens.takvim_screen import TakvimScreen
                self.screens[screen_name] = TakvimScreen(self.content_area, self.current_user)
            elif screen_name == "yeni_teklif":
                from screens.yeni_teklif_screen import YeniTeklifScreen
                self.screens[screen_name] = YeniTeklifScreen(self.content_area, self.current_user)
            elif screen_name == "musteriler":
                from screens.musteriler_screen import MusterilerScreen
                self.screens[screen_name] = MusterilerScreen(self.content_area, self.current_user)
            elif screen_name == "malzemeler":
                from screens.malzemeler_screen import MalzemelerScreen
                self.screens[screen_name] = MalzemelerScreen(self.content_area, self.current_user)
            elif screen_name == "islemler":
                from screens.islemler_screen import IslemlerScreen
                self.screens[screen_name] = IslemlerScreen(self.content_area, self.current_user)
            elif screen_name == "hurda":
                from screens.hurda_screen import HurdaScreen
                self.screens[screen_name] = HurdaScreen(self.content_area, self.current_user)
            elif screen_name == "proformalar":
                from screens.proformalar_screen import ProformalarScreen
                self.screens[screen_name] = ProformalarScreen(self.content_area, self.current_user)
            elif screen_name == "kullanicilar":
                from screens.kullanicilar_screen import KullanicilarScreen
                self.screens[screen_name] = KullanicilarScreen(self.content_area, self.current_user)
            elif screen_name == "ayarlar":
                from screens.ayarlar_screen import AyarlarScreen
                self.screens[screen_name] = AyarlarScreen(self.content_area, self.current_user)
            else:
                # Yapım aşamasındaki diğer sayfalar için geçici alan
                placeholder = ctk.CTkFrame(self.content_area, fg_color=Renkler.BG_LIGHT)
                lbl = ctk.CTkLabel(placeholder, text=f"{screen_name.capitalize()} Ekranı Yapım Aşamasında", font=Fontlar.H2, text_color=Renkler.TEXT_DARK)
                lbl.pack(expand=True)
                self.screens[screen_name] = placeholder
                
        # Seçilen sayfayı ekrana yerleştir
        self.current_screen = self.screens[screen_name]
        self.current_screen.pack(fill="both", expand=True)
        
        # Ekranı yenileme metodu varsa çağır (verilerin güncellenmesi için)
        if hasattr(self.current_screen, 'load_data'):
            self.current_screen.load_data()
