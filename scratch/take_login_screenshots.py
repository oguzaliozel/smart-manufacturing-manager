import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from PIL import ImageGrab
import time
from tema import ThemeManager
from screens.login_screen import LoginScreen

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def capture_theme(theme_name, filename):
    root = ctk.CTk()
    root.geometry("1380x830")
    root.title(f"Login Screen - {theme_name}")
    root.state("normal")
    
    ThemeManager.apply(theme_name)
    
    root.deiconify()
    root.lift()
    root.focus_force()
    root.attributes("-topmost", True)
    root.update()
    
    def on_login(user):
        pass
        
    login_scr = LoginScreen(root, on_login)
    login_scr.pack(fill="both", expand=True)
    
    root.update()
    time.sleep(2.0) # Wait for rendering
    root.update_idletasks()
    
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    w = root.winfo_width()
    h = root.winfo_height()
    
    path = os.path.join(OUTPUT_DIR, filename)
    try:
        img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        img.save(path)
        sys.stdout.buffer.write(f"Captured {theme_name} -> {path}\n".encode("utf-8"))
    except OSError as e:
        sys.stdout.buffer.write(f"Warning: Screen grab failed for {theme_name} ({e}). Ensure screen is unlocked.\n".encode("utf-8"))
    
    root.destroy()
    sys.stdout.buffer.flush()

# Capture both
capture_theme("Açık", "00_login_light.png")
capture_theme("Koyu", "00_login_dark.png")
sys.stdout.buffer.write(b"Login screenshots complete.\n")
sys.stdout.buffer.flush()
