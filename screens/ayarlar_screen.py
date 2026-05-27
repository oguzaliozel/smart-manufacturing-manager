import customtkinter as ctk
from tema import Renkler, Fontlar
import database
import dil
from tkinter import messagebox

class AyarlarScreen(ctk.CTkFrame):
    def __init__(self, master, current_user):
        super().__init__(master, fg_color=Renkler.BG_LIGHT)
        self.current_user = current_user
        self.db = database.Database()
        self._needs_refresh = False
        
        self.create_widgets()

    def create_widgets(self):
        # ── ÜST BAŞLIK ALANI ──────────────────────────────────────────────────
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(30, 15))
        
        ctk.CTkLabel(
            self.header_frame, 
            text="Sistem Ayarları", 
            font=Fontlar.H1, 
            text_color=Renkler.TEXT_DARK
        ).pack(side="left")

        # Kaydet Butonu (Sabit Alt Panel)
        self.btn_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_panel.pack(side="bottom", fill="x", padx=30, pady=20)
        
        self.btn_save = ctk.CTkButton(
            self.btn_panel, 
            text="Tüm Ayarları Kaydet", 
            font=Fontlar.BODY_BOLD, 
            fg_color=Renkler.PRIMARY, 
            hover_color=Renkler.PRIMARY_HOVER, 
            height=45,
            command=self.save_settings
        )
        self.btn_save.pack(fill="x")

        # ── ANA İÇERİK ALANI (KART DÜZENİ - Geri kalan alan) ──────────────────
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=30, pady=0)

        # ── 1. KART: PROFİL BİLGİLERİ ─────────────────────────────────────────
        self.profile_card = ctk.CTkFrame(self.scroll_container, fg_color=Renkler.CARD_BG, corner_radius=10)
        self.profile_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(self.profile_card, text="Profil Bilgileri", font=Fontlar.H3, text_color=Renkler.PRIMARY).pack(anchor="w", padx=20, pady=(15, 10))
        
        self.entry_name = self.create_input_row(self.profile_card, "Ad Soyad:")
        self.entry_name.insert(0, self.current_user.get("ad_soyad") or "")
        
        self.entry_username = self.create_input_row(self.profile_card, "Kullanıcı Adı:")
        self.entry_username.insert(0, self.current_user.get("kullanici_adi") or "")
        
        # ── 2. KART: ŞİFRE DEĞİŞTİR ───────────────────────────────────────────
        self.password_card = ctk.CTkFrame(self.scroll_container, fg_color=Renkler.CARD_BG, corner_radius=10)
        self.password_card.pack(fill="x", pady=15)
        
        ctk.CTkLabel(self.password_card, text="Güvenlik ve Şifre", font=Fontlar.H3, text_color=Renkler.PRIMARY).pack(anchor="w", padx=20, pady=(15, 10))
        
        self.entry_old_pwd = self.create_input_row(self.password_card, "Mevcut Şifre:", show="*")
        self.entry_new_pwd = self.create_input_row(self.password_card, "Yeni Şifre:", show="*")
        self.entry_new_pwd_confirm = self.create_input_row(self.password_card, "Yeni Şifre (Tekrar):", show="*")
        
        # ── 3. KART: TERCİHLER ─────────────────────────────────────────────────
        self.pref_card = ctk.CTkFrame(self.scroll_container, fg_color=Renkler.CARD_BG, corner_radius=10)
        self.pref_card.pack(fill="x", pady=15)
        
        ctk.CTkLabel(self.pref_card, text="Görünüm ve Tercihler", font=Fontlar.H3, text_color=Renkler.PRIMARY).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Tema Tercihi
        row_theme = ctk.CTkFrame(self.pref_card, fg_color="transparent")
        row_theme.pack(fill="x", padx=20, pady=8)
        ctk.CTkLabel(row_theme, text="Görünüm Teması:", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_DARK, width=150, anchor="w").pack(side="left")
        
        self.combo_theme = ctk.CTkComboBox(row_theme, values=["Açık", "Koyu"], font=Fontlar.SMALL, height=35)
        self.combo_theme.pack(side="left", fill="x", expand=True)
        self.combo_theme.set(self.current_user.get("tema") or "Açık")
        
        # Dil Tercihi
        row_lang = ctk.CTkFrame(self.pref_card, fg_color="transparent")
        row_lang.pack(fill="x", padx=20, pady=8)
        ctk.CTkLabel(row_lang, text="Sistem Dili:", font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_DARK, width=150, anchor="w").pack(side="left")
        
        self.combo_lang = ctk.CTkComboBox(row_lang, values=["Türkçe (tr)", "English (en)"], font=Fontlar.SMALL, height=35)
        self.combo_lang.pack(side="left", fill="x", expand=True)
        self.combo_lang.set("Türkçe (tr)" if self.current_user.get("dil") == "tr" else "English (en)")

    def create_input_row(self, parent, label_text, show=None):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=8)
        
        ctk.CTkLabel(row, text=label_text, font=Fontlar.BODY_BOLD, text_color=Renkler.TEXT_DARK, width=150, anchor="w").pack(side="left")
        entry = ctk.CTkEntry(row, font=Fontlar.SMALL, height=35, show=show)
        entry.pack(side="left", fill="x", expand=True)
        return entry

    def save_settings(self):
        ad_soyad = self.entry_name.get().strip()
        k_adi = self.entry_username.get().strip()
        
        old_pwd = self.entry_old_pwd.get().strip()
        new_pwd = self.entry_new_pwd.get().strip()
        new_pwd_confirm = self.entry_new_pwd_confirm.get().strip()
        
        tema_val = self.combo_theme.get()
        dil_val = "tr" if "Türkçe" in self.combo_lang.get() else "en"
        
        if not ad_soyad or not k_adi:
            messagebox.showwarning("Uyarı", "Lütfen Ad Soyad ve Kullanıcı Adı alanlarını doldurun.")
            return
            
        conn = self.db.connect()
        cursor = conn.cursor()
        
        # Şifre Değişimi Kontrolü
        if old_pwd or new_pwd or new_pwd_confirm:
            # Önce mevcut şifrenin doğruluğunu kontrol et
            cursor.execute("SELECT sifre FROM kullanicilar WHERE id = ?", (self.current_user["id"],))
            db_pwd = cursor.fetchone()["sifre"]
            
            if old_pwd != db_pwd:
                messagebox.showerror("Hata", "Mevcut şifreniz yanlış.")
                conn.close()
                return
                
            if not new_pwd:
                messagebox.showwarning("Uyarı", "Lütfen yeni şifreyi girin.")
                conn.close()
                return
                
            if new_pwd != new_pwd_confirm:
                messagebox.showerror("Hata", "Yeni şifreler uyuşmuyor.")
                conn.close()
                return
                
            # Şifreyi de güncelle
            sifre_sql = ", sifre = ?"
            sifre_param = [new_pwd]
        else:
            sifre_sql = ""
            sifre_param = []
            
        try:
            query = f"""
                UPDATE kullanicilar 
                SET ad_soyad = ?, kullanici_adi = ?, tema = ?, dil = ? {sifre_sql}
                WHERE id = ?
            """
            params = [ad_soyad, k_adi, tema_val, dil_val] + sifre_param + [self.current_user["id"]]
            cursor.execute(query, params)
            conn.commit()
            
            # Lokal session güncelleme
            self.current_user["ad_soyad"] = ad_soyad
            self.current_user["kullanici_adi"] = k_adi
            self.current_user["tema"] = tema_val
            self.current_user["dil"] = dil_val
            if sifre_param:
                self.current_user["sifre"] = new_pwd
                
            # Tema uygulamasını güncelle
            if tema_val == "Koyu":
                ctk.set_appearance_mode("Dark")
            else:
                ctk.set_appearance_mode("Light")
                
            # Dil ayarlarını güncelle
            dil.DIL = dil_val
            
            # Sidebar ismini anlık güncelle
            if hasattr(self.master.master, "lbl_user"):
                self.master.master.lbl_user.configure(text=ad_soyad)
                
            messagebox.showinfo("Başarılı", "Ayarlar başarıyla kaydedildi ve uygulandı.")
            
            # Şifre alanlarını temizle
            self.entry_old_pwd.delete(0, "end")
            self.entry_new_pwd.delete(0, "end")
            self.entry_new_pwd_confirm.delete(0, "end")
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Hata", "Bu kullanıcı adı zaten başka bir kullanıcı tarafından kullanılıyor.")
        finally:
            conn.close()

    def apply_theme(self):
        self.configure(fg_color=Renkler.BG_LIGHT)
        self._needs_refresh = False
