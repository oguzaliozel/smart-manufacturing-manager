import customtkinter as ctk
from tema import Renkler, Fontlar
import database
import calendar
from datetime import datetime, date, timedelta
from tkinter import messagebox

class TakvimScreen(ctk.CTkFrame):
    def __init__(self, master, current_user):
        super().__init__(master, fg_color=Renkler.BG_LIGHT)
        self.current_user = current_user
        self.db = database.Database()
        
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.selected_date = date.today()
        
        # Seçili günün görevlerini saklamak için
        self.events_cache = {}
        
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # ── ÜST SATIR (BAŞLIK & YÖNLENDİRME) ──────────────────────────────────
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(25, 15))
        
        # Sol taraf: Başlık
        self.lbl_title = ctk.CTkLabel(
            self.header_frame, 
            text="İş Planlama ve Takvim", 
            font=Fontlar.H1, 
            text_color=Renkler.TEXT_DARK
        )
        self.lbl_title.pack(side="left")
        
        # Sağ taraf: Ay Değiştirme Butonları ve Ay Adı
        self.nav_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.nav_frame.pack(side="right", fill="y")
        
        self.btn_prev = ctk.CTkButton(
            self.nav_frame, text="◀ Önceki Ay", font=Fontlar.SMALL_BOLD, 
            fg_color=Renkler.CARD_BG, text_color=Renkler.TEXT_DARK, 
            hover_color=Renkler.BORDER, width=90, height=32, command=self.prev_month
        )
        self.btn_prev.pack(side="left", padx=5)
        
        self.lbl_month = ctk.CTkLabel(
            self.nav_frame, text="Mayıs 2026", font=Fontlar.BODY_BOLD, 
            text_color=Renkler.PRIMARY, width=120, justify="center"
        )
        self.lbl_month.pack(side="left", padx=10)
        
        self.btn_next = ctk.CTkButton(
            self.nav_frame, text="Sonraki Ay ▶", font=Fontlar.SMALL_BOLD, 
            fg_color=Renkler.CARD_BG, text_color=Renkler.TEXT_DARK, 
            hover_color=Renkler.BORDER, width=90, height=32, command=self.next_month
        )
        self.btn_next.pack(side="left", padx=5)
        
        self.btn_today = ctk.CTkButton(
            self.nav_frame, text="Bugün", font=Fontlar.SMALL_BOLD, 
            fg_color=Renkler.PRIMARY, text_color="white", 
            hover_color=Renkler.PRIMARY_HOVER, width=70, height=32, command=self.go_today
        )
        self.btn_today.pack(side="left", padx=(15, 0))

        # ── ANA İÇERİK BÖLÜMÜ ─────────────────────────────────────────────────
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=30, pady=(0, 25))
        self.content_frame.grid_columnconfigure(0, weight=1) # Takvim Grid (Sol)
        self.content_frame.grid_columnconfigure(1, weight=0) # Sabit genişlikli sağ panel
        self.content_frame.grid_rowconfigure(0, weight=1)

        # ── SOL: TAKVİM KART ALANI ───────────────────────────────────────────
        self.calendar_card = ctk.CTkFrame(self.content_frame, fg_color=Renkler.CARD_BG, corner_radius=10)
        self.calendar_card.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        # Gün isimleri başlığı (Pzt, Sal...)
        self.weekdays_frame = ctk.CTkFrame(self.calendar_card, fg_color="transparent")
        self.weekdays_frame.pack(fill="x", padx=15, pady=(15, 5))
        self.weekdays_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1, uniform="days")
        
        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        for idx, gun in enumerate(gunler):
            fg_col = Renkler.TEXT_GRAY
            if idx >= 5: fg_col = Renkler.ERROR # Hafta sonları kırmızımsı/gri olsun
            ctk.CTkLabel(
                self.weekdays_frame, text=gun, font=Fontlar.SMALL_BOLD, 
                text_color=fg_col, anchor="center"
            ).grid(row=0, column=idx, sticky="ew")
            
        # Grid Çizgisi
        ctk.CTkFrame(self.calendar_card, fg_color=Renkler.BORDER, height=1).pack(fill="x", padx=15, pady=5)

        # Gün hücrelerinin yerleştirileceği asıl alan
        self.grid_frame = ctk.CTkFrame(self.calendar_card, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self.grid_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1, uniform="days")
        self.grid_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1, uniform="weeks")

        # ── SAĞ: SEÇİLİ GÜN DETAYI VE YENİ İŞ EKLEME (Notion/SaaS Tasarım) ────
        self.right_card = ctk.CTkFrame(self.content_frame, fg_color=Renkler.CARD_BG, corner_radius=12, width=350)
        self.right_card.grid(row=0, column=1, sticky="nsew")
        self.right_card.pack_propagate(False)
        
        # A. Üst Başlık Alanı
        self.day_header_frame = ctk.CTkFrame(self.right_card, fg_color="transparent")
        self.day_header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        self.lbl_selected_day = ctk.CTkLabel(
            self.day_header_frame, text="22 Mayıs 2026", font=ctk.CTkFont(family="Inter", size=18, weight="bold"), 
            text_color=Renkler.PRIMARY, anchor="w"
        )
        self.lbl_selected_day.pack(fill="x")
        
        self.lbl_selected_weekday = ctk.CTkLabel(
            self.day_header_frame, text="Cuma", font=ctk.CTkFont(family="Inter", size=12, weight="normal"), 
            text_color=Renkler.TEXT_GRAY, anchor="w"
        )
        self.lbl_selected_weekday.pack(fill="x")
        
        ctk.CTkFrame(self.day_header_frame, fg_color=Renkler.BORDER, height=1).pack(fill="x", pady=(10, 5))
        
        # B. Hızlı Görev Ekleme Alanı (Sticky Footer - Alt Panel)
        self.task_form_frame = ctk.CTkFrame(self.right_card, fg_color=Renkler.BG_LIGHT, corner_radius=10)
        self.task_form_frame.pack(side="bottom", fill="x", padx=15, pady=(10, 15))
        
        ctk.CTkLabel(
            self.task_form_frame, text="Hızlı Görev Ekle", 
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"), 
            text_color=Renkler.TEXT_DARK
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.entry_task_title = ctk.CTkEntry(
            self.task_form_frame, placeholder_text="Görev Başlığı...", 
            font=Fontlar.SMALL, height=28, fg_color="white", border_width=1, border_color="#E2E8F0"
        )
        self.entry_task_title.pack(fill="x", padx=15, pady=3)
        
        self.entry_task_desc = ctk.CTkEntry(
            self.task_form_frame, placeholder_text="Açıklama...", 
            font=Fontlar.SMALL, height=28, fg_color="white", border_width=1, border_color="#E2E8F0"
        )
        self.entry_task_desc.pack(fill="x", padx=15, pady=3)
        
        # Saat ve Renk Seçici Yatay Alanı
        options_row = ctk.CTkFrame(self.task_form_frame, fg_color="transparent")
        options_row.pack(fill="x", padx=15, pady=5)
        
        # Saat Dropdown
        self.combo_task_time = ctk.CTkComboBox(
            options_row, 
            values=["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"],
            font=Fontlar.SMALL, width=80, height=26, dropdown_font=Fontlar.SMALL
        )
        self.combo_task_time.set("12:00")
        self.combo_task_time.pack(side="left")
        
        # Renk Butonları Kabı
        colors_frame = ctk.CTkFrame(options_row, fg_color="transparent")
        colors_frame.pack(side="right")
        
        self.selected_color = "#3B82F6"
        self.color_buttons = []
        
        color_choices = [
            ("#3B82F6", "Mavi"),
            ("#F59E0B", "Turuncu"),
            ("#10B981", "Yeşil"),
            ("#EF4444", "Kırmızı"),
            ("#8B5CF6", "Mor")
        ]
        
        def select_color(col_hex, btn_widget):
            self.selected_color = col_hex
            for btn in self.color_buttons:
                btn.configure(border_width=0)
            btn_widget.configure(border_width=2, border_color="#1E293B")
            
        for hex_val, name in color_choices:
            btn = ctk.CTkButton(
                colors_frame, text="", fg_color=hex_val, hover_color=hex_val,
                width=16, height=16, corner_radius=8, border_width=0
            )
            btn.configure(command=lambda h=hex_val, b=btn: select_color(h, b))
            btn.pack(side="left", padx=2)
            self.color_buttons.append(btn)
            
        # İlk rengi varsayılan olarak seçili göster
        self.color_buttons[0].configure(border_width=2, border_color="#1E293B")
        
        self.btn_add_task = ctk.CTkButton(
            self.task_form_frame, text="+ Planla", font=Fontlar.SMALL_BOLD, 
            fg_color=Renkler.PRIMARY, hover_color=Renkler.PRIMARY_HOVER, height=28,
            command=self.add_manual_task
        )
        self.btn_add_task.pack(fill="x", padx=15, pady=(5, 12))
        
        # C. Orta Görev Listesi Bölümü (Scrollable)
        self.scroll_details = ctk.CTkScrollableFrame(self.right_card, fg_color="transparent")
        self.scroll_details.pack(fill="both", expand=True, padx=10, pady=5)
        
        # İnce ve modern scrollbar stili
        try:
            self.scroll_details._scrollbar.configure(
                width=6, fg_color="transparent", 
                scrollbar_color="#CBD5E1", scrollbar_hover_color="#94A3B8"
            )
        except Exception:
            pass

    # ── METODLAR ─────────────────────────────────────────────────────────────

    def prev_month(self):
        self.current_month -= 1
        if self.current_month == 0:
            self.current_month = 12
            self.current_year -= 1
        self.load_data()

    def next_month(self):
        self.current_month += 1
        if self.current_month == 13:
            self.current_month = 1
            self.current_year += 1
        self.load_data()

    def go_today(self):
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.selected_date = date.today()
        self.load_data()

    def select_date(self, day_num):
        if day_num <= 0: return
        self.selected_date = date(self.current_year, self.current_month, day_num)
        self.update_details_panel()
        self.draw_calendar_grid()

    def load_data(self):
        aylar = [
            "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", 
            "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
        ]
        self.lbl_month.configure(text=f"{aylar[self.current_month - 1]} {self.current_year}")
        
        user_id = self.current_user["id"]
        conn = self.db.connect()
        cursor = conn.cursor()
        
        # 1. Teklif Teslimatlarını Çek
        cursor.execute("""
            SELECT t.id, t.teklif_no, t.baslik, t.teslim_tarihi, t.durum, m.firma_adi
            FROM teklifler t
            LEFT JOIN musteriler m ON t.musteri_id = m.id
            WHERE t.kullanici_id = ? AND t.teslim_tarihi IS NOT NULL AND t.teslim_tarihi != ''
        """, (user_id,))
        teklifler = cursor.fetchall()
        
        # 2. Manuel Takvim İşlerini Çek (saat ve renk dahil)
        cursor.execute("""
            SELECT id, baslik, aciklama, teslim_tarihi, durum, saat, renk
            FROM takvim_isleri
            WHERE kullanici_id = ? AND teslim_tarihi IS NOT NULL AND teslim_tarihi != ''
        """, (user_id,))
        gorevler = cursor.fetchall()
        conn.close()
        
        self.events_cache = {}
        
        for t in teklifler:
            tarih_str = t["teslim_tarihi"]
            if tarih_str not in self.events_cache:
                self.events_cache[tarih_str] = []
            self.events_cache[tarih_str].append({
                "type": "teklif",
                "id": t["id"],
                "badge": f"TEK-{t['teklif_no'][-4:] if t['teklif_no'] else ''}",
                "title": t["baslik"],
                "durum": t["durum"],
                "subtitle": f"Müşteri: {t['firma_adi'] or '-'}",
                "saat": "17:00",  # Teslimat için varsayılan saat
                "renk": "#F59E0B"
            })
            
        for g in gorevler:
            tarih_str = g["teslim_tarihi"]
            if tarih_str not in self.events_cache:
                self.events_cache[tarih_str] = []
            self.events_cache[tarih_str].append({
                "type": "gorev",
                "id": g["id"],
                "badge": "GÖREV",
                "title": g["baslik"],
                "durum": g["durum"] or "Yapılacak",
                "subtitle": g["aciklama"] or "",
                "saat": g["saat"] or "12:00",
                "renk": g["renk"] or "#3B82F6"
            })
            
        self.draw_calendar_grid()
        self.update_details_panel()

    def draw_calendar_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
            
        cal = calendar.Calendar(firstweekday=0)
        weeks = cal.monthdayscalendar(self.current_year, self.current_month)
        
        bugun = date.today()
        
        for r_idx, week in enumerate(weeks):
            for c_idx, day in enumerate(week):
                if day == 0:
                    cell = ctk.CTkFrame(self.grid_frame, fg_color="transparent", border_width=0)
                    cell.grid(row=r_idx, column=c_idx, sticky="nsew", padx=2, pady=2)
                    continue
                
                cell_date = date(self.current_year, self.current_month, day)
                cell_date_str = cell_date.strftime("%Y-%m-%d")
                
                border_w = 0
                bg_col = Renkler.BG_LIGHT
                
                if cell_date == self.selected_date:
                    border_w = 2
                    border_c = Renkler.PRIMARY
                    bg_col = Renkler.CARD_BG
                elif cell_date == bugun:
                    border_w = 2
                    border_c = Renkler.SUCCESS
                    bg_col = Renkler.CARD_BG
                else:
                    border_c = bg_col
                
                cell = ctk.CTkFrame(
                    self.grid_frame, fg_color=bg_col, border_width=border_w, 
                    border_color=border_c, corner_radius=6
                )
                cell.grid(row=r_idx, column=c_idx, sticky="nsew", padx=2, pady=2)
                
                cell.bind("<Button-1>", lambda e, d=day: self.select_date(d))
                
                num_color = Renkler.TEXT_DARK
                if c_idx >= 5: num_color = Renkler.TEXT_GRAY
                
                lbl_num = ctk.CTkLabel(cell, text=str(day), font=Fontlar.SMALL_BOLD, text_color=num_color)
                lbl_num.pack(anchor="ne", padx=6, pady=3)
                lbl_num.bind("<Button-1>", lambda e, d=day: self.select_date(d))
                
                if cell_date_str in self.events_cache:
                    day_events = self.events_cache[cell_date_str]
                    for e_idx, ev in enumerate(day_events[:2]):
                        lbl_text = f"• {ev['badge']}"
                        t_col = ev["renk"]
                        
                        lbl_ev = ctk.CTkLabel(
                            cell, text=lbl_text, font=ctk.CTkFont(family="Inter", size=9, weight="bold"),
                            text_color=t_col, anchor="w"
                        )
                        lbl_ev.pack(fill="x", padx=6, pady=0)
                        lbl_ev.bind("<Button-1>", lambda e, d=day: self.select_date(d))
                        
                    if len(day_events) > 2:
                        lbl_more = ctk.CTkLabel(
                            cell, text=f"+ {len(day_events)-2} daha", 
                            font=ctk.CTkFont(family="Inter", size=8, weight="bold"),
                            text_color=Renkler.TEXT_GRAY, anchor="w"
                        )
                        lbl_more.pack(fill="x", padx=6, pady=0)
                        lbl_more.bind("<Button-1>", lambda e, d=day: self.select_date(d))

    def update_details_panel(self):
        aylar = [
            "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", 
            "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
        ]
        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        
        self.lbl_selected_day.configure(
            text=f"{self.selected_date.day} {aylar[self.selected_date.month - 1]} {self.selected_date.year}"
        )
        self.lbl_selected_weekday.configure(
            text=gunler[self.selected_date.weekday()]
        )
        
        for w in self.scroll_details.winfo_children():
            w.destroy()
            
        tarih_key = self.selected_date.strftime("%Y-%m-%d")
        
        # 1. BÖLÜM: BÜGÜNKÜ İŞLER
        lbl_today_title = ctk.CTkLabel(
            self.scroll_details, text="Bugünkü İşler", 
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"), 
            text_color=Renkler.TEXT_DARK, anchor="w"
        )
        lbl_today_title.pack(fill="x", padx=5, pady=(5, 8))
        
        if tarih_key not in self.events_cache or not self.events_cache[tarih_key]:
            lbl_empty = ctk.CTkLabel(
                self.scroll_details, text="Bugün için planlanmış görev bulunmuyor.", 
                font=ctk.CTkFont(family="Inter", size=11), text_color=Renkler.TEXT_GRAY,
                justify="center"
            )
            lbl_empty.pack(fill="x", pady=15)
        else:
            for ev in self.events_cache[tarih_key]:
                card = ctk.CTkFrame(self.scroll_details, fg_color="#F8FAFC", corner_radius=8, height=65)
                card.pack(fill="x", pady=4, padx=5)
                card.pack_propagate(False)
                
                # Sol Accent Çizgisi Rengi
                strip_color = "#3B82F6"
                if ev["type"] == "teklif":
                    if ev["durum"] == "Beklemede": strip_color = "#F59E0B"
                    elif ev["durum"] == "Onaylandı": strip_color = "#10B981"
                    elif ev["durum"] == "Reddedildi": strip_color = "#EF4444"
                    else: strip_color = "#6B7280"
                else:
                    strip_color = ev.get("renk", "#3B82F6")
                
                # Sol Accent Çizgi
                strip = ctk.CTkFrame(card, fg_color=strip_color, width=4, corner_radius=0)
                strip.pack(side="left", fill="y")
                
                info = ctk.CTkFrame(card, fg_color="transparent")
                info.pack(side="left", fill="both", expand=True, padx=10, pady=6)
                
                # Üst Sıra (Rozet & Saat)
                t_row = ctk.CTkFrame(info, fg_color="transparent")
                t_row.pack(fill="x")
                
                lbl_badge = ctk.CTkLabel(
                    t_row, text=ev["badge"], font=ctk.CTkFont(family="Inter", size=8, weight="bold"),
                    text_color="white", fg_color=strip_color, corner_radius=4, width=50
                )
                lbl_badge.pack(side="left")
                
                lbl_time = ctk.CTkLabel(
                    t_row, text=ev.get("saat", "12:00"), font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
                    text_color=Renkler.TEXT_GRAY
                )
                lbl_time.pack(side="right")
                
                # Alt Sıra (Başlık & Müşteri/Detay)
                lbl_title = ctk.CTkLabel(
                    info, text=ev["title"], font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                    text_color=Renkler.TEXT_DARK, anchor="w"
                )
                lbl_title.pack(fill="x", pady=(2, 0))
                
                lbl_sub = ctk.CTkLabel(
                    info, text=ev["subtitle"], font=ctk.CTkFont(family="Inter", size=10),
                    text_color=Renkler.TEXT_GRAY, anchor="w"
                )
                lbl_sub.pack(fill="x")
                
                # Hover & Click Entegrasyonları
                def make_hover(c=card):
                    c.bind("<Enter>", lambda e: c.configure(fg_color="#F1F5F9"))
                    c.bind("<Leave>", lambda e: c.configure(fg_color="#F8FAFC"))
                make_hover()
                
                card.bind("<Button-1>", lambda e, item=ev: self.show_event_details(item))
                for child in [info, t_row, lbl_badge, lbl_time, lbl_title, lbl_sub]:
                    child.bind("<Button-1>", lambda e, item=ev: self.show_event_details(item))
                    child.bind("<Enter>", lambda e: card.configure(fg_color="#F1F5F9"))
                    child.bind("<Leave>", lambda e: card.configure(fg_color="#F8FAFC"))

        # 2. BÖLÜM: YAKLAŞAN TESLİMLER (Sonraki 7 Gün)
        ctk.CTkFrame(self.scroll_details, fg_color=Renkler.BORDER, height=1).pack(fill="x", padx=5, pady=(15, 10))
        
        lbl_upcoming_title = ctk.CTkLabel(
            self.scroll_details, text="Yaklaşan Teslimler (7 Gün)", 
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"), 
            text_color=Renkler.TEXT_DARK, anchor="w"
        )
        lbl_upcoming_title.pack(fill="x", padx=5, pady=(0, 8))
        
        upcoming_found = False
        
        for offset in range(1, 8):
            future_date = self.selected_date + timedelta(days=offset)
            future_key = future_date.strftime("%Y-%m-%d")
            
            if future_key in self.events_cache and self.events_cache[future_key]:
                for ev in self.events_cache[future_key]:
                    upcoming_found = True
                    card = ctk.CTkFrame(self.scroll_details, fg_color="#F8FAFC", corner_radius=8, height=52)
                    card.pack(fill="x", pady=3, padx=5)
                    card.pack_propagate(False)
                    
                    # Renk Seçimi
                    strip_color = "#3B82F6"
                    if ev["type"] == "teklif":
                        if ev["durum"] == "Beklemede": strip_color = "#F59E0B"
                        elif ev["durum"] == "Onaylandı": strip_color = "#10B981"
                        elif ev["durum"] == "Reddedildi": strip_color = "#EF4444"
                        else: strip_color = "#6B7280"
                    else:
                        strip_color = ev.get("renk", "#3B82F6")
                        
                    # Sol Çizgi
                    strip = ctk.CTkFrame(card, fg_color=strip_color, width=4, corner_radius=0)
                    strip.pack(side="left", fill="y")
                    
                    info = ctk.CTkFrame(card, fg_color="transparent")
                    info.pack(side="left", fill="both", expand=True, padx=8, pady=4)
                    
                    # Satır
                    t_row = ctk.CTkFrame(info, fg_color="transparent")
                    t_row.pack(fill="x")
                    
                    lbl_f_date = ctk.CTkLabel(
                        t_row, text=f"{future_date.day} {aylar[future_date.month-1][:3]}",
                        font=ctk.CTkFont(family="Inter", size=9, weight="bold"), text_color=Renkler.TEXT_GRAY
                    )
                    lbl_f_date.pack(side="left", padx=(0, 6))
                    
                    lbl_badge = ctk.CTkLabel(
                        t_row, text=ev["badge"], font=ctk.CTkFont(family="Inter", size=8, weight="bold"),
                        text_color="white", fg_color=strip_color, corner_radius=4, width=50
                    )
                    lbl_badge.pack(side="left")
                    
                    lbl_time = ctk.CTkLabel(
                        t_row, text=ev.get("saat", "12:00"), font=ctk.CTkFont(family="Inter", size=9),
                        text_color=Renkler.TEXT_GRAY
                    )
                    lbl_time.pack(side="right")
                    
                    lbl_title = ctk.CTkLabel(
                        info, text=ev["title"], font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
                        text_color=Renkler.TEXT_DARK, anchor="w"
                    )
                    lbl_title.pack(fill="x")
                    
                    # Hover & Clicks
                    def make_hover_upcoming(c=card):
                        c.bind("<Enter>", lambda e: c.configure(fg_color="#F1F5F9"))
                        c.bind("<Leave>", lambda e: c.configure(fg_color="#F8FAFC"))
                    make_hover_upcoming()
                    
                    card.bind("<Button-1>", lambda e, item=ev: self.show_event_details(item))
                    for child in [info, t_row, lbl_f_date, lbl_badge, lbl_time, lbl_title]:
                        child.bind("<Button-1>", lambda e, item=ev: self.show_event_details(item))
                        child.bind("<Enter>", lambda e: card.configure(fg_color="#F1F5F9"))
                        child.bind("<Leave>", lambda e: card.configure(fg_color="#F8FAFC"))
                        
        if not upcoming_found:
            lbl_no_up = ctk.CTkLabel(
                self.scroll_details, text="Yaklaşan 7 gün içinde planlanmış teslimat bulunmuyor.",
                font=ctk.CTkFont(family="Inter", size=11), text_color=Renkler.TEXT_GRAY,
                justify="center"
            )
            lbl_no_up.pack(fill="x", pady=10)

    def show_event_details(self, ev):
        detail_win = ctk.CTkToplevel(self)
        detail_win.title("Plan Detayı")
        detail_win.geometry("380x280")
        detail_win.resizable(False, False)
        detail_win.configure(fg_color="white")
        detail_win.transient(self)
        detail_win.grab_set()
        
        detail_win.update_idletasks()
        width = 380
        height = 280
        x = self.winfo_screenwidth() // 2 - width // 2
        y = self.winfo_screenheight() // 2 - height // 2
        detail_win.geometry(f"+{x}+{y}")
        
        hdr_color = "#3B82F6"
        if ev["type"] == "teklif":
            if ev["durum"] == "Beklemede": hdr_color = "#F59E0B"
            elif ev["durum"] == "Onaylandı": hdr_color = "#10B981"
            elif ev["durum"] == "Reddedildi": hdr_color = "#EF4444"
            else: hdr_color = "#6B7280"
        else:
            hdr_color = ev.get("renk", "#3B82F6")
            
        hdr = ctk.CTkFrame(detail_win, fg_color=hdr_color, height=60, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        
        lbl_hdr = ctk.CTkLabel(
            hdr, text=ev["badge"], font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color="white", anchor="w"
        )
        lbl_hdr.pack(fill="both", expand=True, padx=20)
        
        content = ctk.CTkFrame(detail_win, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=15)
        
        ctk.CTkLabel(content, text="Başlık / Açıklama:", font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color=Renkler.TEXT_GRAY, anchor="w").pack(fill="x")
        ctk.CTkLabel(content, text=ev["title"], font=ctk.CTkFont(family="Inter", size=14, weight="bold"), text_color=Renkler.TEXT_DARK, anchor="w", wraplength=340).pack(fill="x", pady=(0, 10))
        
        row = ctk.CTkFrame(content, fg_color="transparent")
        row.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(row, text="Planlanan Saat:", font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color=Renkler.TEXT_GRAY, anchor="w").pack(fill="x")
        ctk.CTkLabel(row, text=ev.get("saat", "12:00"), font=ctk.CTkFont(family="Inter", size=12, weight="bold"), text_color=Renkler.PRIMARY, anchor="w").pack(fill="x")
        
        ctk.CTkLabel(content, text="Detaylar / Müşteri:", font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color=Renkler.TEXT_GRAY, anchor="w").pack(fill="x")
        ctk.CTkLabel(content, text=ev["subtitle"], font=ctk.CTkFont(family="Inter", size=12), text_color=Renkler.TEXT_DARK, anchor="w", wraplength=340, justify="left").pack(fill="x", pady=(0, 15))
        
        actions = ctk.CTkFrame(detail_win, fg_color="transparent")
        actions.pack(fill="x", side="bottom", pady=15, padx=20)
        
        if ev["type"] == "gorev":
            def delete_and_close():
                detail_win.destroy()
                self.delete_manual_task(ev["id"])
                
            btn_del = ctk.CTkButton(
                actions, text="Görevi Sil", font=Fontlar.SMALL_BOLD, fg_color=Renkler.ERROR,
                hover_color="#DC2626", height=32, command=delete_and_close
            )
            btn_del.pack(side="left")
            
        btn_close = ctk.CTkButton(
            actions, text="Kapat", font=Fontlar.SMALL_BOLD, fg_color=Renkler.BORDER,
            text_color=Renkler.TEXT_DARK, hover_color="#E2E8F0", height=32, command=detail_win.destroy
        )
        btn_close.pack(side="right")

    def add_manual_task(self):
        baslik = self.entry_task_title.get().strip()
        aciklama = self.entry_task_desc.get().strip()
        saat = self.combo_task_time.get()
        renk = self.selected_color
        
        if not baslik:
            messagebox.showwarning("Uyarı", "Lütfen görev başlığını boş bırakmayın.")
            return
            
        tarih_str = self.selected_date.strftime("%Y-%m-%d")
        user_id = self.current_user["id"]
        
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO takvim_isleri (kullanici_id, baslik, aciklama, baslangic_tarihi, teslim_tarihi, durum, saat, renk)
            VALUES (?, ?, ?, ?, ?, 'Devam Ediyor', ?, ?)
        """, (user_id, baslik, aciklama, tarih_str, tarih_str, saat, renk))
        conn.commit()
        conn.close()
        
        self.entry_task_title.delete(0, "end")
        self.entry_task_desc.delete(0, "end")
        
        self.load_data()
        
        if hasattr(self.master.master, 'screens'):
            screens = self.master.master.screens
            if "dashboard" in screens and hasattr(screens["dashboard"], "load_data"):
                screens["dashboard"]._needs_refresh = True

    def delete_manual_task(self, task_id):
        if not messagebox.askyesno("Onay", "Bu görevi silmek istediğinize emin misiniz?"):
            return
            
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM takvim_isleri WHERE id = ? AND kullanici_id = ?", (task_id, self.current_user["id"]))
        conn.commit()
        conn.close()
        
        self.load_data()
        
        if hasattr(self.master.master, 'screens'):
            screens = self.master.master.screens
            if "dashboard" in screens and hasattr(screens["dashboard"], "load_data"):
                screens["dashboard"]._needs_refresh = True

    def apply_theme(self):
        self.configure(fg_color=Renkler.BG_LIGHT)
        try:
            self.calendar_card.configure(fg_color=Renkler.CARD_BG)
            self.right_card.configure(fg_color=Renkler.CARD_BG)
            self.task_form_frame.configure(fg_color=Renkler.BG_LIGHT)
        except Exception:
            pass
        self._needs_refresh = True
        is_active = (hasattr(self.master, "master") and getattr(self.master.master, "current_screen", None) == self)
        if is_active:
            self.load_data()
