import customtkinter as ctk
import database
from screens.login_screen import LoginScreen
from dil import t

class AtolyeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Ana pencere ayarları
        self.title(t("app_title"))
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # CustomTkinter genel tema ayarı
        ctk.set_appearance_mode("Light")
        
        # Veritabanını hazırla ve tabloları oluştur
        self.db = database.Database()
        self.db.create_tables()
        self.db.create_default_user()
        
        self.current_user = None
        self.current_screen = None
        
        # Uygulama başlarken giriş ekranını göster
        self.show_login_screen()

    def show_login_screen(self):
        if self.current_screen:
            self.current_screen.destroy()
            
        self.current_screen = LoginScreen(self, self.handle_login)
        self.current_screen.pack(fill="both", expand=True)
        
    def handle_login(self, user):
        self.current_user = user
        
        # Giriş başarılıysa giriş ekranını temizle
        if self.current_screen:
            self.current_screen.destroy()
            
        # Ana Layout'u (Sidebar + İçerik) başlat
        from screens.main_layout import MainLayout
        self.current_screen = MainLayout(self, self.current_user, self.logout)
        self.current_screen.pack(fill="both", expand=True)
        
    def logout(self):
        self.current_user = None
        self.show_login_screen()

if __name__ == "__main__":
    app = AtolyeApp()
    app.mainloop()