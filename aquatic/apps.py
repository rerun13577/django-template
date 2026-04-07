# from django.apps import AppConfig


# class AquaticConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "aquatic"

#     def ready(self):
#         # 🚀 這一行是啟動「自動刪除 R2 圖片」監聽器的關鍵
#         pass

from django.apps import AppConfig


class AquaticConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "aquatic"

    def ready(self):
        # 🚀 必須要在這裡手動 import，監聽器才會在 Django 啟動時生效
        import aquatic.signals  # noqa
