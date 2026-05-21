import sys
sys.path.insert(0, r'c:\Users\oguza\OneDrive\Desktop\atolye_yonetim')

import customtkinter as ctk
import database
from screens.main_layout import MainLayout
import os
from PIL import ImageGrab

def take_screenshots():
    app = ctk.CTk()
    app.geometry("1280x720")
    
    # Pencereyi ön plana çıkar ve odakla
    app.lift()
    app.attributes('-topmost', True)
    app.focus_force()
    
    db = database.Database()
    user = db.login('admin', '1234')
    
    layout = MainLayout(app, user, lambda: None)
    layout.pack(fill="both", expand=True)
    
    artifact_dir = r"C:\Users\oguza\.gemini\antigravity\brain\212781eb-004c-4be7-a637-187779f7fcc0"
    os.makedirs(artifact_dir, exist_ok=True)
    
    screens_to_test = ["proformalar", "kullanicilar", "ayarlar"]
    
    for screen in screens_to_test:
        print(f"{screen} ekranı yükleniyor...")
        layout.show_screen(screen)
        
        # UI'ın çizilmesini bekle
        app.update_idletasks()
        app.update()
        app.after(1000)
        app.update()
        
        x = app.winfo_rootx()
        y = app.winfo_rooty()
        w = app.winfo_width()
        h = app.winfo_height()
        
        # Koordinatların sıfır olmamasını garanti et
        if w < 100 or h < 100:
            x, y, w, h = 0, 0, 1280, 720
            
        image = ImageGrab.grab(bbox=(x, y, x+w, y+h))
        img_path = os.path.join(artifact_dir, f"{screen}_screenshot.png")
        image.save(img_path)
        print(f"{screen} screenshot saved to: {img_path}")
        
    app.destroy()

if __name__ == '__main__':
    take_screenshots()
