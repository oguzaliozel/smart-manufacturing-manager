"""
tema.py — Merkezi Tema Yönetim Sistemi
Açık ve Koyu tema için tüm renk değerlerini tutar.
ThemeManager ile dinamik olarak değiştirilebilir.
"""
import customtkinter as ctk

# ── RENK PALETLERİ ────────────────────────────────────────────────────────────

LIGHT_COLORS = {
    "BG_LIGHT":        "#F5F7FB",
    "CARD_BG":         "#FFFFFF",
    "CARD_BG2":        "#F8FAFC",
    "SIDEBAR_BG":      "#172033",
    "SIDEBAR_HOVER":   "#22304A",
    "PRIMARY":         "#2F6BFF",
    "PRIMARY_HOVER":   "#1D4ED8",
    "TEXT_DARK":       "#0F172A",
    "TEXT_LIGHT":      "#F8FAFC",
    "TEXT_GRAY":       "#64748B",
    "TEXT_HEADING":    "#0B1220",
    "BORDER":          "#E2E8F0",
    "INPUT_BG":        "#FFFFFF",
    "INPUT_BORDER":    "#CBD5E1",
    "SUCCESS":         "#16A34A",
    "WARNING":         "#F59E0B",
    "ERROR":           "#DC2626",
    "INFO":            "#2563EB",
    # Sidebar yazı rengi (açık temada sidebar koyu)
    "SIDEBAR_TEXT":    "#F8FAFC",
    "BG_DARK":         "#0F172A",
}

DARK_COLORS = {
    "BG_LIGHT":        "#0F172A",
    "CARD_BG":         "#111827",
    "CARD_BG2":        "#1E293B",
    "SIDEBAR_BG":      "#020617",
    "SIDEBAR_HOVER":   "#1E293B",
    "PRIMARY":         "#2563EB",
    "PRIMARY_HOVER":   "#1D4ED8",
    "TEXT_DARK":       "#F8FAFC",
    "TEXT_LIGHT":      "#F8FAFC",
    "TEXT_GRAY":       "#94A3B8",
    "TEXT_HEADING":    "#FFFFFF",
    "BORDER":          "#334155",
    "INPUT_BG":        "#0F172A",
    "INPUT_BORDER":    "#334155",
    "SUCCESS":         "#22C55E",
    "WARNING":         "#F59E0B",
    "ERROR":           "#EF4444",
    "INFO":            "#3B82F6",
    # Sidebar yazı rengi
    "SIDEBAR_TEXT":    "#F8FAFC",
    "BG_DARK":         "#020617",
}


# ── RENKLER SINIFI — Dinamik class attribute'lar ──────────────────────────────

class Renkler:
    """
    Merkezi renk sınıfı. Her bir renk (Açık, Koyu) olacak şekilde tuple formatındadır.
    Bu sayede CustomTkinter widget'ları tema geçişlerinde otomatik olarak güncellenir.
    """
    BG_LIGHT        = (LIGHT_COLORS["BG_LIGHT"], DARK_COLORS["BG_LIGHT"])
    CARD_BG         = (LIGHT_COLORS["CARD_BG"], DARK_COLORS["CARD_BG"])
    CARD_BG2        = (LIGHT_COLORS["CARD_BG2"], DARK_COLORS["CARD_BG2"])
    SIDEBAR_BG      = (LIGHT_COLORS["SIDEBAR_BG"], DARK_COLORS["SIDEBAR_BG"])
    SIDEBAR_HOVER   = (LIGHT_COLORS["SIDEBAR_HOVER"], DARK_COLORS["SIDEBAR_HOVER"])
    PRIMARY         = (LIGHT_COLORS["PRIMARY"], DARK_COLORS["PRIMARY"])
    PRIMARY_HOVER   = (LIGHT_COLORS["PRIMARY_HOVER"], DARK_COLORS["PRIMARY_HOVER"])
    TEXT_DARK       = (LIGHT_COLORS["TEXT_DARK"], DARK_COLORS["TEXT_DARK"])
    TEXT_LIGHT      = (LIGHT_COLORS["TEXT_LIGHT"], DARK_COLORS["TEXT_LIGHT"])
    TEXT_GRAY       = (LIGHT_COLORS["TEXT_GRAY"], DARK_COLORS["TEXT_GRAY"])
    TEXT_HEADING    = (LIGHT_COLORS["TEXT_HEADING"], DARK_COLORS["TEXT_HEADING"])
    BORDER          = (LIGHT_COLORS["BORDER"], DARK_COLORS["BORDER"])
    INPUT_BG        = (LIGHT_COLORS["INPUT_BG"], DARK_COLORS["INPUT_BG"])
    INPUT_BORDER    = (LIGHT_COLORS["INPUT_BORDER"], DARK_COLORS["INPUT_BORDER"])
    SUCCESS         = (LIGHT_COLORS["SUCCESS"], DARK_COLORS["SUCCESS"])
    WARNING         = (LIGHT_COLORS["WARNING"], DARK_COLORS["WARNING"])
    ERROR           = (LIGHT_COLORS["ERROR"], DARK_COLORS["ERROR"])
    INFO            = (LIGHT_COLORS["INFO"], DARK_COLORS["INFO"])
    SIDEBAR_TEXT    = (LIGHT_COLORS["SIDEBAR_TEXT"], DARK_COLORS["SIDEBAR_TEXT"])
    BG_DARK         = (LIGHT_COLORS["BG_DARK"], DARK_COLORS["BG_DARK"])

    @classmethod
    def get(cls, color_value):
        """
        Matplotlib veya diğer standart kütüphaneler için 
        aktif temaya göre tek bir renk string değeri döner.
        """
        if isinstance(color_value, tuple) and len(color_value) == 2:
            return color_value[1 if ThemeManager.is_dark() else 0]
        return color_value


# ── FONTLAR SINIFI ────────────────────────────────────────────────────────────

class Fontlar:
    FAMILY = "Segoe UI"
    
    H1         = (FAMILY, 24, "bold")
    H2         = (FAMILY, 20, "bold")
    H3         = (FAMILY, 16, "bold")
    
    BODY       = (FAMILY, 14)
    BODY_BOLD  = (FAMILY, 14, "bold")
    
    SMALL      = (FAMILY, 12)
    SMALL_BOLD = (FAMILY, 12, "bold")

    # CTkFont nesneleri — CTkinter widget'larında kullanmak için
    @staticmethod
    def ctk_font(size=13, weight="normal", family="Segoe UI"):
        return ctk.CTkFont(family=family, size=size, weight=weight)


# ── TEMA YÖNETİCİSİ ──────────────────────────────────────────────────────────

class ThemeManager:
    """
    Merkezi tema yöneticisi.
    Kullanım: ThemeManager.apply("Koyu") veya ThemeManager.apply("Açık")
    """
    _current_theme: str = "Açık"
    _callbacks: list = []

    @classmethod
    def current(cls) -> str:
        return cls._current_theme

    @classmethod
    def is_dark(cls) -> bool:
        return cls._current_theme == "Koyu"

    @classmethod
    def apply(cls, theme_name: str):
        """
        Tema adını alır ('Açık' veya 'Koyu') ve CTkinter görünüm modunu ayarlar.
        """
        cls._current_theme = theme_name
        
        # CTkinter'ın kendi dark/light modunu ayarla
        ctk_mode = "Dark" if theme_name == "Koyu" else "Light"
        ctk.set_appearance_mode(ctk_mode)
        
        # Kayıtlı callback'leri çağır
        for cb in cls._callbacks:
            try:
                cb(theme_name)
            except Exception:
                pass

    @classmethod
    def register_callback(cls, callback):
        """Tema değişiminde çağrılacak fonksiyon kaydet."""
        if callback not in cls._callbacks:
            cls._callbacks.append(callback)

    @classmethod
    def unregister_callback(cls, callback):
        if callback in cls._callbacks:
            cls._callbacks.remove(callback)

    @classmethod
    def get_ctk_mode(cls) -> str:
        return "Dark" if cls._current_theme == "Koyu" else "Light"
