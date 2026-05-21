DIL = "tr"

METINLER = {
    "tr": {
        "app_title": "Atölye Kar-Zarar ve Teklif Yönetim Sistemi",
        "login_title": "Sisteme Giriş",
        "username": "Kullanıcı Adı",
        "password": "Şifre",
        "login_btn": "Giriş Yap",
        "login_error_empty": "Lütfen kullanıcı adı ve şifreyi doldurun.",
        "login_error_invalid": "Kullanıcı adı veya şifre hatalı."
    },
    "en": {
        "app_title": "Workshop P&L and Quote Management System",
        "login_title": "System Login",
        "username": "Username",
        "password": "Password",
        "login_btn": "Login",
        "login_error_empty": "Please enter username and password.",
        "login_error_invalid": "Invalid username or password."
    },
    "ar": {
        "app_title": "نظام إدارة الورشة والأرباح",
        "login_title": "تسجيل الدخول للنظام",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "login_btn": "تسجيل الدخول",
        "login_error_empty": "الرجاء إدخال اسم المستخدم وكلمة المرور.",
        "login_error_invalid": "اسم المستخدم أو كلمة المرور غير صحيحة."
    }
}

def t(anahtar):
    """Aktif dile göre metni döndürür."""
    return METINLER.get(DIL, {}).get(anahtar, anahtar)
