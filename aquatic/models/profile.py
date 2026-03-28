import posixpath

from django.contrib.auth.models import User
from django.db import models

from ..utils import handle_model_image_upload, purge_cloudflare_cache
from .base import BaseModel  # 🚀 繼承你剛寫好的地基


def get_profile_upload_path(instance, filename):
    # UUID 已經由 BaseModel 搞定了，直接拿來用
    token = instance.folder_uuid
    sub_folder = "avatar" if "avatar" in filename else "background"
    return posixpath.join("profiles", token, sub_folder, "main.webp")


class Profile(BaseModel):
    # 🚀 一對一焊死 User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50, blank=True)

    avatar = models.ImageField(
        upload_to=get_profile_upload_path, null=True, blank=True, verbose_name="大頭貼"
    )
    background_image = models.ImageField(
        upload_to=get_profile_upload_path,
        null=True,
        blank=True,
        verbose_name="個人頁背景",
    )
    bio = models.TextField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        # 1. 圖片預處理改名（為了讓路徑函式抓到關鍵字）
        if self.avatar and hasattr(self.avatar, "file"):
            self.avatar.name = "avatar.webp"
        if self.background_image and hasattr(self.background_image, "file"):
            self.background_image.name = "background_image.webp"

        # 2. 執行萬用壓縮
        handle_model_image_upload(self, "avatar")
        handle_model_image_upload(self, "background_image")

        # 3. 呼叫老爸 (BaseModel) 的 save，它會幫你檢查 UUID 並正式存檔
        super().save(*args, **kwargs)

        # 4. 存完後清快取
        purge_list = [img.url for img in [self.avatar, self.background_image] if img]
        if purge_list:
            purge_cloudflare_cache(purge_list)

    def __str__(self):
        return f"{self.user.username} 的個人檔案"
