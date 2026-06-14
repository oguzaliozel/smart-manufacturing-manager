import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from PIL import ImageGrab
import time
import database
from tema import ThemeManager
from screens.main_layout import MainLayout

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

db = database.Database()
user = db.login("admin", "1234")
if not user:
    user = db.login("ogz", "1")
user = dict(user)

def capture_dashboard(theme_name, filename):
    ThemeManager.apply(theme_name)
    user["tema"] = theme_name
    
    root = ctk.CTk()
    root.geometry("1380x830")
    root.title(f"Dashboard - {theme_name}")
    root.state("normal")
    root.deiconify()
    root.lift()
    root.focus_force()
    root.attributes("-topmost", True)
    root.update()
    
    def on_logout():
        pass
        
    layout = MainLayout(root, user, on_logout)
    layout.pack(fill="both", expand=True)
    
    # Force theme on layout
    if hasattr(layout, "apply_theme"):
        layout.apply_theme()
        
    layout.show_screen("dashboard")
    
    root.update()
    time.sleep(2.5) # Wait for charts to render and settle
    root.update_idletasks()
    
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    w = root.winfo_width()
    h = root.winfo_height()
    
    path = os.path.join(OUTPUT_DIR, filename)
    try:
        img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        img.save(path)
        sys.stdout.buffer.write(f"Captured Dashboard {theme_name} -> {path}\n".encode("utf-8"))
    except OSError as e:
        sys.stdout.buffer.write(f"Warning: Screen grab failed for {theme_name} ({e}). Ensure screen is unlocked.\n".encode("utf-8"))
    
    root.destroy()
    sys.stdout.buffer.flush()

capture_dashboard("Koyu", "01_dashboard_dark.png")
capture_dashboard("Açık", "01_dashboard_light.png")
sys.stdout.buffer.write(b"Dashboard theme screenshots complete.\n")
sys.stdout.buffer.flush()
