"""
Tüm ekranların ekran görüntüsünü otomatik olarak alır.
Her ekran geçişinden sonra screenshot kaydeder.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from PIL import ImageGrab
import time

# Uygulama bileşenlerini import et
import database
from tema import ThemeManager, Renkler
from screens.main_layout import MainLayout

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Koyu tema için
ThemeManager.apply("Koyu")

db = database.Database()
user = db.login("admin", "1234")
if not user:
    user = db.login("ogz", "1")
if not user:
    print("Kullanici bulunamadi!")
    sys.exit(1)

user = dict(user)
# Temayı uygula
ThemeManager.apply(user.get("tema", "Koyu"))

root = ctk.CTk()
root.geometry("1380x830")
root.title("Atolye Yonetim - Screenshots")
root.state("normal")
root.deiconify()
root.lift()
root.focus_force()
root.attributes("-topmost", True)   # pencere HEP üstte kalır
root.update()
time.sleep(1.0)
root.update()

def take_screenshot(name):
    root.lift()
    root.focus_force()
    root.update()
    time.sleep(1.2)
    root.update_idletasks()
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    w = root.winfo_width()
    h = root.winfo_height()
    path = os.path.join(OUTPUT_DIR, f"{name}.png")
    try:
        img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        img.save(path)
        sys.stdout.buffer.write(f"  OK {path}\n".encode("utf-8"))
    except OSError as e:
        sys.stdout.buffer.write(f"  Warning: Screen grab failed for {name} ({e}). Ensure screen is unlocked.\n".encode("utf-8"))
    sys.stdout.buffer.flush()
    return path

layout = None

def on_logout():
    pass

layout = MainLayout(root, user, on_logout)
layout.pack(fill="both", expand=True)
root.update()

SCREENS = [
    ("dashboard",       "01_dashboard"),
    ("teklifler",       "02_teklifler"),
    ("yeni_teklif",     "03_yeni_teklif"),
    ("musteriler",      "04_musteriler"),
    ("raporlar",        "05_raporlar"),
    ("takvim",          "06_takvim"),
    ("malzemeler",      "07_malzemeler"),
    ("islemler",        "08_islemler"),
    ("hurda",           "09_hurda"),
    ("proformalar",     "10_proformalar"),
    ("ayarlar",         "11_ayarlar"),
]

idx = [0]

def capture_next():
    if idx[0] >= len(SCREENS):
        sys.stdout.buffer.write(b"\nTum ekranlar kaydedildi!\n")
        sys.stdout.buffer.flush()
        root.destroy()
        return
    screen_key, fname = SCREENS[idx[0]]
    sys.stdout.buffer.write(f"Ekran: {screen_key}\n".encode("utf-8"))
    sys.stdout.buffer.flush()
    try:
        layout.show_screen(screen_key)
    except Exception as e:
        sys.stdout.buffer.write(f"  ! hatasi: {e}\n".encode("utf-8"))
        sys.stdout.buffer.flush()
    idx[0] += 1
    root.after(1000, lambda: _snap(fname))

def _snap(fname):
    take_screenshot(fname)
    root.after(200, capture_next)

root.after(2000, capture_next)
root.mainloop()
sys.stdout.buffer.write(b"Bitti.\n")
sys.stdout.buffer.flush()
