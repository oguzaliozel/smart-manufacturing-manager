import customtkinter as ctk
from tema import Renkler, Fontlar, ThemeManager
import database
from screens.dashboard_screen import DashboardScreen
from screens.teklifler_screen import TekliflerScreen

class MainLayout(ctk.CTkFrame):
    def __init__(self, master, current_user, on_logout):
        super().__init__(master, fg_color=Renkler.BG_LIGHT)
        self.master = master
        self.current_user = current_user
        self.on_logout = on_logout
        self.db = database.Database()
        
        # İçinde gösterilecek ekranların (sayfaların) tutulduğu sözlük
        self.screens = {}
        self.current_screen_name = None
        self.current_screen = None
        
        self.create_sidebar()
        self.create_content_area()
        
        # Uygulama açıldığında ilk olarak Dashboard'u göster
        self.show_screen("dashboard")
        
    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            fg_color=Renkler.SIDEBAR_BG,
            corner_radius=0,
            width=240
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # ── Logo ──────────────────────────────────────────────────────────
        self.lbl_logo = ctk.CTkLabel(
            self.sidebar,
            text="ATÖLYE\nYÖNETİM",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=Renkler.SIDEBAR_TEXT,
            justify="center"
        )
        self.lbl_logo.pack(pady=(35, 25))
        
        # ── Kaydırılabilir menü alanı ──────────────────────────────────────
        self.menu_scroll = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent",
            bg_color="transparent"
        )
        self.menu_scroll.pack(fill="both", expand=True)
        
        self.menus = []
        
        self.add_category("GENEL")
        self.add_menu_btn("Dashboard", "dashboard", "📊")
        self.add_menu_btn("Takvim", "takvim", "📅")
        self.add_menu_btn("Raporlar", "raporlar", "📈")
        
        self.add_category("TEKLİF YÖNETİMİ")
        self.add_menu_btn("Teklifler", "teklifler", "📄")
        self.add_menu_btn("Proformalar", "proformalar", "🧾")
        self.add_menu_btn("Müşteriler", "musteriler", "🏢")
        
        self.add_category("ÜRETİM")
        self.add_menu_btn("Malzemeler", "malzemeler", "🔩")
        self.add_menu_btn("İşlemler / Makineler", "islemler", "⚙️")
        self.add_menu_btn("Hurda Deposu", "hurda", "♻️")
        
        self.add_category("SİSTEM")
        self.add_menu_btn("Kullanıcılar", "kullanicilar", "👥")
        self.add_menu_btn("Ayarlar", "ayarlar", "⚙️")
        
        # ── Tema Seçici ────────────────────────────────────────────────────
        self.theme_panel = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
            corner_radius=0
        )
        self.theme_panel.pack(side="bottom", fill="x", padx=15, pady=(0, 8))
        
        # Ayırıcı çizgi
        ctk.CTkFrame(
            self.theme_panel,
            fg_color=Renkler.BORDER,
            height=1,
            corner_radius=0
        ).pack(fill="x", pady=(0, 10))
        
        # Tema başlığı
        self.lbl_tema = ctk.CTkLabel(
            self.theme_panel,
            text="GÖRÜNÜM",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=Renkler.TEXT_GRAY,
            anchor="w"
        )
        self.lbl_tema.pack(fill="x", pady=(0, 6))
        
        # Segmented tema butonu
        current_theme = ThemeManager.current()
        self.seg_tema = ctk.CTkSegmentedButton(
            self.theme_panel,
            values=["☀ Açık", "🌙 Koyu"],
            command=self._on_theme_change,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=Renkler.SIDEBAR_HOVER,
            selected_color=Renkler.PRIMARY,
            selected_hover_color=Renkler.PRIMARY_HOVER,
            unselected_color=Renkler.SIDEBAR_HOVER,
            unselected_hover_color=Renkler.SIDEBAR_HOVER,
            text_color=Renkler.SIDEBAR_TEXT,
            corner_radius=8,
        )
        self.seg_tema.pack(fill="x", pady=(0, 4))
        self.seg_tema.set("🌙 Koyu" if current_theme == "Koyu" else "☀ Açık")
        
        # ── Kullanıcı Paneli ────────────────────────────────────────────────
        self.user_panel = ctk.CTkFrame(
            self.sidebar,
            fg_color=Renkler.SIDEBAR_HOVER,
            corner_radius=10
        )
        self.user_panel.pack(side="bottom", fill="x", padx=15, pady=(0, 15))
        
        # Kullanıcı avatar/icon
        avatar_frame = ctk.CTkFrame(
            self.user_panel,
            fg_color=Renkler.PRIMARY,
            width=36, height=36,
            corner_radius=18
        )
        avatar_frame.pack(side="left", padx=(12, 8), pady=12)
        avatar_frame.pack_propagate(False)
        initials = "".join([w[0].upper() for w in self.current_user['ad_soyad'].split()[:2]])
        ctk.CTkLabel(
            avatar_frame,
            text=initials[:2],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#FFFFFF"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        info_frame = ctk.CTkFrame(self.user_panel, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=12)
        
        self.lbl_user = ctk.CTkLabel(
            info_frame,
            text=self.current_user['ad_soyad'],
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=Renkler.SIDEBAR_TEXT,
            anchor="w"
        )
        self.lbl_user.pack(fill="x")
        
        self.lbl_role = ctk.CTkLabel(
            info_frame,
            text=self.current_user['rol'],
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=Renkler.TEXT_GRAY,
            anchor="w"
        )
        self.lbl_role.pack(fill="x")
        
        self.btn_logout = ctk.CTkButton(
            self.user_panel,
            text="↩",
            font=ctk.CTkFont(family="Segoe UI", size=16),
            fg_color="transparent",
            hover_color=Renkler.ERROR,
            text_color=Renkler.TEXT_GRAY,
            width=36,
            height=36,
            corner_radius=8,
            command=self.on_logout
        )
        self.btn_logout.pack(side="right", padx=(0, 8), pady=12)

    def _on_theme_change(self, value: str):
        """Kullanıcı tema butonuna bastığında çalışır."""
        new_theme = "Koyu" if "Koyu" in value else "Açık"
        
        # 1. ThemeManager ile renkleri güncelle
        ThemeManager.apply(new_theme)
        
        # 2. DB'deki değer ile farklıysa güncelle
        if self.current_user.get("tema") != new_theme:
            self.db.tema_guncelle(self.current_user["id"], new_theme)
            self.current_user["tema"] = new_theme
        
        # 3. Ana layout arka plan renklerini güncelle
        self.configure(fg_color=Renkler.BG_LIGHT)
        self.content_area.configure(fg_color=Renkler.BG_LIGHT)
        
        # 4. Sidebar renklerini güncelle
        self._refresh_sidebar_colors()
        
        # 5. Cached ekranların renklerini güncelle (destroy etmeden!)
        for screen in self.screens.values():
            try:
                if hasattr(screen, "apply_theme"):
                    screen.apply_theme()
            except Exception:
                pass
        
        # 6. Mevcut ekranı yeniden pack et (renkler güncellendikten sonra görünür olsun)
        if self.current_screen:
            self.current_screen.pack_forget()
            self.current_screen.pack(fill="both", expand=True)

    def _refresh_sidebar_colors(self):
        """Sidebar widget'larının renklerini tema değişiminde günceller."""
        self.sidebar.configure(fg_color=Renkler.SIDEBAR_BG)
        self.user_panel.configure(fg_color=Renkler.SIDEBAR_HOVER)
        self.lbl_logo.configure(text_color=Renkler.SIDEBAR_TEXT)
        self.lbl_user.configure(text_color=Renkler.SIDEBAR_TEXT)
        self.lbl_role.configure(text_color=Renkler.TEXT_GRAY)
        self.lbl_tema.configure(text_color=Renkler.TEXT_GRAY)
        self.btn_logout.configure(text_color=Renkler.TEXT_GRAY)
        
        # Menü butonları
        for menu in self.menus:
            btn = menu["btn"]
            if menu["name"] == (self.current_screen_name or "dashboard"):
                btn.configure(
                    fg_color=Renkler.PRIMARY,
                    text_color=Renkler.SIDEBAR_TEXT
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=Renkler.SIDEBAR_TEXT,
                    hover_color=Renkler.SIDEBAR_HOVER
                )
        
        # Kategori label'ları
        for lbl in getattr(self, "_cat_labels", []):
            lbl.configure(text_color=Renkler.TEXT_GRAY)
        
        # Segmented button
        self.seg_tema.configure(
            fg_color=Renkler.SIDEBAR_HOVER,
            selected_color=Renkler.PRIMARY,
            selected_hover_color=Renkler.PRIMARY_HOVER,
            unselected_color=Renkler.SIDEBAR_HOVER,
        )

    def add_category(self, title):
        lbl = ctk.CTkLabel(
            self.menu_scroll,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=Renkler.TEXT_GRAY,
            anchor="w"
        )
        lbl.pack(fill="x", padx=15, pady=(18, 4))
        if not hasattr(self, "_cat_labels"):
            self._cat_labels = []
        self._cat_labels.append(lbl)
        
    def add_menu_btn(self, text, screen_name, icon=""):
        btn = ctk.CTkButton(
            self.menu_scroll,
            text=f"  {icon}  {text}" if icon else text,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="transparent",
            text_color=Renkler.SIDEBAR_TEXT,
            hover_color=Renkler.SIDEBAR_HOVER,
            anchor="w",
            corner_radius=8,
            height=38,
            command=lambda sn=screen_name: self.show_screen(sn)
        )
        btn.pack(fill="x", padx=10, pady=2)
        self.menus.append({"btn": btn, "name": screen_name})

    def create_content_area(self):
        self.content_area = ctk.CTkFrame(
            self,
            fg_color=Renkler.BG_LIGHT,
            corner_radius=0
        )
        self.content_area.pack(side="right", fill="both", expand=True)
        
    def show_screen(self, screen_name):
        # Aktif menü butonunu güncelle
        for menu in self.menus:
            if menu["name"] == screen_name:
                menu["btn"].configure(
                    fg_color=Renkler.PRIMARY,
                    hover_color=Renkler.PRIMARY_HOVER,
                    text_color="#FFFFFF"
                )
            else:
                menu["btn"].configure(
                    fg_color="transparent",
                    hover_color=Renkler.SIDEBAR_HOVER,
                    text_color=Renkler.SIDEBAR_TEXT
                )
                
        # Mevcut ekranı gizle
        if self.current_screen:
            self.current_screen.pack_forget()
            
        # İstenen ekranı oluştur veya cache'den al
        is_new = screen_name not in self.screens
        if is_new:
            self.screens[screen_name] = self._create_screen(screen_name)
                
        self.current_screen_name = screen_name
        self.current_screen = self.screens[screen_name]
        if self.current_screen:
            self.current_screen.pack(fill="both", expand=True)
        
        # load_data: Yeni ekranda __init__ zaten çağırdı.
        # Sadece _needs_refresh=True ise tekrar yükle (veri değişince diğer ekranlar flag seter).
        if self.current_screen and not is_new:
            if getattr(self.current_screen, '_needs_refresh', False):
                if hasattr(self.current_screen, 'load_data'):
                    self.current_screen.load_data()
                self.current_screen._needs_refresh = False


    def mark_screen_refresh(self, screen_name):
        """Belirtilen ekranı bir sonraki görünümde yeniden yüklenecek şekilde işaretle."""
        if screen_name in self.screens:
            screen = self.screens[screen_name]
            if hasattr(screen, '_needs_refresh'):
                screen._needs_refresh = True

    def _create_screen(self, screen_name):
        """Ekran nesnesini oluşturur ve döner."""
        try:
            if screen_name == "dashboard":
                return DashboardScreen(self.content_area, self.current_user)
            elif screen_name == "teklifler":
                return TekliflerScreen(self.content_area, self.current_user)
            elif screen_name == "raporlar":
                from screens.raporlar_screen import RaporlarScreen
                return RaporlarScreen(self.content_area, self.current_user)
            elif screen_name == "takvim":
                from screens.takvim_screen import TakvimScreen
                return TakvimScreen(self.content_area, self.current_user)
            elif screen_name == "yeni_teklif":
                from screens.yeni_teklif_screen import YeniTeklifScreen
                return YeniTeklifScreen(self.content_area, self.current_user)
            elif screen_name == "musteriler":
                from screens.musteriler_screen import MusterilerScreen
                return MusterilerScreen(self.content_area, self.current_user)
            elif screen_name == "malzemeler":
                from screens.malzemeler_screen import MalzemelerScreen
                return MalzemelerScreen(self.content_area, self.current_user)
            elif screen_name == "islemler":
                from screens.islemler_screen import IslemlerScreen
                return IslemlerScreen(self.content_area, self.current_user)
            elif screen_name == "hurda":
                from screens.hurda_screen import HurdaScreen
                return HurdaScreen(self.content_area, self.current_user)
            elif screen_name == "proformalar":
                from screens.proformalar_screen import ProformalarScreen
                return ProformalarScreen(self.content_area, self.current_user)
            elif screen_name == "kullanicilar":
                from screens.kullanicilar_screen import KullanicilarScreen
                return KullanicilarScreen(self.content_area, self.current_user)
            elif screen_name == "ayarlar":
                from screens.ayarlar_screen import AyarlarScreen
                return AyarlarScreen(self.content_area, self.current_user)
            else:
                placeholder = ctk.CTkFrame(self.content_area, fg_color=Renkler.BG_LIGHT)
                lbl = ctk.CTkLabel(
                    placeholder,
                    text=f"{screen_name.capitalize()} — Yapım Aşamasında",
                    font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
                    text_color=Renkler.TEXT_DARK
                )
                lbl.pack(expand=True)
                return placeholder
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Hata durumunda bilgi ekranı göster
            err_frame = ctk.CTkFrame(self.content_area, fg_color=Renkler.BG_LIGHT)
            ctk.CTkLabel(
                err_frame,
                text=f"Ekran yüklenirken hata oluştu:\n{e}",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=Renkler.ERROR
            ).pack(expand=True)
            return err_frame
