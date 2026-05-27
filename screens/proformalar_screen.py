import customtkinter as ctk
from tema import Renkler, Fontlar
import database
import os
from datetime import datetime
from tkinter import messagebox
from outputs.exporter import export_to_pdf, export_to_excel

class ProformalarScreen(ctk.CTkFrame):
    def __init__(self, master, current_user):
        super().__init__(master, fg_color=Renkler.BG_LIGHT)
        self.current_user = current_user
        self.db = database.Database()
        self._needs_refresh = False
        
        self.secili_proforma_id = None
        self.secili_proforma = None
        self.kalemler_listesi = []
        
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # ── ÜST BAŞLIK ALANI ──────────────────────────────────────────────────
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(30, 15))
        
        ctk.CTkLabel(
            self.header_frame, 
            text="Proforma Faturalar", 
            font=Fontlar.H1, 
            text_color=Renkler.TEXT_DARK
        ).pack(side="left")

        # Arama Kutusu
        self.entry_ara = ctk.CTkEntry(
            self.header_frame, 
            placeholder_text="Proforma No veya Müşteri Ara...", 
            width=260, 
            font=Fontlar.SMALL
        )
        self.entry_ara.pack(side="right", padx=10)
        self.entry_ara.bind("<KeyRelease>", lambda e: self.load_data())

        # ── ANA İÇERİK ALANI (BÖLÜNMÜŞ DÜZEN) ─────────────────────────────────
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        self.content_frame.grid_columnconfigure(0, weight=5) # Sol Liste
        self.content_frame.grid_columnconfigure(1, weight=5) # Sağ Detay
        self.content_frame.grid_rowconfigure(0, weight=1)

        # ── SOL: TABLO / LİSTE KARTI ──────────────────────────────────────────
        self.left_card = ctk.CTkFrame(self.content_frame, fg_color=Renkler.CARD_BG, corner_radius=10)
        self.left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        # Tablo Başlıkları
        self.table_header = ctk.CTkFrame(self.left_card, fg_color="transparent")
        self.table_header.pack(fill="x", padx=15, pady=10)
        self.table_header.grid_columnconfigure(0, weight=3) # No
        self.table_header.grid_columnconfigure(1, weight=4) # Müşteri
        self.table_header.grid_columnconfigure(2, weight=3) # Tutar
        
        ctk.CTkLabel(self.table_header, text="Proforma No", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_GRAY, anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(self.table_header, text="Müşteri", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_GRAY, anchor="w").grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(self.table_header, text="Toplam Tutar", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_GRAY, anchor="e").grid(row=0, column=2, sticky="e")
        
        ctk.CTkFrame(self.left_card, fg_color=Renkler.BORDER, height=1).pack(fill="x", padx=15)

        # Kaydırılabilir Liste
        self.list_scroll = ctk.CTkScrollableFrame(self.left_card, fg_color="transparent")
        self.list_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # ── SAĞ: FATURA / DETAY KARTI ─────────────────────────────────────────
        self.right_card = ctk.CTkFrame(self.content_frame, fg_color=Renkler.CARD_BG, corner_radius=10)
        self.right_card.grid(row=0, column=1, sticky="nsew")
        
        # Detay Kartı Boş Durum
        self.empty_label = ctk.CTkLabel(
            self.right_card, 
            text="Detayları görüntülemek için\nsoldan bir proforma seçin.", 
            font=Fontlar.BODY, 
            text_color=Renkler.TEXT_GRAY,
            justify="center"
        )
        self.empty_label.pack(expand=True)
        
        # Detay Paneli Çerçevesi (Gizli başlayacak)
        self.detail_panel = ctk.CTkFrame(self.right_card, fg_color="transparent")
        
        # Detay Başlığı
        self.lbl_detail_title = ctk.CTkLabel(self.detail_panel, text="PROFORMA DETAYI", font=Fontlar.H3, text_color=Renkler.PRIMARY)
        self.lbl_detail_title.pack(anchor="w", padx=20, pady=(20, 5))
        
        # Kaydırılabilir İçerik
        self.detail_scroll = ctk.CTkScrollableFrame(self.detail_panel, fg_color="transparent")
        self.detail_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Fatura Görünümlü Kart
        self.invoice_card = ctk.CTkFrame(self.detail_scroll, fg_color="#F8FAFC", corner_radius=8, border_color=Renkler.BORDER, border_width=1)
        self.invoice_card.pack(fill="x", padx=15, pady=10)
        
        # Fatura No & Tarih Satırı
        self.row_info = ctk.CTkFrame(self.invoice_card, fg_color="transparent")
        self.row_info.pack(fill="x", padx=15, pady=10)
        self.lbl_inv_no = ctk.CTkLabel(self.row_info, text="No: -", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_DARK)
        self.lbl_inv_no.pack(side="left")
        self.lbl_inv_date = ctk.CTkLabel(self.row_info, text="Tarih: -", font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY)
        self.lbl_inv_date.pack(side="right")
        
        # Müşteri Bilgileri
        self.lbl_cust_title = ctk.CTkLabel(self.invoice_card, text="MÜŞTERİ BİLGİLERİ", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_GRAY, anchor="w")
        self.lbl_cust_title.pack(fill="x", padx=15, pady=(5, 1))
        self.lbl_cust_name = ctk.CTkLabel(self.invoice_card, text="-", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_DARK, anchor="w")
        self.lbl_cust_name.pack(fill="x", padx=15, pady=(0, 5))
        
        # Finansal Özet Tablosu
        self.lbl_fin_title = ctk.CTkLabel(self.invoice_card, text="MALİYET & FİYAT ÖZETİ", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_GRAY, anchor="w")
        self.lbl_fin_title.pack(fill="x", padx=15, pady=(10, 1))
        
        self.summary_table = ctk.CTkFrame(self.invoice_card, fg_color="transparent")
        self.summary_table.pack(fill="x", padx=15, pady=5)
        
        self.lbl_val_maliyet = self.create_inv_row(self.summary_table, "Net Üretim Maliyeti:")
        self.lbl_val_kar = self.create_inv_row(self.summary_table, "Kar Tutarı:")
        self.lbl_val_indirim = self.create_inv_row(self.summary_table, "Manuel İndirim:")
        self.lbl_val_toplam = self.create_inv_row(self.summary_table, "Toplam Tutar (KDV Hariç):", is_bold=True, text_color=Renkler.PRIMARY)
        self.lbl_val_hurda = self.create_inv_row(self.summary_table, "Geri Kazanılabilir Hurda Değeri:", text_color=Renkler.WARNING)

        # Alt Buton Paneli
        self.actions_panel = ctk.CTkFrame(self.detail_panel, fg_color="transparent")
        self.actions_panel.pack(fill="x", padx=20, pady=20, side="bottom")
        
        self.btn_open_pdf = ctk.CTkButton(
            self.actions_panel, 
            text="PDF Olarak Aç/Yazdır", 
            font=Fontlar.BODY_BOLD, 
            fg_color=Renkler.PRIMARY, 
            hover_color=Renkler.PRIMARY_HOVER, 
            command=self.open_pdf
        )
        self.btn_open_pdf.pack(fill="x", pady=4)
        
        self.btn_open_excel = ctk.CTkButton(
            self.actions_panel, 
            text="Excel Raporu Aç", 
            font=Fontlar.BODY_BOLD, 
            fg_color="#10B981", 
            hover_color="#0D9488", 
            command=self.open_excel
        )
        self.btn_open_excel.pack(fill="x", pady=4)

    def create_inv_row(self, parent, label_text, is_bold=False, text_color=Renkler.TEXT_DARK):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=3)
        font_lbl = Fontlar.SMALL_BOLD if is_bold else Fontlar.SMALL
        font_val = Fontlar.BODY_BOLD if is_bold else Fontlar.SMALL_BOLD
        
        ctk.CTkLabel(frame, text=label_text, font=font_lbl, text_color=Renkler.TEXT_GRAY).pack(side="left")
        val = ctk.CTkLabel(frame, text="0.00 ₺", font=font_val, text_color=text_color)
        val.pack(side="right")
        
        ctk.CTkFrame(parent, fg_color=Renkler.BORDER, height=1).pack(fill="x", pady=1)
        return val

    def load_data(self):
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
            
        arama_kelimesi = self.entry_ara.get().strip()
        user_id = self.current_user["id"]
        
        conn = self.db.connect()
        cursor = conn.cursor()
        
        # Sadece durum = 'Onaylandı' olan teklifler proformadır
        query = """
            SELECT t.*, m.firma_adi 
            FROM teklifler t
            LEFT JOIN musteriler m ON t.musteri_id = m.id
            WHERE t.kullanici_id = ? AND t.durum = 'Onaylandı'
        """
        params = [user_id]
        
        if arama_kelimesi:
            query += " AND (t.teklif_no LIKE ? OR m.firma_adi LIKE ?)"
            params.extend([f"%{arama_kelimesi}%", f"%{arama_kelimesi}%"])
            
        query += " ORDER BY t.id DESC"
        
        cursor.execute(query, params)
        proformalar = cursor.fetchall()
        conn.close()
        
        if not proformalar:
            ctk.CTkLabel(self.list_scroll, text="Onaylanmış proforma bulunamadı.", font=Fontlar.BODY, text_color=Renkler.TEXT_GRAY).pack(pady=40)
            self.hide_detail()
            return
            
        for p in proformalar:
            satir = ctk.CTkFrame(self.list_scroll, fg_color="transparent")
            satir.pack(fill="x", pady=2, padx=5)
            satir.grid_columnconfigure(0, weight=3)
            satir.grid_columnconfigure(1, weight=4)
            satir.grid_columnconfigure(2, weight=3)
            
            btn_no = ctk.CTkButton(
                satir, 
                text=p["teklif_no"], 
                font=Fontlar.SMALL_BOLD, 
                fg_color="transparent", 
                text_color=Renkler.TEXT_DARK, 
                hover_color=Renkler.BORDER,
                anchor="w",
                command=lambda item=dict(p): self.select_proforma(item)
            )
            btn_no.grid(row=0, column=0, sticky="ew")
            
            lbl_firma = ctk.CTkLabel(satir, text=p["firma_adi"] or "Bireysel", font=Fontlar.SMALL, text_color=Renkler.TEXT_DARK, anchor="w")
            lbl_firma.grid(row=0, column=1, sticky="w", padx=10)
            
            lbl_tutar = ctk.CTkLabel(satir, text=f"{p['son_tutar'] or 0:,.2f} ₺", font=Fontlar.SMALL_BOLD, text_color=Renkler.PRIMARY, anchor="e")
            lbl_tutar.grid(row=0, column=2, sticky="e", padx=10)
            
            ctk.CTkFrame(self.list_scroll, fg_color=Renkler.BORDER, height=1).pack(fill="x", pady=2)

    def select_proforma(self, p):
        self.secili_proforma_id = p["id"]
        self.secili_proforma = p
        
        # Veritabanından kalemleri çek
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teklif_kalemleri WHERE teklif_id = ?", (p["id"],))
        self.kalemler_listesi = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Arayüzü güncelle
        self.empty_label.pack_forget()
        self.detail_panel.pack(fill="both", expand=True)
        
        self.lbl_inv_no.configure(text=f"Proforma No: {p['teklif_no']}")
        self.lbl_inv_date.configure(text=f"Tarih: {p['olusturma_tarihi']}")
        self.lbl_cust_name.configure(text=p["firma_adi"] or "Bireysel Müşteri")
        
        self.lbl_val_maliyet.configure(text=f"{p['malzeme_maliyeti'] + p['makine_maliyeti'] + p['ek_gider']:,.2f} ₺")
        self.lbl_val_kar.configure(text=f"{p['kar_tutari']:,.2f} ₺")
        self.lbl_val_indirim.configure(text=f"-{p['manuel_indirim']:,.2f} ₺")
        self.lbl_val_toplam.configure(text=f"{p['son_tutar']:,.2f} ₺")
        self.lbl_val_hurda.configure(text=f"{p['tahmini_hurda_degeri']:,.2f} ₺")

    def hide_detail(self):
        self.detail_panel.pack_forget()
        self.empty_label.pack(expand=True)
        self.secili_proforma_id = None
        self.secili_proforma = None

    def export_files(self):
        if not self.secili_proforma: return None, None
        
        os.makedirs("outputs/pdf", exist_ok=True)
        os.makedirs("outputs/excel", exist_ok=True)
        
        p_no_clean = self.secili_proforma["teklif_no"].replace("/", "-").replace("\\", "-")
        pdf_path = f"outputs/pdf/proforma_{p_no_clean}.pdf"
        excel_path = f"outputs/excel/proforma_{p_no_clean}.xlsx"
        
        # export metotlarını çağır
        export_to_pdf(self.secili_proforma, self.kalemler_listesi, pdf_path)
        export_to_excel(self.secili_proforma, self.kalemler_listesi, excel_path)
        
        return pdf_path, excel_path

    def open_pdf(self):
        try:
            pdf_path, _ = self.export_files()
            if pdf_path and os.path.exists(pdf_path):
                os.startfile(pdf_path)
        except Exception as e:
            messagebox.showerror("Hata", f"PDF açılamadı:\n{e}")

    def open_excel(self):
        try:
            _, excel_path = self.export_files()
            if excel_path and os.path.exists(excel_path):
                os.startfile(excel_path)
        except Exception as e:
            messagebox.showerror("Hata", f"Excel açılamadı:\n{e}")

    def apply_theme(self):
        """Tema değişiminde ana renkleri günceller."""
        self.configure(fg_color=Renkler.BG_LIGHT)
        try:
            self.left_card.configure(fg_color=Renkler.CARD_BG)
            self.right_card.configure(fg_color=Renkler.CARD_BG)
        except Exception:
            pass
        self._needs_refresh = True
