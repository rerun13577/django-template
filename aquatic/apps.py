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
        # 🚀 這是靈魂！這行沒寫，signals.py 就是一張廢紙
        pass
