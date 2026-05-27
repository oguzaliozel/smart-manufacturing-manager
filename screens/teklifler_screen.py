import customtkinter as ctk
from tema import Renkler, Fontlar
import database
from tkinter import messagebox
import tkinter as tk

def hesapla_kalan_sure(teslim_tarihi_str):
    if not teslim_tarihi_str:
        return "Belirtilmedi"
    try:
        from datetime import datetime
        teslim_tarihi = datetime.strptime(teslim_tarihi_str, "%Y-%m-%d").date()
        bugun = datetime.now().date()
        fark = (teslim_tarihi - bugun).days
        if fark > 0:
            return f"{fark} gün kaldı"
        elif fark == 0:
            return "Bugün teslimat günü!"
        else:
            return f"{-fark} gün gecikti"
    except Exception:
        return "Geçersiz Tarih"

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.delay = 300  # ms
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

class TekliflerScreen(ctk.CTkFrame):
    def __init__(self, master, current_user):
        super().__init__(master, fg_color=Renkler.BG_LIGHT)
        self.current_user = current_user
        self.db = database.Database()
        self._needs_refresh = False
        
        # Grid kolon oranları (Kullanıcı talebine göre)
        self.col_weights = {
            0: 150, # Teklif No
            1: 220, # Müşteri
            2: 130, # Durum
            3: 150, # Net Maliyet
            4: 140, # Kar Tutarı
            5: 160, # Toplam Tutar
            6: 120, # Tarih
            7: 190  # İşlemler
        }
        
        # Güvenli minimum genişlikler (Pencere küçüldüğünde taşmayı önlemek için)
        self.col_minsizes = {
            0: 100,
            1: 150,
            2: 90,
            3: 100,
            4: 90,
            5: 110,
            6: 80,
            7: 130
        }
        
        # Kolon hizalama ve padding kuralları: (Hizalama, padx)
        self.column_configs = [
            ("w", (15, 5)), # Teklif No (Sola hizalı)
            ("w", (5, 5)),  # Müşteri (Sola hizalı)
            ("", (5, 5)),   # Durum (Ortalı)
            ("e", (5, 15)), # Net Maliyet (Sağa hizalı)
            ("e", (5, 15)), # Kar Tutarı (Sağa hizalı)
            ("e", (5, 15)), # Toplam Tutar (Sağa hizalı)
            ("", (5, 5)),   # Tarih (Ortalı)
            ("", (5, 5))    # İşlemler (Ortalı)
        ]
        
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        # ── ÜST BAŞLIK ALANI ──────────────────────────────────────────────────
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(30, 15))
        
        self.lbl_title = ctk.CTkLabel(self.header_frame, text="Teklifler", font=Fontlar.H1, text_color=Renkler.TEXT_DARK)
        self.lbl_title.pack(side="left")
        
        self.btn_yeni = ctk.CTkButton(
            self.header_frame, 
            text="+ Yeni Teklif", 
            font=Fontlar.BODY_BOLD,
            fg_color=Renkler.PRIMARY,
            hover_color=Renkler.PRIMARY_HOVER,
            command=self.yeni_teklif_ac
        )
        self.btn_yeni.pack(side="right")

        # ── TABLO ANA KARTI ───────────────────────────────────────────────────
        self.table_frame = ctk.CTkFrame(self, fg_color=Renkler.CARD_BG, corner_radius=10)
        self.table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # Tablo Başlıkları
        # Dikey scrollbar alanını (16px) dengelemek için sağ padding 31px yapıldı
        self.table_header = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        self.table_header.pack(fill="x", padx=(15, 31), pady=12)
        
        headers = [
            "Teklif No",
            "Müşteri",
            "Durum",
            "Net Maliyet",
            "Kar Tutarı",
            "Toplam Tutar",
            "Tarih",
            "İşlemler"
        ]
        
        for i, text in enumerate(headers):
            align, padx = self.column_configs[i]
            lbl = ctk.CTkLabel(self.table_header, text=text, font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_GRAY)
            lbl.grid(row=0, column=i, sticky=align, padx=padx)
            
            # Tüm kolonlar aynı uniform grupta orantılı ölçeklenir
            self.table_header.grid_columnconfigure(
                i, 
                weight=self.col_weights[i], 
                uniform="col", 
                minsize=self.col_minsizes[i]
            )

        # Çizgi
        ayrac = ctk.CTkFrame(self.table_frame, fg_color=Renkler.BORDER, height=1)
        ayrac.pack(fill="x", padx=20)
        
        # Liste Alanı (Scrollable)
        self.list_frame = ctk.CTkScrollableFrame(self.table_frame, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def load_data(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        conn = self.db.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.id, t.teklif_no, m.firma_adi, t.durum, t.net_maliyet, t.kar_tutari, t.son_tutar, t.olusturma_tarihi, t.teslim_tarihi 
            FROM teklifler t
            LEFT JOIN musteriler m ON t.musteri_id = m.id
            WHERE t.kullanici_id = ?
            ORDER BY t.id DESC
        ''', (self.current_user["id"],))
        
        teklifler = cursor.fetchall()
        conn.close()
        
        if not teklifler:
            ctk.CTkLabel(self.list_frame, text="Kayıtlı teklif bulunamadı.", font=Fontlar.BODY, text_color=Renkler.TEXT_GRAY).pack(pady=40)
            return
            
        for t_satir in teklifler:
            t_id = t_satir['id']
            t_no = t_satir['teklif_no'] or "-"
            musteri = t_satir['firma_adi'] or "-"
            durum = t_satir['durum'] or "Beklemede"
            maliyet = f"{t_satir['net_maliyet'] or 0.0:,.2f} ₺"
            kar = f"{t_satir['kar_tutari'] or 0.0:,.2f} ₺"
            tutar = f"{t_satir['son_tutar'] or 0.0:,.2f} ₺"
            tarih = t_satir['olusturma_tarihi'] or "-"
            
            # Satır Çerçevesi (Sabit 64px yükseklik)
            row = ctk.CTkFrame(self.list_frame, fg_color="white", corner_radius=6, height=64)
            row.pack(fill="x", pady=3, padx=5)
            row.grid_propagate(False)
            row.pack_propagate(False)
            row.grid_rowconfigure(0, weight=1)
            
            # Grid ağırlıklarını ve uniform gruplarını satıra da ata
            for col_idx, weight in self.col_weights.items():
                row.grid_columnconfigure(
                    col_idx, 
                    weight=weight, 
                    uniform="col", 
                    minsize=self.col_minsizes[col_idx]
                )
                
            # Hover efekti bind helper
            def make_hover_effect(widget_item, row_frame=row):
                widget_item.bind("<Enter>", lambda e: row_frame.configure(fg_color="#F1F5F9"))
                widget_item.bind("<Leave>", lambda e: row_frame.configure(fg_color="white"))
                
            row.bind("<Enter>", lambda e, r=row: r.configure(fg_color="#F1F5F9"))
            row.bind("<Leave>", lambda e, r=row: r.configure(fg_color="white"))

            # Uzun müşteri isimlerini kırp
            if len(musteri) > 22:
                musteri = musteri[:19] + "..."

            # 0. Teklif No
            lbl_no = ctk.CTkLabel(row, text=t_no, font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK)
            lbl_no.grid(row=0, column=0, sticky=self.column_configs[0][0], padx=self.column_configs[0][1])
            make_hover_effect(lbl_no)
            
            # 1. Müşteri
            lbl_cust = ctk.CTkLabel(row, text=musteri, font=Fontlar.SMALL, text_color=Renkler.TEXT_DARK)
            lbl_cust.grid(row=0, column=1, sticky=self.column_configs[1][0], padx=self.column_configs[1][1])
            make_hover_effect(lbl_cust)
            
            # 2. Durum (Badge / Rozet)
            badge = self.create_status_badge(row, durum)
            badge.grid(row=0, column=2, sticky=self.column_configs[2][0], padx=self.column_configs[2][1])
            make_hover_effect(badge)
            for child in badge.winfo_children():
                make_hover_effect(child)
            
            # 3. Net Maliyet
            lbl_mal = ctk.CTkLabel(row, text=maliyet, font=Fontlar.SMALL, text_color=Renkler.TEXT_DARK)
            lbl_mal.grid(row=0, column=3, sticky=self.column_configs[3][0], padx=self.column_configs[3][1])
            make_hover_effect(lbl_mal)
            
            # 4. Kar Tutarı
            lbl_kar = ctk.CTkLabel(row, text=kar, font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY)
            lbl_kar.grid(row=0, column=4, sticky=self.column_configs[4][0], padx=self.column_configs[4][1])
            make_hover_effect(lbl_kar)
            
            # 5. Toplam Tutar
            lbl_tot = ctk.CTkLabel(row, text=tutar, font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color=Renkler.PRIMARY)
            lbl_tot.grid(row=0, column=5, sticky=self.column_configs[5][0], padx=self.column_configs[5][1])
            make_hover_effect(lbl_tot)
            
            # 6. Tarih (Tek satır, detaylar tooltip'te)
            lbl_date = ctk.CTkLabel(row, text=tarih, font=Fontlar.SMALL, text_color=Renkler.TEXT_DARK)
            lbl_date.grid(row=0, column=6, sticky=self.column_configs[6][0], padx=self.column_configs[6][1])
            make_hover_effect(lbl_date)
            
            tooltip_text = f"Oluşturma Tarihi: {tarih}"
            if t_satir['teslim_tarihi']:
                kalan = hesapla_kalan_sure(t_satir['teslim_tarihi'])
                tooltip_text += f"\nTeslimat Tarihi: {t_satir['teslim_tarihi']} ({kalan})"
            ToolTip(lbl_date, tooltip_text)
            
            # 7. İşlemler Alanı (Kompakt ikon butonları)
            actions_frame = ctk.CTkFrame(row, fg_color="transparent")
            actions_frame.grid(row=0, column=7, sticky=self.column_configs[7][0], padx=self.column_configs[7][1])
            make_hover_effect(actions_frame)
            
            self.build_action_buttons(actions_frame, t_id, durum)

    def create_status_badge(self, parent, status):
        badge_frame = ctk.CTkFrame(parent, corner_radius=12, height=22)
        if status == "Beklemede":
            bg_color = "#FEF3C7"
            text_color = "#D97706"
        elif status == "Onaylandı":
            bg_color = "#D1FAE5"
            text_color = "#059669"
        elif status == "Reddedildi":
            bg_color = "#FEE2E2"
            text_color = "#DC2626"
        else: # İptal
            bg_color = "#E5E7EB"
            text_color = "#4B5563"
            
        badge_frame.configure(fg_color=bg_color)
        lbl = ctk.CTkLabel(badge_frame, text=status, font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color=text_color)
        lbl.pack(padx=8, pady=2)
        return badge_frame

    def build_action_buttons(self, parent, t_id, status):
        # Duruma göre yüklenecek buton haritası: (İkon, Metin, Arka Plan, Hover, Yazı Rengi, Eylem, Tooltip)
        buttons = []
        if status == "Beklemede":
            buttons = [
                ("👁", "İncele", "#E2E8F0", "#CBD5E1", "#475569", lambda: self.goruntule_teklif(t_id), "Teklifi İncele"),
                ("✏", "Düzenle", "#DBEAFE", "#BFDBFE", "#2563EB", lambda: self.duzenle_teklif(t_id), "Teklifi Düzenle"),
                ("✓", "Onayla", "#D1FAE5", "#A7F3D0", "#059669", lambda: self.guncelle_durum(t_id, "Onaylandı"), "Teklifi Onayla"),
                ("✕", "Reddet", "#FEE2E2", "#FCA5A5", "#DC2626", lambda: self.guncelle_durum(t_id, "Reddedildi"), "Teklifi Reddet"),
                ("⏸", "İptal", "#F1F5F9", "#E2E8F0", "#64748B", lambda: self.guncelle_durum(t_id, "İptal"), "Teklifi İptal Et")
            ]
        elif status == "Onaylandı":
            buttons = [
                ("👁", "İncele", "#E2E8F0", "#CBD5E1", "#475569", lambda: self.goruntule_teklif(t_id), "Teklifi İncele"),
                ("📄", "PDF", "#FCE7F3", "#FBCFE8", "#DB2777", lambda: self.pdf_indir(t_id), "PDF Olarak İndir"),
                ("⏸", "İptal", "#F1F5F9", "#E2E8F0", "#64748B", lambda: self.guncelle_durum(t_id, "İptal"), "Teklifi İptal Et")
            ]
        elif status == "Reddedildi":
            buttons = [
                ("👁", "İncele", "#E2E8F0", "#CBD5E1", "#475569", lambda: self.goruntule_teklif(t_id), "Teklifi İncele"),
                ("✏", "Düzenle", "#DBEAFE", "#BFDBFE", "#2563EB", lambda: self.duzenle_teklif(t_id), "Teklifi Düzenle"),
                ("⏸", "İptal", "#F1F5F9", "#E2E8F0", "#64748B", lambda: self.guncelle_durum(t_id, "İptal"), "Teklifi İptal Et")
            ]
        else: # İptal
            buttons = [
                ("👁", "İncele", "#E2E8F0", "#CBD5E1", "#475569", lambda: self.goruntule_teklif(t_id), "Teklifi İncele")
            ]

        # Eğer 2'den fazla buton varsa sadece ikon göster
        show_only_icon = len(buttons) > 2
        
        for icon, text, bg, hover, fg, cmd, tooltip in buttons:
            if show_only_icon:
                self.create_icon_btn(
                    parent, 
                    icon, 
                    bg, 
                    hover, 
                    fg, 
                    cmd, 
                    tooltip, 
                    width=26, 
                    height=26, 
                    corner_radius=13, 
                    font=("Inter", 13)
                )
            else:
                self.create_icon_btn(
                    parent, 
                    f"{icon} {text}", 
                    bg, 
                    hover, 
                    fg, 
                    cmd, 
                    tooltip, 
                    width=85, 
                    height=26, 
                    corner_radius=13, 
                    font=("Inter", 10, "bold")
                )

    def create_icon_btn(self, parent, text, fg, hover, text_col, command, tooltip_text, **kwargs):
        btn = ctk.CTkButton(
            parent, 
            text=text, 
            fg_color=fg, 
            hover_color=hover, 
            text_color=text_col, 
            command=command,
            **kwargs
        )
        btn.pack(side="left", padx=2)
        ToolTip(btn, tooltip_text)

    # ── EYLEM FONKSİYONLARI ──────────────────────────────────────────────────

    def guncelle_durum(self, t_id, yeni_durum):
        success = self.db.teklif_durum_guncelle(t_id, yeni_durum, self.current_user["id"])
        if success:
            self.load_data()
            # Dashboard'u bir sonraki ziyarette yenile
            if hasattr(self.master.master, 'screens'):
                screens = self.master.master.screens
                if "dashboard" in screens and hasattr(screens["dashboard"], "_needs_refresh"):
                    screens["dashboard"]._needs_refresh = True
        else:
            messagebox.showerror("Hata", "Durum güncellenirken bir hata oluştu.")

    def goruntule_teklif(self, teklif_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.*, m.firma_adi, m.telefon, m.mail 
            FROM teklifler t 
            LEFT JOIN musteriler m ON t.musteri_id = m.id 
            WHERE t.id = ? AND t.kullanici_id = ?
        """, (teklif_id, self.current_user["id"]))
        teklif = cursor.fetchone()
        
        cursor.execute("SELECT * FROM teklif_kalemleri WHERE teklif_id = ?", (teklif_id,))
        kalemler = cursor.fetchall()
        conn.close()
        
        if not teklif:
            messagebox.showerror("Hata", "Teklif detayları yüklenemedi.")
            return
            
        # Modal Detay Penceresi (CTkToplevel)
        detay_win = ctk.CTkToplevel(self)
        detay_win.title(f"Teklif Detayı - {teklif['teklif_no']}")
        detay_win.geometry("520x650")
        detay_win.resizable(False, False)
        detay_win.configure(fg_color=Renkler.BG_LIGHT)
        
        # Modal modu (Ana pencereyi kitler)
        detay_win.grab_set()
        
        # Başlık Bölümü
        header = ctk.CTkFrame(detay_win, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(25, 10))
        ctk.CTkLabel(header, text=f"Teklif No: {teklif['teklif_no']}", font=Fontlar.H2, text_color=Renkler.TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(header, text=f"Başlık: {teklif['baslik']}", font=Fontlar.BODY_BOLD, text_color=Renkler.PRIMARY).pack(anchor="w", pady=(2, 0))
        
        # Ana Kart Alanı (Scrollable)
        card = ctk.CTkScrollableFrame(detay_win, fg_color=Renkler.CARD_BG, corner_radius=10)
        card.pack(fill="both", expand=True, padx=25, pady=(5, 15))
        
        def ekle_bilgi(parent, label, value, bold=False, text_col=Renkler.TEXT_DARK):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(fill="x", padx=10, pady=4)
            ctk.CTkLabel(f, text=label, font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_GRAY).pack(side="left")
            ctk.CTkLabel(f, text=value, font=Fontlar.SMALL_BOLD if bold else Fontlar.SMALL, text_color=text_col).pack(side="right")
            
        # Müşteri Bilgileri
        ekle_bilgi(card, "Müşteri Firma:", teklif["firma_adi"])
        ekle_bilgi(card, "Durum:", teklif["durum"], bold=True, text_col=Renkler.PRIMARY)
        ekle_bilgi(card, "Oluşturma Tarihi:", teklif["olusturma_tarihi"])
        if teklif["teslim_tarihi"]:
            kalan = hesapla_kalan_sure(teklif["teslim_tarihi"])
            ekle_bilgi(card, "Teslimat Tarihi:", f"{teklif['teslim_tarihi']} ({kalan})", bold=True, text_col=Renkler.WARNING)
        
        # Bölücü
        ctk.CTkFrame(card, fg_color=Renkler.BORDER, height=1).pack(fill="x", padx=10, pady=10)
        
        # Kalem Detayları
        ctk.CTkLabel(card, text="Teklif Kalemleri", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_GRAY).pack(anchor="w", padx=10, pady=(0, 5))
        for k in kalemler:
            ekle_bilgi(card, "  Malzeme Adı:", f"{k['malzeme_adi']} ({k['miktar']:.1f} {k['birim']})")
            ekle_bilgi(card, "  İşlem / Makine:", f"{k['islem_adi']} ({k['makine_suresi']:.1f} Saat)")
            ekle_bilgi(card, "  Varsayılan Fire:", f"% {k['fire_orani']}")
            if k["tahmini_hurda_degeri"]:
                ekle_bilgi(card, "  Tahmini Hurda Geliri:", f"{k['tahmini_hurda_degeri']:.2f} ₺", text_col=Renkler.WARNING)
                
        # Bölücü
        ctk.CTkFrame(card, fg_color=Renkler.BORDER, height=1).pack(fill="x", padx=10, pady=10)
        
        # Maliyet Özeti
        ekle_bilgi(card, "Malzeme Maliyeti:", f"{teklif['malzeme_maliyeti'] or 0.0:.2f} ₺")
        ekle_bilgi(card, "Makine Maliyeti:", f"{teklif['makine_maliyeti'] or 0.0:.2f} ₺")
        ekle_bilgi(card, "Ek Giderler:", f"{teklif['ek_gider'] or 0.0:.2f} ₺")
        ekle_bilgi(card, "Net Maliyet:", f"{teklif['net_maliyet'] or 0.0:.2f} ₺", bold=True)
        ekle_bilgi(card, "Kar Tutarı:", f"{teklif['kar_tutari'] or 0.0:.2f} ₺")
        ekle_bilgi(card, "Manuel İndirim:", f"- {teklif['manuel_indirim'] or 0.0:.2f} ₺", text_col=Renkler.ERROR)
        
        # Bölücü
        ctk.CTkFrame(card, fg_color=Renkler.BORDER, height=1).pack(fill="x", padx=10, pady=10)
        
        ekle_bilgi(card, "Son Teklif Tutarı:", f"{teklif['son_tutar'] or 0.0:.2f} ₺", bold=True, text_col=Renkler.PRIMARY)
        ekle_bilgi(card, "Tahmini Hurda Değeri:", f"{teklif['tahmini_hurda_degeri'] or 0.0:.2f} ₺", text_col=Renkler.WARNING)

        # Kapat Butonu
        ctk.CTkButton(detay_win, text="Pencereyi Kapat", font=Fontlar.BODY_BOLD, fg_color=Renkler.PRIMARY, hover_color=Renkler.PRIMARY_HOVER, command=detay_win.destroy).pack(pady=15)

    def duzenle_teklif(self, teklif_id):
        # MainLayout üzerinden yeni_teklif ekranını al
        if hasattr(self.master.master, 'screens'):
            screens = self.master.master.screens
            
            # Eğer önbellekte yeni_teklif yoksa import edip oluştur
            if "yeni_teklif" not in screens:
                from screens.yeni_teklif_screen import YeniTeklifScreen
                screens["yeni_teklif"] = YeniTeklifScreen(self.master.master.content_area, self.current_user)
                
            yeni_teklif_scr = screens["yeni_teklif"]
            
            # Sayfa yönlendirmesi
            self.master.master.show_screen("yeni_teklif")
            
            # Düzenleme modunu yükle
            yeni_teklif_scr.load_teklif_for_edit(teklif_id)

    def pdf_indir(self, teklif_id):
        try:
            import os
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, m.firma_adi, m.telefon, m.mail 
                FROM teklifler t 
                LEFT JOIN musteriler m ON t.musteri_id = m.id 
                WHERE t.id = ? AND t.kullanici_id = ?
            """, (teklif_id, self.current_user["id"]))
            teklif = cursor.fetchone()
            
            cursor.execute("SELECT * FROM teklif_kalemleri WHERE teklif_id = ?", (teklif_id,))
            kalemler = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            if not teklif:
                messagebox.showerror("Hata", "Teklif detayları veritabanında bulunamadı.")
                return
                
            teklif_dict = dict(teklif)
            
            # Dosya isimleri (Türkçe karakter ve geçersiz karakter temizliği ile)
            teklif_no_clean = teklif_dict["teklif_no"].replace("/", "-").replace("\\", "-")
            pdf_filename = f"outputs/pdf/teklif_{teklif_no_clean}.pdf"
            excel_filename = f"outputs/excel/teklif_{teklif_no_clean}.xlsx"
            
            from outputs.exporter import export_to_pdf, export_to_excel
            
            export_to_pdf(teklif_dict, kalemler, pdf_filename)
            export_to_excel(teklif_dict, kalemler, excel_filename)
            
            messagebox.showinfo(
                "Çıktı Başarılı", 
                f"Teklif dökümleri başarıyla oluşturuldu!\n\n"
                f"PDF: {pdf_filename}\n"
                f"Excel: {excel_filename}"
            )
        except Exception as e:
            messagebox.showerror("Hata", f"Dökümler oluşturulurken bir hata oluştu:\n{e}")

    def yeni_teklif_ac(self):
        if hasattr(self.master.master, 'screens'):
            screens = self.master.master.screens
            if "yeni_teklif" in screens:
                screens["yeni_teklif"].reset_form()
        
        if hasattr(self.master.master, 'show_screen'):
            self.master.master.show_screen("yeni_teklif")

    def apply_theme(self):
        """Tema değişiminde ana renkleri günceller."""
        self.configure(fg_color=Renkler.BG_LIGHT)
        try:
            self.table_frame.configure(fg_color=Renkler.CARD_BG)
            self.lbl_title.configure(text_color=Renkler.TEXT_DARK)
            self.btn_yeni.configure(fg_color=Renkler.PRIMARY, hover_color=Renkler.PRIMARY_HOVER)
        except Exception:
            pass
        # Veri güncellemesi için bir sonraki görünümde reload yap
        self._needs_refresh = True