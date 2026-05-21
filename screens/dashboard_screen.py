import customtkinter as ctk
from tema import Renkler, Fontlar
import database
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master, current_user):
        super().__init__(master, fg_color=Renkler.BG_LIGHT)
        self.current_user = current_user
        self.db = database.Database()

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Tüm sayfa içeriğini kaydırılabilir yapıyoruz (SaaS esnekliği için)
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        # ── BAŞLIK ALANI ──────────────────────────────────────────────────────
        self.header_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=25, pady=(15, 10))
        
        ctk.CTkLabel(
            self.header_frame, 
            text="Panel Özeti", 
            font=Fontlar.H1, 
            text_color=Renkler.TEXT_DARK
        ).pack(side="left")

        # ── 1. SATIR: 5'Lİ ÜST KPI KARTLARI ───────────────────────────────────
        self.kpi_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.kpi_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="kpi")
        
        self.card_bekleyen = self.create_kpi_card(self.kpi_frame, "Bekleyen Teklifler", "0", 0)
        self.card_onaylanan = self.create_kpi_card(self.kpi_frame, "Onaylanan Teklifler", "0", 1)
        self.card_reddedilen = self.create_kpi_card(self.kpi_frame, "Reddedilen Teklifler", "0", 2)
        self.card_kar = self.create_kpi_card(self.kpi_frame, "Toplam Beklenen Kar", "0.00 ₺", 3)
        self.card_hurda = self.create_kpi_card(self.kpi_frame, "Hurda Deposu", "0.00 ₺", 4)

        # ── 2. SATIR: ORTA ANALİZ KARTLARI (Yükseklik: ~290px) ──────────────────
        self.mid_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.mid_frame.pack(fill="x", padx=20, pady=5)
        self.mid_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="mid")
        
        # Ozet Kartı
        self.card_ozet = self.create_container_card(self.mid_frame, 0, 290)
        self.build_ozet_card(self.card_ozet)
        
        # Donut Grafik Kartı
        self.card_durum = self.create_container_card(self.mid_frame, 1, 290)
        self.build_durum_card(self.card_durum)
        
        # Line Grafik Kartı
        self.card_grafik = self.create_container_card(self.mid_frame, 2, 290)
        self.build_grafik_card(self.card_grafik)
        
        # Son Teklifler Kartı
        self.card_son_teklifler = self.create_container_card(self.mid_frame, 3, 290)
        self.build_son_teklifler_card(self.card_son_teklifler)

        # ── 3. SATIR: ALT DETAY KARTLARI (Yükseklik: ~200px) ───────────────────
        self.bot_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.bot_frame.pack(fill="x", padx=20, pady=10)
        self.bot_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="bot")
        
        # En Çok Kullanılan İşlemler
        self.card_islemler = self.create_container_card(self.bot_frame, 0, 200)
        self.build_islemler_card(self.card_islemler)
        
        # Yaklaşan İşler
        self.card_yaklasan = self.create_container_card(self.bot_frame, 1, 200)
        self.build_yaklasan_card(self.card_yaklasan)
        
        # Hurda Özeti
        self.card_hurda_ozet = self.create_container_card(self.bot_frame, 2, 200)
        self.build_hurda_ozet_card(self.card_hurda_ozet)
        
        # Hızlı İşlemler
        self.card_hizli = self.create_container_card(self.bot_frame, 3, 200)
        self.build_hizli_card(self.card_hizli)

    # ── KART FABRİKALARI ─────────────────────────────────────────────────────

    def create_kpi_card(self, parent, title, value, col):
        card = ctk.CTkFrame(parent, fg_color=Renkler.CARD_BG, corner_radius=10, height=85)
        card.grid(row=0, column=col, sticky="nsew", padx=5)
        card.pack_propagate(False)
        
        ctk.CTkLabel(card, text=title, font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY).pack(anchor="w", padx=15, pady=(12, 1))
        lbl_val = ctk.CTkLabel(card, text=value, font=Fontlar.H3, text_color=Renkler.TEXT_DARK)
        lbl_val.pack(anchor="w", padx=15)
        return lbl_val

    def create_container_card(self, parent, col, height):
        card = ctk.CTkFrame(parent, fg_color=Renkler.CARD_BG, corner_radius=10, height=height)
        card.grid(row=0, column=col, sticky="nsew", padx=5)
        card.pack_propagate(False)
        return card

    # ── ORTA KART DETAYLARI (290px) ──────────────────────────────────────────

    def build_ozet_card(self, parent):
        ctk.CTkLabel(parent, text="Bu Ayın Özeti", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_DARK).pack(anchor="w", padx=15, pady=(12, 5))
        self.lbl_toplam_teklif = self.create_row(parent, "Toplam Ciro:")
        self.lbl_toplam_maliyet = self.create_row(parent, "Net Maliyet:")
        self.lbl_brut_kar = self.create_row(parent, "Tahmini Brüt Kar:", color=Renkler.SUCCESS)
        self.lbl_ortalama_kar = self.create_row(parent, "Ort. Kar Oranı:")
        self.lbl_tahmini_hurda = self.create_row(parent, "Hurda Değeri:", color=Renkler.WARNING)

    def create_row(self, parent, label_text, color=Renkler.TEXT_DARK):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(frame, text=label_text, font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY).pack(side="left")
        val_label = ctk.CTkLabel(frame, text="0.00 ₺", font=Fontlar.SMALL_BOLD, text_color=color)
        val_label.pack(side="right")
        ctk.CTkFrame(parent, fg_color=Renkler.BORDER, height=1).pack(fill="x", padx=15, pady=(2, 0))
        return val_label

    def build_durum_card(self, parent):
        ctk.CTkLabel(parent, text="Teklif Dağılımı", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_DARK).pack(anchor="w", padx=15, pady=(12, 2))
        
        layout = ctk.CTkFrame(parent, fg_color="transparent")
        layout.pack(fill="both", expand=True, padx=5, pady=2)
        
        self.pie_container = ctk.CTkFrame(layout, fg_color="transparent", width=140, height=140)
        self.pie_container.pack(side="left", padx=(10, 0), expand=True)
        self.pie_container.pack_propagate(False)
        
        self.fig_pie = Figure(figsize=(1.4, 1.4), dpi=100, facecolor="white")
        self.ax_pie = self.fig_pie.add_subplot(111)
        self.fig_pie.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
        
        self.canvas_pie = FigureCanvasTkAgg(self.fig_pie, master=self.pie_container)
        self.canvas_pie.get_tk_widget().pack(fill="both", expand=True)
        
        self.legend_panel = ctk.CTkFrame(layout, fg_color="transparent")
        self.legend_panel.pack(side="right", fill="y", padx=(5, 10), pady=10, expand=True)
        
        self.lbl_leg_onay = self.create_legend_row(self.legend_panel, "Onay", "#10B981")
        self.lbl_leg_bekle = self.create_legend_row(self.legend_panel, "Bekle", "#F59E0B")
        self.lbl_leg_red = self.create_legend_row(self.legend_panel, "Red", "#EF4444")

    def create_legend_row(self, parent, label_text, color_hex):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=3, anchor="w")
        color_box = ctk.CTkFrame(frame, fg_color=color_hex, width=8, height=8, corner_radius=4)
        color_box.pack(side="left", padx=(0, 5))
        lbl = ctk.CTkLabel(frame, text=f"{label_text}: 0", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK)
        lbl.pack(side="left")
        return lbl

    def build_grafik_card(self, parent):
        ctk.CTkLabel(parent, text="Aylık Performans", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_DARK).pack(anchor="w", padx=15, pady=(12, 2))
        self.line_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.line_container.pack(fill="both", expand=True, padx=8, pady=(0, 10))
        
        self.fig_line = Figure(figsize=(2.6, 1.5), dpi=100, facecolor="white")
        self.ax_line = self.fig_line.add_subplot(111)
        self.fig_line.subplots_adjust(left=0.15, right=0.92, top=0.92, bottom=0.22)
        
        self.canvas_line = FigureCanvasTkAgg(self.fig_line, master=self.line_container)
        self.canvas_line.get_tk_widget().pack(fill="both", expand=True)

    def build_son_teklifler_card(self, parent):
        ctk.CTkLabel(parent, text="Son Teklifler", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_DARK).pack(anchor="w", padx=15, pady=(12, 5))
        self.son_teklifler_liste = ctk.CTkFrame(parent, fg_color="transparent")
        self.son_teklifler_liste.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ── ALT KART DETAYLARI (200px) ───────────────────────────────────────────

    def build_islemler_card(self, parent):
        ctk.CTkLabel(parent, text="En Çok Kullanılan İşlemler", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_DARK).pack(anchor="w", padx=15, pady=(12, 5))
        self.list_islemler = ctk.CTkFrame(parent, fg_color="transparent")
        self.list_islemler.pack(fill="both", expand=True, padx=15, pady=(0, 10))

    def build_yaklasan_card(self, parent):
        ctk.CTkLabel(parent, text="Yaklaşan Teslimatlar", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_DARK).pack(anchor="w", padx=15, pady=(12, 5))
        self.list_yaklasan = ctk.CTkFrame(parent, fg_color="transparent")
        self.list_yaklasan.pack(fill="both", expand=True, padx=15, pady=(0, 10))

    def build_hurda_ozet_card(self, parent):
        ctk.CTkLabel(parent, text="Hurda Özeti", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_DARK).pack(anchor="w", padx=15, pady=(12, 5))
        self.lbl_toplam_hurda = self.create_row(parent, "Toplam Hurda Miktarı:")
        self.lbl_ortalama_hurda_fiyat = self.create_row(parent, "Ortalama Hurda Fiyatı:")
        self.lbl_tahmini_hurda_kazanc = self.create_row(parent, "Potansiyel Kazanç:", color=Renkler.WARNING)

    def build_hizli_card(self, parent):
        ctk.CTkLabel(parent, text="Hızlı İşlemler", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_DARK).pack(anchor="w", padx=15, pady=(12, 10))
        
        grid_frame = ctk.CTkFrame(parent, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        grid_frame.grid_columnconfigure((0, 1), weight=1, uniform="btn")
        grid_frame.grid_rowconfigure((0, 1), weight=1)
        
        self.create_hizli_btn(grid_frame, "Yeni Teklif", "yeni_teklif", 0, 0)
        self.create_hizli_btn(grid_frame, "Müşteri Ekle", "musteriler", 0, 1)
        self.create_hizli_btn(grid_frame, "Malzeme Ekle", "malzemeler", 1, 0)
        self.create_hizli_btn(grid_frame, "İşlem Tanımla", "islemler", 1, 1)

    def create_hizli_btn(self, parent, text, screen_name, row, col):
        btn = ctk.CTkButton(
            parent, 
            text=text, 
            font=Fontlar.SMALL_BOLD, 
            fg_color=Renkler.BG_LIGHT, 
            text_color=Renkler.TEXT_DARK, 
            hover_color=Renkler.BORDER,
            corner_radius=6,
            command=lambda: self.hizli_islem_tetikle(screen_name)
        )
        btn.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

    def hizli_islem_tetikle(self, screen_name):
        if hasattr(self.master.master, 'show_screen'):
            self.master.master.show_screen(screen_name)

    # ── DATA LOAD VE GRAFİKLER ──────────────────────────────────────────────

    def load_data(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        user_id = self.current_user["id"]
        
        # 1. KPI Kartları
        cursor.execute("SELECT COUNT(*) FROM teklifler WHERE kullanici_id = ? AND durum = 'Beklemede'", (user_id,))
        bekleyen = cursor.fetchone()[0]
        self.card_bekleyen.configure(text=str(bekleyen))
        
        cursor.execute("SELECT COUNT(*) FROM teklifler WHERE kullanici_id = ? AND durum = 'Onaylandı'", (user_id,))
        onaylanan = cursor.fetchone()[0]
        self.card_onaylanan.configure(text=str(onaylanan))

        cursor.execute("SELECT COUNT(*) FROM teklifler WHERE kullanici_id = ? AND durum = 'Reddedildi'", (user_id,))
        reddedilen = cursor.fetchone()[0]
        self.card_reddedilen.configure(text=str(reddedilen))
        
        cursor.execute("SELECT SUM(kar_tutari) FROM teklifler WHERE kullanici_id = ? AND durum IN ('Beklemede', 'Onaylandı')", (user_id,))
        toplam_kar = cursor.fetchone()[0] or 0.0
        self.card_kar.configure(text=f"{toplam_kar:,.2f} ₺")
        
        cursor.execute("SELECT SUM(tahmini_hurda_degeri) FROM hurda_hareketleri WHERE kullanici_id = ?", (user_id,))
        hurda = cursor.fetchone()[0] or 0.0
        self.card_hurda.configure(text=f"{hurda:,.2f} ₺")
        
        # 2. Bu Ayın Özeti
        cursor.execute("""
            SELECT SUM(son_tutar), SUM(net_maliyet), AVG(kar_orani), SUM(tahmini_hurda_degeri)
            FROM teklifler 
            WHERE kullanici_id = ? AND durum IN ('Beklemede', 'Onaylandı')
        """, (user_id,))
        stats = cursor.fetchone()
        
        toplam_tutar = stats[0] or 0.0
        toplam_maliyet = stats[1] or 0.0
        brut_kar = toplam_tutar - toplam_maliyet
        ort_kar_orani = stats[2] or 0.0
        tahmini_hurda = stats[3] or 0.0
        
        self.lbl_toplam_teklif.configure(text=f"{toplam_tutar:,.2f} ₺")
        self.lbl_toplam_maliyet.configure(text=f"{toplam_maliyet:,.2f} ₺")
        self.lbl_brut_kar.configure(text=f"{brut_kar:,.2f} ₺")
        self.lbl_ortalama_kar.configure(text=f"% {ort_kar_orani:,.1f}")
        self.lbl_tahmini_hurda.configure(text=f"{tahmini_hurda:,.2f} ₺")
        
        # 3. Son Teklifler
        for widget in self.son_teklifler_liste.winfo_children():
            widget.destroy()
            
        cursor.execute('''
            SELECT t.teklif_no, m.firma_adi, t.son_tutar, t.durum 
            FROM teklifler t
            LEFT JOIN musteriler m ON t.musteri_id = m.id
            WHERE t.kullanici_id = ? 
            ORDER BY t.id DESC LIMIT 3
        ''', (user_id,))
        son_teklifler = cursor.fetchall()
        
        if not son_teklifler:
            # Boş görünmemesi için "Yeni Teklif" butonu
            empty_lbl = ctk.CTkLabel(self.son_teklifler_liste, text="Henüz teklif yok.", font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY)
            empty_lbl.pack(pady=(15, 5))
            
            btn = ctk.CTkButton(
                self.son_teklifler_liste, 
                text="+ Teklif Oluştur", 
                font=Fontlar.SMALL_BOLD, 
                fg_color=Renkler.PRIMARY, 
                hover_color=Renkler.PRIMARY_HOVER,
                command=lambda: self.hizli_islem_tetikle("yeni_teklif")
            )
            btn.pack(pady=5)
        else:
            for t_satir in son_teklifler:
                satir = ctk.CTkFrame(self.son_teklifler_liste, fg_color="transparent")
                satir.pack(fill="x", pady=4)
                satir.grid_columnconfigure(0, weight=1)  # Teklif no & Firma
                satir.grid_columnconfigure(1, weight=0)  # Tutar
                satir.grid_columnconfigure(2, weight=0)  # Durum
                
                teklif_no_kisa = f"TEK-{t_satir['teklif_no'][-4:] if t_satir['teklif_no'] else ''}"
                firma_ad = t_satir['firma_adi'] or 'Bireysel'
                if len(firma_ad) > 12:
                    firma_ad = firma_ad[:10] + "..."
                    
                lbl_adi = ctk.CTkLabel(
                    satir, 
                    text=f"{teklif_no_kisa} | {firma_ad}", 
                    font=ctk.CTkFont(family="Inter", size=11, weight="bold"), 
                    text_color=Renkler.TEXT_DARK, 
                    anchor="w"
                )
                lbl_adi.grid(row=0, column=0, sticky="w")
                
                lbl_tutar = ctk.CTkLabel(
                    satir, 
                    text=f"{t_satir['son_tutar'] or 0:,.0f} ₺", 
                    font=ctk.CTkFont(family="Inter", size=11, weight="bold"), 
                    text_color=Renkler.PRIMARY
                )
                lbl_tutar.grid(row=0, column=1, sticky="e", padx=5)
                
                durum_r = Renkler.SUCCESS if t_satir['durum'] == "Onaylandı" else Renkler.WARNING
                if t_satir['durum'] == "Reddedildi": durum_r = Renkler.ERROR
                
                lbl_durum = ctk.CTkLabel(
                    satir, 
                    text=t_satir['durum'], 
                    font=ctk.CTkFont(family="Inter", size=10, weight="bold"), 
                    text_color=durum_r
                )
                lbl_durum.grid(row=0, column=2, sticky="e", padx=(5, 0))
                
                ctk.CTkFrame(self.son_teklifler_liste, fg_color=Renkler.BORDER, height=1).pack(fill="x", pady=1)

        # 4. Donut Verileri
        cursor.execute("SELECT durum, COUNT(*) FROM teklifler WHERE kullanici_id = ? GROUP BY durum", (user_id,))
        durumlar = dict(cursor.fetchall())
        onay_c = durumlar.get("Onaylandı", 0)
        bekle_c = durumlar.get("Beklemede", 0)
        red_c = durumlar.get("Reddedildi", 0)
        toplam_t = onay_c + bekle_c + red_c
        
        self.lbl_leg_onay.configure(text=f"Onay: {onay_c}")
        self.lbl_leg_bekle.configure(text=f"Bekle: {bekle_c}")
        self.lbl_leg_red.configure(text=f"Red: {red_c}")

        # 5. Ciro Verileri (Line)
        cursor.execute("""
            SELECT strftime('%m', olusturma_tarihi) AS ay, SUM(son_tutar)
            FROM teklifler 
            WHERE kullanici_id = ? AND strftime('%Y', olusturma_tarihi) = strftime('%Y', 'now') AND durum IN ('Beklemede', 'Onaylandı')
            GROUP BY ay ORDER BY ay
        """, (user_id,))
        ciro_data = dict(cursor.fetchall())
        
        # 6. En Çok Kullanılan İşlemler
        for w in self.list_islemler.winfo_children(): w.destroy()
        cursor.execute("""
            SELECT islem_adi, COUNT(*) as count 
            FROM teklif_kalemleri tk
            JOIN teklifler t ON tk.teklif_id = t.id
            WHERE t.kullanici_id = ?
            GROUP BY islem_adi ORDER BY count DESC LIMIT 3
        """, (user_id,))
        top_islemler = cursor.fetchall()
        
        if not top_islemler:
            ctk.CTkLabel(self.list_islemler, text="İşlem verisi bulunmuyor.", font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY).pack(pady=10)
        else:
            for islem_row in top_islemler:
                fr = ctk.CTkFrame(self.list_islemler, fg_color="transparent")
                fr.pack(fill="x", pady=2)
                ctk.CTkLabel(fr, text=islem_row["islem_adi"], font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK).pack(side="left")
                ctk.CTkLabel(fr, text=f"{islem_row['count']} Kez", font=Fontlar.SMALL_BOLD, text_color=Renkler.PRIMARY).pack(side="right")
                ctk.CTkFrame(self.list_islemler, fg_color=Renkler.BORDER, height=1).pack(fill="x", pady=1)

        # 7. Yaklaşan Teslimatlar
        for w in self.list_yaklasan.winfo_children(): w.destroy()
        cursor.execute("""
            SELECT baslik, teslim_tarihi 
            FROM teklifler 
            WHERE kullanici_id = ? AND durum = 'Onaylandı' AND teslim_tarihi IS NOT NULL AND teslim_tarihi != ''
            ORDER BY teslim_tarihi ASC LIMIT 3
        """, (user_id,))
        yaklasan_isler = cursor.fetchall()
        
        if not yaklasan_isler:
            ctk.CTkLabel(self.list_yaklasan, text="Teslimat planı bulunmuyor.", font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY).pack(pady=10)
        else:
            for is_row in yaklasan_isler:
                fr = ctk.CTkFrame(self.list_yaklasan, fg_color="transparent")
                fr.pack(fill="x", pady=2)
                ctk.CTkLabel(fr, text=is_row["baslik"], font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK).pack(side="left")
                ctk.CTkLabel(fr, text=is_row["teslim_tarihi"], font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY).pack(side="right")
                ctk.CTkFrame(self.list_yaklasan, fg_color=Renkler.BORDER, height=1).pack(fill="x", pady=1)

        # 8. Hurda Özeti Alt Bilgileri
        cursor.execute("SELECT SUM(fire_miktari), AVG(hurda_birim_fiyati) FROM hurda_hareketleri WHERE kullanici_id = ?", (user_id,))
        hurda_stats = cursor.fetchone()
        toplam_h_miktar = hurda_stats[0] or 0.0
        ort_h_fiyat = hurda_stats[1] or 0.0
        
        self.lbl_toplam_hurda.configure(text=f"{toplam_h_miktar:,.1f} Birim")
        self.lbl_ortalama_hurda_fiyat.configure(text=f"{ort_h_fiyat:,.2f} ₺")
        self.lbl_tahmini_hurda_kazanc.configure(text=f"{toplam_h_miktar * ort_h_fiyat:,.2f} ₺")

        conn.close()
        
        self.draw_donut_chart(onay_c, bekle_c, red_c, toplam_t)
        self.draw_line_chart(ciro_data)

    # ── MATPLOTLIB DRAW METODLARI ───────────────────────────────────────────

    def draw_donut_chart(self, onay, bekle, red, toplam):
        self.ax_pie.clear()
        sizes, colors = [], []
        
        if onay > 0:
            sizes.append(onay)
            colors.append("#10B981")
        if bekle > 0:
            sizes.append(bekle)
            colors.append("#F59E0B")
        if red > 0:
            sizes.append(red)
            colors.append("#EF4444")
            
        if not sizes:
            sizes = [1]
            colors = ["#E2E8F0"]
            
        self.ax_pie.pie(
            sizes, 
            colors=colors,
            wedgeprops=dict(width=0.35, edgecolor="white", linewidth=1.5),
            startangle=90
        )
        
        self.ax_pie.text(
            0, 0, 
            f"{toplam}\nTeklif", 
            ha="center", va="center", 
            fontsize=8, 
            fontweight="bold", 
            color=Renkler.TEXT_DARK
        )
        self.canvas_pie.draw()

    def draw_line_chart(self, ciro_data):
        self.ax_line.clear()
        
        aylar_ad = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
        degerler, gosterilecek_aylar = [], []
        
        aktif_ay = datetime.now().month
        for i in range(5, -1, -1):
            target_month = aktif_ay - i
            if target_month <= 0: target_month += 12
            key = f"{target_month:02d}"
            gosterilecek_aylar.append(aylar_ad[target_month - 1])
            degerler.append(ciro_data.get(key, 0.0))
            
        self.ax_line.plot(
            gosterilecek_aylar, 
            degerler, 
            color="#2563EB", 
            linewidth=1.5, 
            marker="o", 
            markersize=3
        )
        
        self.ax_line.fill_between(gosterilecek_aylar, degerler, color="#2563EB", alpha=0.1)
        
        self.ax_line.spines["top"].set_visible(False)
        self.ax_line.spines["right"].set_visible(False)
        self.ax_line.spines["left"].set_color("#E2E8F0")
        self.ax_line.spines["bottom"].set_color("#E2E8F0")
        self.ax_line.tick_params(colors=Renkler.TEXT_GRAY, labelsize=7)
        self.ax_line.grid(axis="y", linestyle="--", alpha=0.4, color="#E2E8F0")
        
        self.ax_line.yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, pos: f"{int(x/1000)}k" if x >= 1000 else f"{int(x)}")
        )
        self.canvas_line.draw()