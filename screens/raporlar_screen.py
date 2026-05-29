import os
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import sqlite3

from tema import Renkler, Fontlar
import database
from outputs.rapor_exporter import export_rapor_to_excel, export_rapor_to_pdf

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.delay = 300
        self.id = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hide()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def show(self):
        if self.tooltip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            tw, 
            text=self.text, 
            justify='left',
            background='#1E293B',
            foreground='#FFFFFF',
            relief='solid', 
            border=0,
            padx=8,
            pady=4,
            font=("Inter", 9, "normal")
        )
        label.pack(ipadx=1)
        tw.configure(background='#1E293B')

    def hide(self):
        tw = self.tooltip_window
        self.tooltip_window = None
        if tw:
            tw.destroy()


class RaporlarScreen(ctk.CTkFrame):
    def __init__(self, master, current_user):
        super().__init__(master, fg_color=Renkler.BG_LIGHT)
        self.current_user = current_user
        self.db = database.Database()
        self._needs_refresh = False
        
        # Seçim mapping'leri (ID ve İsim eşleşmeleri için)
        self.customer_list = []
        self.operation_list = []
        
        # Son hesaplanan rapor verilerini saklar (Export için)
        self.report_data = {}
        
        self.create_widgets()
        self.load_filters_data()
        self.load_data()

    def create_widgets(self):
        # Dikey kaydırılabilir ana container
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ── 1. BAŞLIK ALANI ───────────────────────────────────────────────────
        self.header_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=25, pady=(20, 10))
        
        self.lbl_title = ctk.CTkLabel(self.header_frame, text="Raporlar", font=Fontlar.H1, text_color=Renkler.TEXT_DARK)
        self.lbl_title.pack(anchor="w")
        
        self.lbl_subtitle = ctk.CTkLabel(
            self.header_frame, 
            text="Teklif, kar, maliyet ve üretim analizleri", 
            font=Fontlar.BODY, 
            text_color=Renkler.TEXT_GRAY
        )
        self.lbl_subtitle.pack(anchor="w", pady=(2, 0))

        # ── 2. ÜST FİLTRE KARTI ───────────────────────────────────────────────
        self.filter_card = ctk.CTkFrame(self.scroll_container, fg_color=Renkler.CARD_BG, corner_radius=10)
        self.filter_card.pack(fill="x", padx=25, pady=10)
        
        # Filtre Grid Yerleşimi (5 Sütunlu)
        self.filter_card.grid_columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="filter")
        
        # A: Başlangıç Tarihi
        f_start_frame = ctk.CTkFrame(self.filter_card, fg_color="transparent")
        f_start_frame.grid(row=0, column=0, padx=10, pady=15, sticky="nsew")
        self.lbl_f_start = ctk.CTkLabel(f_start_frame, text="Başlangıç Tarihi (YYYY-MM-DD)", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK)
        self.lbl_f_start.pack(anchor="w", pady=(0, 4))
        self.ent_start_date = ctk.CTkEntry(f_start_frame, placeholder_text="YYYY-MM-DD", font=Fontlar.SMALL)
        self.ent_start_date.pack(fill="x")
        self.ent_start_date.insert(0, f"{datetime.now().year}-01-01") # Varsayılan: Yılın başı
        
        # B: Bitiş Tarihi
        f_end_frame = ctk.CTkFrame(self.filter_card, fg_color="transparent")
        f_end_frame.grid(row=0, column=1, padx=10, pady=15, sticky="nsew")
        self.lbl_f_end = ctk.CTkLabel(f_end_frame, text="Bitiş Tarihi (YYYY-MM-DD)", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK)
        self.lbl_f_end.pack(anchor="w", pady=(0, 4))
        self.ent_end_date = ctk.CTkEntry(f_end_frame, placeholder_text="YYYY-MM-DD", font=Fontlar.SMALL)
        self.ent_end_date.pack(fill="x")
        self.ent_end_date.insert(0, datetime.now().strftime("%Y-%m-%d")) # Varsayılan: Bugün
        
        # C: Müşteri Seçimi
        f_cust_frame = ctk.CTkFrame(self.filter_card, fg_color="transparent")
        f_cust_frame.grid(row=0, column=2, padx=10, pady=15, sticky="nsew")
        self.lbl_f_cust = ctk.CTkLabel(f_cust_frame, text="Müşteri Firma", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK)
        self.lbl_f_cust.pack(anchor="w", pady=(0, 4))
        self.cb_customer = ctk.CTkComboBox(f_cust_frame, values=["Tümü"], font=Fontlar.SMALL)
        self.cb_customer.pack(fill="x")
        
        # D: İşlem Türü
        f_op_frame = ctk.CTkFrame(self.filter_card, fg_color="transparent")
        f_op_frame.grid(row=0, column=3, padx=10, pady=15, sticky="nsew")
        self.lbl_f_op = ctk.CTkLabel(f_op_frame, text="İşlem / Makine Türü", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK)
        self.lbl_f_op.pack(anchor="w", pady=(0, 4))
        self.cb_operation = ctk.CTkComboBox(f_op_frame, values=["Tümü"], font=Fontlar.SMALL)
        self.cb_operation.pack(fill="x")
        
        # E: Teklif Durumu
        f_stat_frame = ctk.CTkFrame(self.filter_card, fg_color="transparent")
        f_stat_frame.grid(row=0, column=4, padx=10, pady=15, sticky="nsew")
        self.lbl_f_stat = ctk.CTkLabel(f_stat_frame, text="Teklif Durumu", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK)
        self.lbl_f_stat.pack(anchor="w", pady=(0, 4))
        self.cb_status = ctk.CTkComboBox(f_stat_frame, values=["Tümü", "Beklemede", "Onaylandı", "Reddedildi", "İptal"], font=Fontlar.SMALL)
        self.cb_status.pack(fill="x")
        self.cb_status.set("Tümü")
        
        # Butonlar Satırı (Filtre Altı)
        self.btn_panel = ctk.CTkFrame(self.filter_card, fg_color="transparent")
        self.btn_panel.grid(row=1, column=0, columnspan=5, padx=15, pady=(0, 15), sticky="e")
        
        self.btn_create = ctk.CTkButton(
            self.btn_panel, 
            text="📈 Rapor Oluştur", 
            font=Fontlar.BODY_BOLD,
            fg_color=Renkler.PRIMARY, 
            hover_color=Renkler.PRIMARY_HOVER,
            command=self.load_data,
            width=140
        )
        self.btn_create.pack(side="left", padx=5)
        
        self.btn_excel = ctk.CTkButton(
            self.btn_panel, 
            text="🟢 Excel İndir", 
            font=Fontlar.BODY_BOLD,
            fg_color="#10B981", 
            hover_color="#059669",
            command=self.download_excel,
            width=130
        )
        self.btn_excel.pack(side="left", padx=5)
        
        self.btn_pdf = ctk.CTkButton(
            self.btn_panel, 
            text="🔴 PDF İndir", 
            font=Fontlar.BODY_BOLD,
            fg_color="#EC4899", 
            hover_color="#DB2777",
            command=self.download_pdf,
            width=130
        )
        self.btn_pdf.pack(side="left", padx=5)

        # ── 3. KPI KARTLARI ───────────────────────────────────────────────────
        self.kpi_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=20, pady=5)
        self.kpi_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="kpi")
        
        self.lbl_val_tot = self.create_kpi_card(self.kpi_frame, "Toplam Teklif Tutarı", "0.00 ₺", 0)
        self.lbl_val_cost = self.create_kpi_card(self.kpi_frame, "Toplam Net Maliyet", "0.00 ₺", 1)
        self.lbl_val_profit = self.create_kpi_card(self.kpi_frame, "Toplam Brüt Kar", "0.00 ₺", 2, val_color=Renkler.SUCCESS)
        self.lbl_val_margin = self.create_kpi_card(self.kpi_frame, "Ortalama Kar Oranı", "% 0.0", 3)
        self.lbl_val_scrap = self.create_kpi_card(self.kpi_frame, "Tahmini Hurda Değeri", "0.00 ₺", 4, val_color=Renkler.WARNING)

        # ── 4. GRAFİK KARTLARI (2x2 Grid) ─────────────────────────────────────
        self.chart_grid = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.chart_grid.pack(fill="x", padx=20, pady=10)
        self.chart_grid.grid_columnconfigure((0, 1), weight=1, uniform="chart_cols")
        
        # A: Aylık Teklif Tutarı Kartı
        self.card_chart_ciro = self.create_chart_container(self.chart_grid, 0, 0, "Aylık Teklif Tutarı (Ciro)")
        self.fig_ciro = Figure(figsize=(4, 2.2), dpi=100)
        self.ax_ciro = self.fig_ciro.add_subplot(111)
        self.canvas_ciro = FigureCanvasTkAgg(self.fig_ciro, master=self.card_chart_ciro)
        self.canvas_ciro.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)
        
        # B: Aylık Kar Tutarı Kartı
        self.card_chart_kar = self.create_chart_container(self.chart_grid, 0, 1, "Aylık Kar Tutarı")
        self.fig_kar = Figure(figsize=(4, 2.2), dpi=100)
        self.ax_kar = self.fig_kar.add_subplot(111)
        self.canvas_kar = FigureCanvasTkAgg(self.fig_kar, master=self.card_chart_kar)
        self.canvas_kar.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)
        
        # C: Teklif Durum Dağılımı Kartı
        self.card_chart_status = self.create_chart_container(self.chart_grid, 1, 0, "Teklif Durum Dağılımı")
        self.fig_status = Figure(figsize=(4, 2.2), dpi=100)
        self.ax_status = self.fig_status.add_subplot(111)
        self.canvas_status = FigureCanvasTkAgg(self.fig_status, master=self.card_chart_status)
        self.canvas_status.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)
        
        # D: En Çok Kullanılan İşlemler Kartı
        self.card_chart_ops = self.create_chart_container(self.chart_grid, 1, 1, "En Çok Kullanılan İşlemler")
        self.fig_ops = Figure(figsize=(4, 2.2), dpi=100)
        self.ax_ops = self.fig_ops.add_subplot(111)
        self.canvas_ops = FigureCanvasTkAgg(self.fig_ops, master=self.card_chart_ops)
        self.canvas_ops.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)

        # ── 5. ALT RAPOR TABLOLARI (Side-by-Side 3 Kolon) ─────────────────────
        self.tables_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.tables_frame.pack(fill="x", padx=20, pady=10)
        self.tables_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="tables")
        
        # A: Müşteri Bazlı Rapor Kartı
        self.card_t_cust = self.create_table_card(self.tables_frame, 0, "Müşteri Bazlı Özet")
        self.scr_t_cust = ctk.CTkScrollableFrame(self.card_t_cust, fg_color="transparent")
        self.scr_t_cust.pack(fill="both", expand=True, padx=10, pady=5)
        
        # B: İşlem Bazlı Rapor Kartı
        self.card_t_ops = self.create_table_card(self.tables_frame, 1, "İşlem Bazlı Özet")
        self.scr_t_ops = ctk.CTkScrollableFrame(self.card_t_ops, fg_color="transparent")
        self.scr_t_ops.pack(fill="both", expand=True, padx=10, pady=5)
        
        # C: Malzeme Bazlı Rapor Kartı
        self.card_t_mat = self.create_table_card(self.tables_frame, 2, "Malzeme Bazlı Özet")
        self.scr_t_mat = ctk.CTkScrollableFrame(self.card_t_mat, fg_color="transparent")
        self.scr_t_mat.pack(fill="both", expand=True, padx=10, pady=5)

    # ── YARDIMCI KART FABRİKALARI ─────────────────────────────────────────────

    def create_kpi_card(self, parent, title, value, col, val_color=Renkler.TEXT_DARK):
        card = ctk.CTkFrame(parent, fg_color=Renkler.CARD_BG, corner_radius=10, height=85)
        card.grid(row=0, column=col, sticky="nsew", padx=5)
        card.pack_propagate(False)
        
        ctk.CTkLabel(card, text=title, font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY).pack(anchor="w", padx=15, pady=(12, 2))
        lbl_val = ctk.CTkLabel(card, text=value, font=Fontlar.H3, text_color=val_color)
        lbl_val.pack(anchor="w", padx=15)
        return lbl_val

    def create_chart_container(self, parent, row, col, title):
        card = ctk.CTkFrame(parent, fg_color=Renkler.CARD_BG, corner_radius=10, height=310)
        card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        card.pack_propagate(False)
        
        ctk.CTkLabel(card, text=title, font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_DARK).pack(anchor="w", padx=15, pady=(12, 2))
        return card

    def create_table_card(self, parent, col, title):
        card = ctk.CTkFrame(parent, fg_color=Renkler.CARD_BG, corner_radius=10, height=340)
        card.grid(row=0, column=col, sticky="nsew", padx=5)
        card.pack_propagate(False)
        
        ctk.CTkLabel(card, text=title, font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_DARK).pack(anchor="w", padx=15, pady=(12, 5))
        return card

    # ── VERİ VE FİLTRE YÜKLEME ────────────────────────────────────────────────

    def load_filters_data(self):
        """Müşteri ve İşlem combobox'larını veritabanındaki verilerle doldurur."""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Müşterileri çek
            cursor.execute("SELECT id, firma_adi FROM musteriler WHERE kullanici_id = ? ORDER BY firma_adi", (self.current_user["id"],))
            self.customer_list = cursor.fetchall()
            cust_names = ["Tümü"] + [f"{c['firma_adi']} (ID: {c['id']})" for c in self.customer_list]
            self.cb_customer.configure(values=cust_names)
            self.cb_customer.set("Tümü")
            
            # İşlemleri çek
            cursor.execute("""
                SELECT DISTINCT islem_adi 
                FROM teklif_kalemleri tk
                JOIN teklifler t ON tk.teklif_id = t.id
                WHERE t.kullanici_id = ? AND islem_adi IS NOT NULL AND islem_adi != ''
                ORDER BY islem_adi
            """, (self.current_user["id"],))
            self.operation_list = [r["islem_adi"] for r in cursor.fetchall()]
            op_names = ["Tümü"] + self.operation_list
            self.cb_operation.configure(values=op_names)
            self.cb_operation.set("Tümü")
            
            conn.close()
        except Exception as e:
            print("Filtre verisi yüklenirken hata oluştu:", e)

    def load_data(self):
        """Filtre değerlerini alarak veritabanından dinamik verileri çeker, KPI ve grafikleri besler."""
        t_bas = self.ent_start_date.get().strip()
        t_bit = self.ent_end_date.get().strip()
        cust_selection = self.cb_customer.get()
        op_selection = self.cb_operation.get()
        status_selection = self.cb_status.get()
        
        # Filtre değerlerini export için sakla
        self.report_data["filters"] = {
            "tarih_bas": t_bas or "-",
            "tarih_bit": t_bit or "-",
            "musteri": cust_selection,
            "islem": op_selection,
            "durum": status_selection
        }
        
        # Tarih doğrulaması
        for date_val, label in [(t_bas, "Başlangıç"), (t_bit, "Bitiş")]:
            if date_val:
                try:
                    datetime.strptime(date_val, "%Y-%m-%d")
                except ValueError:
                    messagebox.showwarning("Geçersiz Tarih", f"{label} tarihi YYYY-MM-DD formatında olmalıdır!")
                    return
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Dinamik Teklifler Sorgusu oluştur
            query = "SELECT t.*, m.firma_adi FROM teklifler t LEFT JOIN musteriler m ON t.musteri_id = m.id WHERE t.kullanici_id = ?"
            params = [self.current_user["id"]]
            
            if t_bas:
                query += " AND t.olusturma_tarihi >= ?"
                params.append(t_bas)
            if t_bit:
                query += " AND t.olusturma_tarihi <= ?"
                params.append(t_bit)
                
            # Müşteri Filtresi
            if cust_selection != "Tümü":
                try:
                    cust_id = int(cust_selection.split("(ID: ")[-1].replace(")", ""))
                    query += " AND t.musteri_id = ?"
                    params.append(cust_id)
                except Exception:
                    pass
                    
            # Durum Filtresi
            if status_selection != "Tümü":
                query += " AND t.durum = ?"
                params.append(status_selection)
                
            # İşlem Filtresi
            if op_selection != "Tümü":
                query += " AND t.id IN (SELECT DISTINCT teklif_id FROM teklif_kalemleri WHERE islem_adi = ?)"
                params.append(op_selection)
                
            cursor.execute(query, params)
            teklifler = [dict(row) for row in cursor.fetchall()]
            
            # ── KPI HESAPLAMALARI ─────────────────────────────────────────────
            toplam_tutar = sum(t["son_tutar"] or 0.0 for t in teklifler)
            toplam_maliyet = sum(t["net_maliyet"] or 0.0 for t in teklifler)
            toplam_kar = sum(t["kar_tutari"] or 0.0 for t in teklifler)
            ort_kar_orani = (toplam_kar / toplam_maliyet * 100) if toplam_maliyet > 0 else 0.0
            tahmini_hurda = sum(t["tahmini_hurda_degeri"] or 0.0 for t in teklifler)
            
            self.lbl_val_tot.configure(text=f"{toplam_tutar:,.2f} ₺")
            self.lbl_val_cost.configure(text=f"{toplam_maliyet:,.2f} ₺")
            self.lbl_val_profit.configure(text=f"{toplam_kar:,.2f} ₺")
            self.lbl_val_margin.configure(text=f"% {ort_kar_orani:.1f}")
            self.lbl_val_scrap.configure(text=f"{tahmini_hurda:,.2f} ₺")
            
            # Export verisi için sakla
            self.report_data["kpi"] = {
                "toplam_tutar": toplam_tutar,
                "toplam_maliyet": toplam_maliyet,
                "toplam_kar": toplam_kar,
                "ort_kar_orani": ort_kar_orani,
                "tahmini_hurda": tahmini_hurda
            }
            
            # ── GRAFİK VERİSİ HESAPLAMALARI ───────────────────────────────────
            # A & B: Aylık Ciro ve Kar
            monthly_ciro = {}
            monthly_kar = {}
            for t in teklifler:
                t_date = t["olusturma_tarihi"] or ""
                try:
                    # YYYY-MM anahtarını elde et
                    key = datetime.strptime(t_date[:10], "%Y-%m-%d").strftime("%Y-%m")
                except Exception:
                    key = "Belirsiz"
                monthly_ciro[key] = monthly_ciro.get(key, 0.0) + (t["son_tutar"] or 0.0)
                monthly_kar[key] = monthly_kar.get(key, 0.0) + (t["kar_tutari"] or 0.0)
                
            # C: Durum Dağılımı
            status_counts = {"Beklemede": 0, "Onaylandı": 0, "Reddedildi": 0, "İptal": 0}
            for t in teklifler:
                st = t["durum"] or "Beklemede"
                status_counts[st] = status_counts.get(st, 0) + 1
                
            # D: İşlemler ve Alt Raporlar
            teklif_ids = [t["id"] for t in teklifler]
            
            musteri_data = {}
            for t in teklifler:
                m_name = t["firma_adi"] or "Bilinmeyen Müşteri"
                if m_name not in musteri_data:
                    musteri_data[m_name] = {"firma_adi": m_name, "teklif_adedi": 0, "toplam_tutar": 0.0, "toplam_maliyet": 0.0, "toplam_kar": 0.0}
                musteri_data[m_name]["teklif_adedi"] += 1
                musteri_data[m_name]["toplam_tutar"] += (t["son_tutar"] or 0.0)
                musteri_data[m_name]["toplam_maliyet"] += (t["net_maliyet"] or 0.0)
                musteri_data[m_name]["toplam_kar"] += (t["kar_tutari"] or 0.0)
                
            self.report_data["musteri_raporu"] = sorted(musteri_data.values(), key=lambda x: x["toplam_tutar"], reverse=True)
            self.render_customer_table()
            
            # Kalem detay sorguları
            islem_list = []
            malzeme_list = []
            
            if teklif_ids:
                # ── TABLO 2: İşlem Bazlı ──────────────────────────────────────
                placeholders = ",".join("?" for _ in teklif_ids)
                cursor.execute(f"""
                    SELECT islem_adi, COUNT(*) as kullanim_sayisi, SUM(makine_suresi) as toplam_sure, SUM(makine_maliyeti) as toplam_maliyet
                    FROM teklif_kalemleri
                    WHERE teklif_id IN ({placeholders}) AND islem_adi IS NOT NULL AND islem_adi != ''
                    GROUP BY islem_adi
                    ORDER BY kullanim_sayisi DESC
                """, teklif_ids)
                islem_list = [dict(row) for row in cursor.fetchall()]
                
                # ── TABLO 3: Malzeme Bazlı ────────────────────────────────────
                cursor.execute(f"""
                    SELECT malzeme_adi, SUM(miktar) as toplam_miktar, birim, SUM(malzeme_maliyeti) as toplam_maliyet
                    FROM teklif_kalemleri
                    WHERE teklif_id IN ({placeholders}) AND malzeme_adi IS NOT NULL AND malzeme_adi != ''
                    GROUP BY malzeme_adi, birim
                    ORDER BY toplam_miktar DESC
                """, teklif_ids)
                malzeme_list = [dict(row) for row in cursor.fetchall()]
                
            self.report_data["islem_raporu"] = islem_list
            self.report_data["malzeme_raporu"] = malzeme_list
            
            self.render_islem_table()
            self.render_malzeme_table()
            
            conn.close()
            
            # Grafikleri Çiz
            self.draw_charts(monthly_ciro, monthly_kar, status_counts, islem_list[:5])
            
        except Exception as e:
            print("Rapor verisi yüklenirken hata oluştu:", e)
            import traceback
            traceback.print_exc()

    # ── TABLO RENDER METODLARI ────────────────────────────────────────────────

    def render_customer_table(self):
        for w in self.scr_t_cust.winfo_children(): w.destroy()
        # Header Row
        h_frame = ctk.CTkFrame(self.scr_t_cust, fg_color="transparent")
        h_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(h_frame, text="Müşteri Firma", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_GRAY, anchor="w").pack(side="left")
        ctk.CTkLabel(h_frame, text="Tutar / Kar", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_GRAY, anchor="e").pack(side="right")
        ctk.CTkFrame(self.scr_t_cust, fg_color=Renkler.BORDER, height=1).pack(fill="x", pady=2)
        
        if not self.report_data["musteri_raporu"]:
            ctk.CTkLabel(self.scr_t_cust, text="Veri bulunamadı.", font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY).pack(pady=10)
            return
            
        for row in self.report_data["musteri_raporu"]:
            fr = ctk.CTkFrame(self.scr_t_cust, fg_color="transparent")
            fr.pack(fill="x", pady=3)
            
            name = row["firma_adi"]
            if len(name) > 18:
                name = name[:16] + ".."
                
            ctk.CTkLabel(fr, text=f"{name} ({row['teklif_adedi']} Teklif)", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK).pack(side="left")
            ctk.CTkLabel(fr, text=f"{row['toplam_tutar']:,.0f} ₺ / {row['toplam_kar']:,.0f} ₺", font=Fontlar.SMALL_BOLD, text_color=Renkler.PRIMARY).pack(side="right")
            ctk.CTkFrame(self.scr_t_cust, fg_color=Renkler.BORDER, height=1).pack(fill="x", pady=1)

    def render_islem_table(self):
        for w in self.scr_t_ops.winfo_children(): w.destroy()
        h_frame = ctk.CTkFrame(self.scr_t_ops, fg_color="transparent")
        h_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(h_frame, text="İşlem / Makine", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_GRAY, anchor="w").pack(side="left")
        ctk.CTkLabel(h_frame, text="Adet / Süre / Maliyet", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_GRAY, anchor="e").pack(side="right")
        ctk.CTkFrame(self.scr_t_ops, fg_color=Renkler.BORDER, height=1).pack(fill="x", pady=2)
        
        if not self.report_data["islem_raporu"]:
            ctk.CTkLabel(self.scr_t_ops, text="Veri bulunamadı.", font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY).pack(pady=10)
            return
            
        for row in self.report_data["islem_raporu"]:
            fr = ctk.CTkFrame(self.scr_t_ops, fg_color="transparent")
            fr.pack(fill="x", pady=3)
            
            name = row["islem_adi"]
            if len(name) > 16:
                name = name[:14] + ".."
                
            ctk.CTkLabel(fr, text=name, font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK).pack(side="left")
            ctk.CTkLabel(fr, text=f"{row['kullanim_sayisi']} ad / {row['toplam_sure']:.1f} sa / {row['toplam_maliyet']:,.0f} ₺", font=Fontlar.SMALL_BOLD, text_color=Renkler.PRIMARY).pack(side="right")
            ctk.CTkFrame(self.scr_t_ops, fg_color=Renkler.BORDER, height=1).pack(fill="x", pady=1)

    def render_malzeme_table(self):
        for w in self.scr_t_mat.winfo_children(): w.destroy()
        h_frame = ctk.CTkFrame(self.scr_t_mat, fg_color="transparent")
        h_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(h_frame, text="Malzeme", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_GRAY, anchor="w").pack(side="left")
        ctk.CTkLabel(h_frame, text="Miktar / Maliyet", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_GRAY, anchor="e").pack(side="right")
        ctk.CTkFrame(self.scr_t_mat, fg_color=Renkler.BORDER, height=1).pack(fill="x", pady=2)
        
        if not self.report_data["malzeme_raporu"]:
            ctk.CTkLabel(self.scr_t_mat, text="Veri bulunamadı.", font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY).pack(pady=10)
            return
            
        for row in self.report_data["malzeme_raporu"]:
            fr = ctk.CTkFrame(self.scr_t_mat, fg_color="transparent")
            fr.pack(fill="x", pady=3)
            
            name = row["malzeme_adi"]
            if len(name) > 18:
                name = name[:16] + ".."
                
            ctk.CTkLabel(fr, text=name, font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK).pack(side="left")
            ctk.CTkLabel(fr, text=f"{row['toplam_miktar']:.1f} {row['birim']} / {row['toplam_maliyet']:,.0f} ₺", font=Fontlar.SMALL_BOLD, text_color=Renkler.PRIMARY).pack(side="right")
            ctk.CTkFrame(self.scr_t_mat, fg_color=Renkler.BORDER, height=1).pack(fill="x", pady=1)

    # ── GRAFİK ÇİZİM METODLARI ────────────────────────────────────────────────

    def draw_charts(self, ciro_data, kar_data, status_counts, top_ops):
        # Tema moduna göre grafik renklerini seç
        is_dark = ctk.get_appearance_mode() == "Dark"
        bg_color = "#1E293B" if is_dark else "white"
        text_color = "white" if is_dark else "#1E293B"
        grid_color = "#475569" if is_dark else "#E2E8F0"
        
        # 1. Ciro Bar Grafiği
        self.ax_ciro.clear()
        self.fig_ciro.set_facecolor(bg_color)
        self.ax_ciro.set_facecolor(bg_color)
        
        months = sorted(ciro_data.keys())[-6:] # Son 6 ay
        ciros = [ciro_data[m] for m in months]
        
        if not months:
            months = ["Veri Yok"]
            ciros = [0]
            
        self.ax_ciro.bar(months, ciros, color="#3B82F6", width=0.4, label="Ciro")
        self.ax_ciro.spines["top"].set_visible(False)
        self.ax_ciro.spines["right"].set_visible(False)
        self.ax_ciro.spines["left"].set_color(grid_color)
        self.ax_ciro.spines["bottom"].set_color(grid_color)
        self.ax_ciro.tick_params(colors=text_color, labelsize=7)
        self.ax_ciro.grid(axis="y", linestyle="--", alpha=0.3, color=grid_color)
        self.ax_ciro.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: f"{int(x/1000)}k" if x >= 1000 else f"{int(x)}"))
        self.fig_ciro.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.2)
        self.canvas_ciro.draw()
        
        # 2. Kar Line Grafiği
        self.ax_kar.clear()
        self.fig_kar.set_facecolor(bg_color)
        self.ax_kar.set_facecolor(bg_color)
        
        kar_months = sorted(kar_data.keys())[-6:]
        kars = [kar_data[m] for m in kar_months]
        
        if not kar_months:
            kar_months = ["Veri Yok"]
            kars = [0]
            
        self.ax_kar.plot(kar_months, kars, color="#10B981", marker="o", markersize=4, linewidth=1.5)
        self.ax_kar.fill_between(kar_months, kars, color="#10B981", alpha=0.1)
        self.ax_kar.spines["top"].set_visible(False)
        self.ax_kar.spines["right"].set_visible(False)
        self.ax_kar.spines["left"].set_color(grid_color)
        self.ax_kar.spines["bottom"].set_color(grid_color)
        self.ax_kar.tick_params(colors=text_color, labelsize=7)
        self.ax_kar.grid(axis="y", linestyle="--", alpha=0.3, color=grid_color)
        self.ax_kar.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: f"{int(x/1000)}k" if x >= 1000 else f"{int(x)}"))
        self.fig_kar.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.2)
        self.canvas_kar.draw()
        
        # 3. Durum Donut Grafiği
        self.ax_status.clear()
        self.fig_status.set_facecolor(bg_color)
        self.ax_status.set_facecolor(bg_color)
        
        labels, sizes, colors_list = [], [], []
        status_colors = {"Beklemede": "#F59E0B", "Onaylandı": "#10B981", "Reddedildi": "#EF4444", "İptal": "#64748B"}
        
        for k, v in status_counts.items():
            if v > 0:
                labels.append(k)
                sizes.append(v)
                colors_list.append(status_colors.get(k, "#9CA3AF"))
                
        if not sizes:
            labels = ["Veri Yok"]
            sizes = [1]
            colors_list = ["#E2E8F0"]
            
        wedges, texts = self.ax_status.pie(
            sizes,
            labels=labels,
            colors=colors_list,
            wedgeprops=dict(width=0.4, edgecolor=bg_color, linewidth=1.5),
            startangle=90,
            textprops=dict(color=text_color, fontsize=8)
        )
        self.fig_status.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self.canvas_status.draw()
        
        # 4. En Çok Kullanılan İşlemler (Yatay Bar)
        self.ax_ops.clear()
        self.fig_ops.set_facecolor(bg_color)
        self.ax_ops.set_facecolor(bg_color)
        
        if top_ops:
            op_names = [row["islem_adi"][:12] + ".." if len(row["islem_adi"]) > 12 else row["islem_adi"] for row in top_ops]
            op_counts = [row["kullanim_sayisi"] for row in top_ops]
            # Yatay grafik için ters çevir
            op_names.reverse()
            op_counts.reverse()
        else:
            op_names = ["Veri Yok"]
            op_counts = [0]
            
        self.ax_ops.barh(op_names, op_counts, color="#EC4899", height=0.4)
        self.ax_ops.spines["top"].set_visible(False)
        self.ax_ops.spines["right"].set_visible(False)
        self.ax_ops.spines["left"].set_color(grid_color)
        self.ax_ops.spines["bottom"].set_color(grid_color)
        self.ax_ops.tick_params(colors=text_color, labelsize=7)
        self.ax_ops.grid(axis="x", linestyle="--", alpha=0.3, color=grid_color)
        self.fig_ops.subplots_adjust(left=0.25, right=0.95, top=0.9, bottom=0.2)
        self.canvas_ops.draw()

    # ── DIŞA AKTARIM AKSİYONLARI ──────────────────────────────────────────────

    def download_excel(self):
        if not self.report_data.get("kpi"):
            messagebox.showwarning("Boş Rapor", "Lütfen önce Rapor Oluştur butonuna basarak verileri yükleyin!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Dosyası", "*.xlsx")],
            initialfile=f"analiz_raporu_{datetime.now().strftime('%Y%m%d')}.xlsx",
            title="Raporu Excel Olarak Kaydet"
        )
        
        if filename:
            try:
                export_rapor_to_excel(self.report_data, filename)
                messagebox.showinfo("Başarılı", f"Excel raporu başarıyla kaydedildi:\n{filename}")
            except Exception as e:
                messagebox.showerror("Hata", f"Excel oluşturulurken bir hata meydana geldi:\n{e}")

    def download_pdf(self):
        if not self.report_data.get("kpi"):
            messagebox.showwarning("Boş Rapor", "Lütfen önce Rapor Oluştur butonuna basarak verileri yükleyin!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Dosyası", "*.pdf")],
            initialfile=f"analiz_raporu_{datetime.now().strftime('%Y%m%d')}.pdf",
            title="Raporu PDF Olarak Kaydet"
        )
        
        if filename:
            try:
                export_rapor_to_pdf(self.report_data, filename)
                messagebox.showinfo("Başarılı", f"PDF raporu başarıyla kaydedildi:\n{filename}")
            except Exception as e:
                messagebox.showerror("Hata", f"PDF oluşturulurken bir hata meydana geldi:\n{e}")

    def apply_theme(self):
        """Tema değişimlerinde tüm UI kartlarını ve grafiklerini günceller."""
        self.configure(fg_color=Renkler.BG_LIGHT)
        
        try:
            self.filter_card.configure(fg_color=Renkler.CARD_BG)
            self.lbl_title.configure(text_color=Renkler.TEXT_DARK)
            self.lbl_subtitle.configure(text_color=Renkler.TEXT_GRAY)
            
            # Filtre label'ları
            self.lbl_f_start.configure(text_color=Renkler.TEXT_DARK)
            self.lbl_f_end.configure(text_color=Renkler.TEXT_DARK)
            self.lbl_f_cust.configure(text_color=Renkler.TEXT_DARK)
            self.lbl_f_op.configure(text_color=Renkler.TEXT_DARK)
            self.lbl_f_stat.configure(text_color=Renkler.TEXT_DARK)
            
            # KPI Kartları Yenileme (Parent frame renk güncellemeleri)
            for widget in self.kpi_frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    widget.configure(fg_color=Renkler.CARD_BG)
                    for child in widget.winfo_children():
                        if isinstance(child, ctk.CTkLabel):
                            # Başlık label'ları gri, değerler dark olmalı
                            if child.cget("font") == Fontlar.SMALL:
                                child.configure(text_color=Renkler.TEXT_GRAY)
                            elif child.cget("text_color") not in [Renkler.SUCCESS, Renkler.WARNING]:
                                child.configure(text_color=Renkler.TEXT_DARK)
                                
            # Grafik Kartları
            for widget in self.chart_grid.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    widget.configure(fg_color=Renkler.CARD_BG)
                    for child in widget.winfo_children():
                        if isinstance(child, ctk.CTkLabel):
                            child.configure(text_color=Renkler.TEXT_DARK)
                            
            # Tablo Kartları
            for widget in self.tables_frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    widget.configure(fg_color=Renkler.CARD_BG)
                    for child in widget.winfo_children():
                        if isinstance(child, ctk.CTkLabel):
                            child.configure(text_color=Renkler.TEXT_DARK)
                            
        except Exception:
            pass
            
        # Grafikleri yeni tema renkleriyle çiz
        self._needs_refresh = True
        is_active = (hasattr(self.master, "master") and getattr(self.master.master, "current_screen", None) == self)
        if is_active:
            self.load_data()
