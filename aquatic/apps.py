from django.apps import AppConfig


class AquaticConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "aquatic"

    def ready(self):
        # 🚀 這一行是啟動「自動刪除 R2 圖片」監聽器的關鍵
        pass
