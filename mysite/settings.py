import os
from pathlib import Path

import pymysql

# 因為fb只能https 本地不能測試
# 🚀 只有在「非 Zeabur」環境（也就是本地端）才嘗試載入 .env
if os.getenv("ZEABUR") is None:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass


# --- 1. 基礎與數據庫修正 ---
pymysql.install_as_MySQLdb()
pymysql.version_info = (2, 2, 8, "final", 0)
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
)

# false 會導致靜態檔案不被讀取
DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["*"]

# --- 2. App 與 Middleware ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.line",
    "allauth.socialaccount.providers.facebook",
    "storages",
    "aquatic.apps.AquaticConfig",  # 👈 必須改成這樣，Signals 才會通電！
    "debug_toolbar",
    "django_cleanup.apps.CleanupConfig",  # 🚀 加上這行
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",  # 🚀 放在最前面
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # 必須在 Security 下方
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

# --- 3. 模板與路徑 (這部分沒設會直接 500) ---
ROOT_URLCONF = "mysite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --- 7. 第三方登入詳細設定 ---
SOCIALACCOUNT_PROVIDERS = {
    "line": {
        "SCOPE": ["profile", "openid", "email"],
    },
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    },
    "facebook": {
        "METHOD": "oauth2",
        "SCOPE": ["email", "public_profile"],
        "FIELDS": [
            "id",
            "email",
            "name",
            "first_name",
            "last_name",
            "picture.type(large)",  # 👈 這裡最重要！
        ],
        "VERIFIED_EMAIL": False,
    },
}

WSGI_APPLICATION = "mysite.wsgi.application"

# --- 4. 數據庫 ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MYSQLDATABASE"),
        "USER": os.getenv("MYSQLUSER"),
        "PASSWORD": os.getenv("MYSQLPASSWORD"),
        "HOST": os.getenv("MYSQLHOST"),
        "PORT": os.getenv("MYSQLPORT"),
    }
}


# --- 5. 雲端儲存與靜態檔案 (終極修正版) ---
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# 讀取 Zeabur 的變數
AWS_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "fissh-prod-media")
AWS_S3_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL")
R2_PUBLIC_DOMAIN = os.getenv("R2_PUBLIC_URL")

# 處理網域，確保乾淨
CLEAN_DOMAIN = (
    R2_PUBLIC_DOMAIN.replace("https://", "").replace("http://", "").rstrip("/")
)

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    # 🚀 使用 Django 4.2+ 最新的 STORAGES 寫法
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "access_key": AWS_ACCESS_KEY_ID,
                "secret_key": AWS_SECRET_ACCESS_KEY,
                "bucket_name": AWS_STORAGE_BUCKET_NAME,
                "endpoint_url": AWS_S3_ENDPOINT_URL,
                "region_name": "auto",
                "addressing_style": "path",
                "signature_version": "s3v4",  # 🚀 R2 必備
                "location": "media",
                "default_acl": None,  # 🚀 R2 不支援 ACL
                "file_overwrite": False,
                "custom_domain": CLEAN_DOMAIN,
                # 🚀 就是這兩行，加進去！
                "querystring_auth": False,  # 關閉簽名網址，直接用公開網址，速度提升 200%
                "file_overwrite": False,  # (你原本就有了，檢查一下)
            },
        },
        "staticfiles": {
            # 🚀 關鍵修正：去掉 "Manifest"，改回這個就不會報錯了
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }
    MEDIA_URL = f"https://{CLEAN_DOMAIN}/media/"
else:
    # 本地開發模式
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# --- 6. 其他關鍵設定 ---
SITE_ID = 4 if os.getenv("ZEABUR") else 2
CSRF_TRUSTED_ORIGINS = [
    "https://fisshshop.com",
    "https://*.zeabur.app",
    "https://*.ngrok-free.dev",
    "https://*.ngrok-free.app",
]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# 🚀 修正 2: 統一登入路徑與跳轉
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# 🚀 修正 3: Allauth 專業設定
ACCOUNT_LOGOUT_ON_GET = True  # 點擊登出連結直接登出
SOCIALACCOUNT_LOGIN_ON_GET = True  # 點擊 Google 登入直接跳轉

# 🚀 修正 5: 認證後端 (這塊一定要留著)
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]


# 通常是因為郵件模板裡有非 ASCII 字元才會導致編碼。
# 如果你希望它在終端機顯示純文字，可以試著在 settings.py 加上這行，強迫它用純文字發送：
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[FisshShop] "

# 語系設定
LANGUAGE_CODE = "zh-hant"
TIME_ZONE = "Asia/Taipei"
USE_I18N = True
USE_TZ = True


# mysite/settings.py

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp-relay.brevo.com"
EMAIL_PORT = 587
# Gmail 的「通訊協議標配」
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("MY_EMAIL")
EMAIL_HOST_PASSWORD = os.getenv("MY_EMAIL_PASSWORD")  # 👈 就是填這裡！

ACCOUNT_EMAIL_SUBJECT_PREFIX = "[FisshShop] "
# 這樣使用者收信時，就會看到寄件人是 FisshShop，而不是你的私人帳號# settings.py
# 🚀 這裡要寫死你的真實信箱，不能用抓到的變數（因為變數現在是 a5724...）
DEFAULT_FROM_EMAIL = "FisshShop <evonelin52@gmail.com>"

# 要不要驗證嗎
ACCOUNT_EMAIL_VERIFICATION = "none"


# 🚀 舊的 ACCOUNT_AUTHENTICATION_METHOD 等等可以刪掉了，改用這個：
ACCOUNT_LOGIN_METHODS = {"email", "username"}

# 🚀 統一設定註冊時需要的欄位
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*"]
