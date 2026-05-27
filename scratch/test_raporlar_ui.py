import sys
import os
sys.path.insert(0, r'c:\Users\oguza\OneDrive\Desktop\atolye_yonetim')

import customtkinter as ctk
import database
from screens.main_layout import MainLayout
from outputs.rapor_exporter import export_rapor_to_excel, export_rapor_to_pdf
from PIL import ImageGrab

def run_test():
    app = ctk.CTk()
    app.geometry("1280x800")
    
    # Window settings to ensure focus
    app.lift()
    app.attributes('-topmost', True)
    app.focus_force()
    
    db = database.Database()
    user = db.login('admin', '1234')
    if not user:
        print("Hata: admin kullanıcısı giriş yapamadı!")
        return
        
    print("MainLayout yükleniyor...")
    layout = MainLayout(app, user, lambda: None)
    layout.pack(fill="both", expand=True)
    
    print("Raporlar ekranı açılıyor...")
    layout.show_screen("raporlar")
    
    # Wait for UI rendering
    app.update_idletasks()
    app.update()
    app.after(1500)
    app.update()
    
    # Save a screenshot to the conversation brain directory
    artifact_dir = r"C:\Users\oguza\.gemini\antigravity\brain\45d41a8a-911d-41da-ac5c-67d25ba0dd04"
    os.makedirs(artifact_dir, exist_ok=True)
    
    x = app.winfo_rootx()
    y = app.winfo_rooty()
    w = app.winfo_width()
    h = app.winfo_height()
    
    if w < 100 or h < 100:
        x, y, w, h = 0, 0, 1280, 800
        
    image = ImageGrab.grab(bbox=(x, y, x+w, y+h))
    img_path = os.path.join(artifact_dir, "raporlar_screenshot.png")
    image.save(img_path)
    print(f"Raporlar ekran görüntüsü kaydedildi: {img_path}")
    
    # Programmatic check for export methods to verify they work with screen data
    screen = layout.screens["raporlar"]
    report_data = screen.report_data
    
    # Veriler boş değilse exportları test et
    if report_data and "kpi" in report_data:
        print("Excel ihracatı test ediliyor...")
        test_xlsx = "outputs/excel/test_rapor_autogen.xlsx"
        export_rapor_to_excel(report_data, test_xlsx)
        print(f"Excel başarıyla oluşturuldu: {test_xlsx}")
        
        print("PDF ihracatı test ediliyor...")
        test_pdf = "outputs/pdf/test_rapor_autogen.pdf"
        export_rapor_to_pdf(report_data, test_pdf)
        print(f"PDF başarıyla oluşturuldu: {test_pdf}")
    else:
        print("Hata: Rapor verileri doldurulamadı!")
        
    # Tema değişimi test ediliyor
    print("Tema Koyu moda geçiriliyor...")
    layout.seg_tema.set("Koyu")
    layout._on_theme_change("Koyu")
    app.update()
    app.after(1000)
    app.update()
    
    # Koyu mod ekran görüntüsü kaydet
    image_dark = ImageGrab.grab(bbox=(x, y, x+w, y+h))
    img_dark_path = os.path.join(artifact_dir, "raporlar_screenshot_dark.png")
    image_dark.save(img_dark_path)
    print(f"Raporlar Koyu mod ekran görüntüsü kaydedildi: {img_dark_path}")
    
    app.destroy()
    print("Test başarıyla tamamlandı!")

if __name__ == '__main__':
    run_test()
