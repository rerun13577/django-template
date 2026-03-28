import posixpath

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from ..utils import handle_model_image_upload
from .base import BaseModel


def get_pet_upload_path(instance, filename):
    """🚀 寵物魚專屬路徑：profiles/UUID/pets/main.webp"""
    token = instance.folder_uuid
    return posixpath.join("profiles", token, "pets", "main.webp")


class PetFish(BaseModel):
    # 🚀 歸屬：這隻魚是誰養的
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_pets")

    # 🚀 基礎資訊
    name = models.CharField(max_length=50, verbose_name="小魚名字")
    species = models.CharField(max_length=100, blank=True, verbose_name="品種(選填)")
    main_photo = models.ImageField(
        upload_to=get_pet_upload_path, verbose_name="展示美照"
    )
    bio = models.TextField(blank=True, verbose_name="關於牠的故事")

    # 🚀 電子雞互動核心
    # 紀錄最後一次被戳（餵食）的時間
    last_feeding_time = models.DateTimeField(
        null=True, blank=True, verbose_name="最後餵食時間"
    )
    # 設定這隻魚多久要餵一次 (預設 24 小時)
    feeding_interval_hours = models.PositiveIntegerField(
        default=24, verbose_name="建議餵食間隔(小時)"
    )
    # 紀錄這隻魚被全站網友「敲碗」了幾次
    feeding_count = models.PositiveIntegerField(
        default=0, verbose_name="累計被餵食次數"
    )

    # 🚀 飢餓偵測小工具 (給前端 Template 用的)
    @property
    def is_hungry(self):
        if not self.last_feeding_time:
            return True
        # 計算時間差：現在時間 - 上次餵食時間
        elapsed_time = now() - self.last_feeding_time
        # 如果超過了建議間隔，就代表牠餓了！
        return elapsed_time.total_seconds() > (self.feeding_interval_hours * 3600)

    def save(self, *args, **kwargs):
        # 1. 圖片改名 (為了讓 R2 路徑統一)
        if self.main_photo and hasattr(self.main_photo, "file"):
            self.main_photo.name = "pet_main.webp"

        # 2. 壓縮轉檔
        handle_model_image_upload(self, "main_photo")

        # 3. 呼叫 BaseModel 處理 UUID 並存檔
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.owner.username} 的心頭好：{self.name}"
