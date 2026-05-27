import customtkinter as ctk
from tema import Renkler, Fontlar
import database

class HurdaScreen(ctk.CTkFrame):
    def __init__(self, master, current_user):
        super().__init__(master, fg_color=Renkler.BG_LIGHT)
        self.current_user = current_user
        self.db = database.Database()
        self._needs_refresh = False
        
        self.secili_hurda_id = None
        self.secili_hurda_veri = None
        
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # ── ÜST BAŞLIK ALANI ──────────────────────────────────────────────────
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(30, 15))
        
        ctk.CTkLabel(
            self.header_frame, 
            text="Hurda Deposu ve Yönetimi", 
            font=Fontlar.H1, 
            text_color=Renkler.TEXT_DARK
        ).pack(side="left")

        # ── 3'LÜ KPI KART SATIRI ──────────────────────────────────────────────
        self.kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=25, pady=(0, 15))
        self.kpi_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="kpi")
        
        self.lbl_depo_miktar = self.create_kpi_card(self.kpi_frame, "Depodaki Toplam Hurda", "0 Birim", 0)
        self.lbl_depo_deger = self.create_kpi_card(self.kpi_frame, "Tahmini Depo Değeri", "0.00 ₺", 1)
        self.lbl_toplam_satis = self.create_kpi_card(self.kpi_frame, "Toplam Satış Geliri", "0.00 ₺", 2)

        # ── ANA ALAN (BÖLÜNMÜŞ DÜZEN) ─────────────────────────────────────────
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        self.content_frame.grid_columnconfigure(0, weight=6) # Sol Listeler (Tabs)
        self.content_frame.grid_columnconfigure(1, weight=4) # Sağ İşlemler Paneli
        self.content_frame.grid_rowconfigure(0, weight=1)

        # ── SOL: TABVIEW (Depodakiler / Satılanlar) ──────────────────────────
        self.left_card = ctk.CTkFrame(self.content_frame, fg_color=Renkler.CARD_BG, corner_radius=10)
        self.left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        self.tabview = ctk.CTkTabview(self.left_card, fg_color="transparent", segmented_button_selected_color=Renkler.PRIMARY)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tab_depo = self.tabview.add("Depodaki Hurdalar")
        self.tab_satis = self.tabview.add("Satış Geçmişi")
        
        self.build_depo_tab()
        self.build_satis_tab()

        # ── SAĞ: FORM VE İŞLEMLER KARTI ───────────────────────────────────────
        self.right_card = ctk.CTkFrame(self.content_frame, fg_color=Renkler.CARD_BG, corner_radius=10)
        self.right_card.grid(row=0, column=1, sticky="nsew")
        
        self.build_action_panel()

    def create_kpi_card(self, parent, title, value, col):
        card = ctk.CTkFrame(parent, fg_color=Renkler.CARD_BG, corner_radius=10, height=85)
        card.grid(row=0, column=col, sticky="nsew", padx=5)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=title, font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY).pack(anchor="w", padx=15, pady=(12, 1))
        lbl_val = ctk.CTkLabel(card, text=value, font=Fontlar.H3, text_color=Renkler.TEXT_DARK)
        lbl_val.pack(anchor="w", padx=15)
        return lbl_val

    # ── TAB TASARIMLARI ──────────────────────────────────────────────────────

    def build_depo_tab(self):
        # Başlık Satırı
        header = ctk.CTkFrame(self.tab_depo, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)
        header.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        ctk.CTkLabel(header, text="Malzeme", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_GRAY, anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="Miktar", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_GRAY, anchor="w").grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(header, text="Birim Fiyat", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_GRAY, anchor="w").grid(row=0, column=2, sticky="w")
        ctk.CTkLabel(header, text="Toplam Değer", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_GRAY, anchor="w").grid(row=0, column=3, sticky="w")
        
        ctk.CTkFrame(self.tab_depo, fg_color=Renkler.BORDER, height=1).pack(fill="x", padx=5, pady=2)
        
        self.scroll_depo = ctk.CTkScrollableFrame(self.tab_depo, fg_color="transparent")
        self.scroll_depo.pack(fill="both", expand=True, padx=2, pady=2)

    def build_satis_tab(self):
        header = ctk.CTkFrame(self.tab_satis, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)
        header.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        ctk.CTkLabel(header, text="Malzeme", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_GRAY, anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="Satılan Miktar", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_GRAY, anchor="w").grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(header, text="Satış Fiyatı", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_GRAY, anchor="w").grid(row=0, column=2, sticky="w")
        ctk.CTkLabel(header, text="Toplam Gelir", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_GRAY, anchor="w").grid(row=0, column=3, sticky="w")
        
        ctk.CTkFrame(self.tab_satis, fg_color=Renkler.BORDER, height=1).pack(fill="x", padx=5, pady=2)
        
        self.scroll_satis = ctk.CTkScrollableFrame(self.tab_satis, fg_color="transparent")
        self.scroll_satis.pack(fill="both", expand=True, padx=2, pady=2)

    # ── SAĞ İŞLEMLER PANELİ ──────────────────────────────────────────────────

    def build_action_panel(self):
        self.lbl_panel_title = ctk.CTkLabel(self.right_card, text="Manuel Hurda Girişi", font=Fontlar.H3, text_color=Renkler.TEXT_DARK)
        self.lbl_panel_title.pack(anchor="w", padx=20, pady=(20, 10))
        
        self.action_scroll = ctk.CTkScrollableFrame(self.right_card, fg_color="transparent")
        self.action_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 1. KISIM: MANUEL EKLEME FORMU (Görünür / Gizlenir)
        self.frame_manuel_ekle = ctk.CTkFrame(self.action_scroll, fg_color="transparent")
        self.frame_manuel_ekle.pack(fill="x")
        
        # Malzeme Seçimi
        mat_frame = ctk.CTkFrame(self.frame_manuel_ekle, fg_color="transparent")
        mat_frame.pack(fill="x", padx=15, pady=6)
        ctk.CTkLabel(mat_frame, text="Malzeme Seçin:", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK).pack(anchor="w", pady=(0, 2))
        self.combo_malzeme = ctk.CTkComboBox(mat_frame, values=[], font=Fontlar.SMALL, height=35)
        self.combo_malzeme.pack(fill="x")
        
        self.entry_miktar = self.create_form_input(self.frame_manuel_ekle, "Miktar (Fire Miktarı):")
        self.entry_hurda_fiyat = self.create_form_input(self.frame_manuel_ekle, "Hurda Birim Fiyatı (₺):")
        
        self.btn_ekle = ctk.CTkButton(self.frame_manuel_ekle, text="Depoya Hurda Ekle", font=Fontlar.BODY_BOLD, fg_color=Renkler.PRIMARY, hover_color=Renkler.PRIMARY_HOVER, command=self.manuel_hurda_ekle)
        self.btn_ekle.pack(fill="x", padx=15, pady=15)
        
        # 2. KISIM: HURDA SATIŞ FORMU (Başlangıçta gizli, hurda seçildiğinde açılır)
        self.frame_satis_yap = ctk.CTkFrame(self.action_scroll, fg_color="transparent")
        # .pack() çağrısı seçime göre yapılacak
        
        self.lbl_secili_info = ctk.CTkLabel(self.frame_satis_yap, text="Seçili Hurda: Sac", font=Fontlar.BODY_BOLD, text_color=Renkler.PRIMARY, justify="left", anchor="w")
        self.lbl_secili_info.pack(fill="x", padx=15, pady=6)
        
        self.entry_satis_fiyati = self.create_form_input(self.frame_satis_yap, "Gerçekleşen Satış Birim Fiyatı (₺):")
        
        self.btn_satis_onayla = ctk.CTkButton(self.frame_satis_yap, text="Satışı Tamamla", font=Fontlar.BODY_BOLD, fg_color=Renkler.SUCCESS, hover_color="#059669", command=self.hurda_satisi_tamamla)
        self.btn_satis_onayla.pack(fill="x", padx=15, pady=10)
        
        self.btn_iptal = ctk.CTkButton(self.frame_satis_yap, text="İptal Et / Manuel Moda Dön", font=Fontlar.SMALL_BOLD, fg_color="transparent", text_color=Renkler.TEXT_GRAY, hover_color=Renkler.BORDER, command=self.islem_modu_sifirla)
        self.btn_iptal.pack(fill="x", padx=15, pady=5)

    def create_form_input(self, parent, label_text):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=6)
        ctk.CTkLabel(frame, text=label_text, font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK).pack(anchor="w", pady=(0, 2))
        entry = ctk.CTkEntry(frame, font=Fontlar.SMALL, height=35)
        entry.pack(fill="x")
        return entry

    # ── VERİ YÜKLEME VE HESAPLAR ─────────────────────────────────────────────

    def load_data(self):
        user_id = self.current_user["id"]
        conn = self.db.connect()
        cursor = conn.cursor()
        
        # 1. KPI Hesapları
        cursor.execute("SELECT SUM(fire_miktari), SUM(tahmini_hurda_degeri) FROM hurda_hareketleri WHERE kullanici_id = ? AND durum = 'Depoda'", (user_id,))
        depo_stats = cursor.fetchone()
        depo_miktar = depo_stats[0] or 0.0
        depo_deger = depo_stats[1] or 0.0
        
        cursor.execute("SELECT SUM(tahmini_hurda_degeri) FROM hurda_hareketleri WHERE kullanici_id = ? AND durum = 'Satıldı'", (user_id,))
        satis_gelir = cursor.fetchone()[0] or 0.0
        
        self.lbl_depo_miktar.configure(text=f"{depo_miktar:,.1f} Birim")
        self.lbl_depo_deger.configure(text=f"{depo_deger:,.2f} ₺")
        self.lbl_toplam_satis.configure(text=f"{satis_gelir:,.2f} ₺")
        
        # 2. Donut / Combobox için Malzemeleri Çek
        cursor.execute("SELECT id, malzeme_adi, birim, hurda_birim_fiyati FROM malzemeler WHERE kullanici_id = ? AND aktif = 1", (user_id,))
        self.malzemeler_listesi = cursor.fetchall()
        self.combo_malzeme.configure(values=[m["malzeme_adi"] for m in self.malzemeler_listesi])
        if self.malzemeler_listesi:
            self.combo_malzeme.set(self.malzemeler_listesi[0]["malzeme_adi"])
            self.entry_hurda_fiyat.delete(0, "end")
            self.entry_hurda_fiyat.insert(0, str(self.malzemeler_listesi[0]["hurda_birim_fiyati"] or 0.0))
            
        # Malzeme seçiminde fiyatı otomatik doldurması için event bind etme
        self.combo_malzeme.configure(command=self.on_malzeme_degisti)

        # 3. Tab 1: Depodaki Hurdalar Listesi
        for w in self.scroll_depo.winfo_children(): w.destroy()
        cursor.execute("""
            SELECT id, malzeme_adi, fire_miktari, birim, hurda_birim_fiyati, tahmini_hurda_degeri
            FROM hurda_hareketleri
            WHERE kullanici_id = ? AND durum = 'Depoda'
            ORDER BY id DESC
        """, (user_id,))
        depodakiler = cursor.fetchall()
        
        if not depodakiler:
            ctk.CTkLabel(self.scroll_depo, text="Depoda birikmiş hurda bulunmuyor.", font=Fontlar.BODY, text_color=Renkler.TEXT_GRAY).pack(pady=30)
        else:
            for hh in depodakiler:
                satir = ctk.CTkFrame(self.scroll_depo, fg_color="transparent")
                satir.pack(fill="x", pady=2)
                satir.grid_columnconfigure((0, 1, 2, 3), weight=1)
                
                btn_ad = ctk.CTkButton(
                    satir, 
                    text=hh["malzeme_adi"] or "Genel Hurda", 
                    font=Fontlar.SMALL_BOLD, 
                    fg_color="transparent", 
                    text_color=Renkler.TEXT_DARK, 
                    hover_color=Renkler.BORDER,
                    anchor="w",
                    command=lambda val=dict(hh): self.hurda_sec_satis_icin(val)
                )
                btn_ad.grid(row=0, column=0, sticky="ew")
                
                ctk.CTkLabel(satir, text=f"{hh['fire_miktari']:.1f} {hh['birim'] or 'Birim'}", font=Fontlar.SMALL, text_color=Renkler.TEXT_DARK, anchor="w").grid(row=0, column=1, sticky="w", padx=10)
                ctk.CTkLabel(satir, text=f"{hh['hurda_birim_fiyati']:.2f} ₺", font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY, anchor="w").grid(row=0, column=2, sticky="w", padx=10)
                ctk.CTkLabel(satir, text=f"{hh['tahmini_hurda_degeri']:.2f} ₺", font=Fontlar.SMALL_BOLD, text_color=Renkler.PRIMARY, anchor="w").grid(row=0, column=3, sticky="w", padx=10)
                
                ctk.CTkFrame(self.scroll_depo, fg_color=Renkler.BORDER, height=1).pack(fill="x", pady=1)

        # 4. Tab 2: Satılan Hurdalar Listesi
        for w in self.scroll_satis.winfo_children(): w.destroy()
        cursor.execute("""
            SELECT id, malzeme_adi, fire_miktari, birim, hurda_birim_fiyati, tahmini_hurda_degeri
            FROM hurda_hareketleri
            WHERE kullanici_id = ? AND durum = 'Satıldı'
            ORDER BY id DESC
        """, (user_id,))
        satilanlar = cursor.fetchall()
        
        if not satilanlar:
            ctk.CTkLabel(self.scroll_satis, text="Henüz hurda satışı gerçekleştirilmedi.", font=Fontlar.BODY, text_color=Renkler.TEXT_GRAY).pack(pady=30)
        else:
            for hh in satilanlar:
                satir = ctk.CTkFrame(self.scroll_satis, fg_color="transparent")
                satir.pack(fill="x", pady=2)
                satir.grid_columnconfigure((0, 1, 2, 3), weight=1)
                
                ctk.CTkLabel(satir, text=hh["malzeme_adi"] or "Genel Hurda", font=Fontlar.SMALL_BOLD, text_color=Renkler.TEXT_DARK, anchor="w").grid(row=0, column=0, sticky="w")
                ctk.CTkLabel(satir, text=f"{hh['fire_miktari']:.1f} {hh['birim'] or 'Birim'}", font=Fontlar.SMALL, text_color=Renkler.TEXT_DARK, anchor="w").grid(row=0, column=1, sticky="w", padx=10)
                ctk.CTkLabel(satir, text=f"{hh['hurda_birim_fiyati']:.2f} ₺", font=Fontlar.SMALL, text_color=Renkler.TEXT_GRAY, anchor="w").grid(row=0, column=2, sticky="w", padx=10)
                ctk.CTkLabel(satir, text=f"{hh['tahmini_hurda_degeri']:.2f} ₺", font=Fontlar.SMALL_BOLD, text_color=Renkler.SUCCESS, anchor="w").grid(row=0, column=3, sticky="w", padx=10)
                
                ctk.CTkFrame(self.scroll_satis, fg_color=Renkler.BORDER, height=1).pack(fill="x", pady=1)
                
        conn.close()

    def on_malzeme_degisti(self, secilen_ad):
        for m in self.malzemeler_listesi:
            if m["malzeme_adi"] == secilen_ad:
                self.entry_hurda_fiyat.delete(0, "end")
                self.entry_hurda_fiyat.insert(0, str(m["hurda_birim_fiyati"] or 0.0))
                break

    # ── BUTON AKSİYONLARI VE MOD GEÇİŞLERİ ───────────────────────────────────

    def hurda_sec_satis_icin(self, hurda_verisi):
        self.secili_hurda_id = hurda_verisi["id"]
        self.secili_hurda_veri = hurda_verisi
        
        self.lbl_panel_title.configure(text="Hurda Satışı Yap")
        
        # Ekleme formunu kaldır, Satış formunu göster
        self.frame_manuel_ekle.pack_forget()
        self.frame_satis_yap.pack(fill="x")
        
        self.lbl_secili_info.configure(text=f"Seçili: {hurda_verisi['malzeme_adi']}\nMiktar: {hurda_verisi['fire_miktari']} Birim\nTahmini Değer: {hurda_verisi['tahmini_hurda_degeri']} ₺")
        
        self.entry_satis_fiyati.delete(0, "end")
        self.entry_satis_fiyati.insert(0, str(hurda_verisi["hurda_birim_fiyati"]))

    def islem_modu_sifirla(self):
        self.secili_hurda_id = None
        self.secili_hurda_veri = None
        
        self.lbl_panel_title.configure(text="Manuel Hurda Girişi")
        self.frame_satis_yap.pack_forget()
        self.frame_manuel_ekle.pack(fill="x")
        
        self.entry_miktar.delete(0, "end")
        if self.malzemeler_listesi:
            self.combo_malzeme.set(self.malzemeler_listesi[0]["malzeme_adi"])
            self.entry_hurda_fiyat.delete(0, "end")
            self.entry_hurda_fiyat.insert(0, str(self.malzemeler_listesi[0]["hurda_birim_fiyati"] or 0.0))

    def manuel_hurda_ekle(self):
        secilen_mat_ad = self.combo_malzeme.get()
        miktar_str = self.entry_miktar.get().strip()
        fiyat_str = self.entry_hurda_fiyat.get().strip()
        
        if not miktar_str or not secilen_mat_ad:
            return
            
        try:
            miktar = float(miktar_str)
            fiyat = float(fiyat_str or 0.0)
        except ValueError:
            return
            
        # Malzeme birimini bul
        birim = "kg"
        for m in self.malzemeler_listesi:
            if m["malzeme_adi"] == secilen_mat_ad:
                birim = m["birim"]
                break
                
        conn = self.db.connect()
        cursor = conn.cursor()
        
        tahmini_deger = miktar * fiyat
        cursor.execute("""
            INSERT INTO hurda_hareketleri (kullanici_id, malzeme_adi, fire_miktari, birim, hurda_birim_fiyati, tahmini_hurda_degeri, durum)
            VALUES (?, ?, ?, ?, ?, ?, 'Depoda')
        """, (self.current_user["id"], secilen_mat_ad, miktar, birim, fiyat, tahmini_deger))
        
        conn.commit()
        conn.close()
        
        self.islem_modu_sifirla()
        self.load_data()

    def hurda_satisi_tamamla(self):
        if not self.secili_hurda_id:
            return
            
        satis_fiyati_str = self.entry_satis_fiyati.get().strip()
        try:
            satis_fiyati = float(satis_fiyati_str)
        except ValueError:
            return
            
        conn = self.db.connect()
        cursor = conn.cursor()
        
        # Satış değerini güncelle ve durumu 'Satıldı' yap
        yeni_toplam_deger = self.secili_hurda_veri["fire_miktari"] * satis_fiyati
        cursor.execute("""
            UPDATE hurda_hareketleri 
            SET durum = 'Satıldı', hurda_birim_fiyati = ?, tahmini_hurda_degeri = ?
            WHERE id = ? AND kullanici_id = ?
        """, (satis_fiyati, yeni_toplam_deger, self.secili_hurda_id, self.current_user["id"]))
        
        conn.commit()
        conn.close()
        
        self.islem_modu_sifirla()
        self.load_data()

    def apply_theme(self):
        self.configure(fg_color=Renkler.BG_LIGHT)
        try:
            self.left_card.configure(fg_color=Renkler.CARD_BG)
            self.right_card.configure(fg_color=Renkler.CARD_BG)
        except Exception:
            pass
        self._needs_refresh = True
