import posixpath

from django.contrib.auth.models import User
from django.db import models

from ..utils import handle_model_image_upload, purge_cloudflare_cache
from .base import BaseModel


def get_profile_upload_path(instance, filename):
    """
    🎯 考慮最周全的路徑防線
    不論 filename 被外部壓縮工具改名成什麼（甚至變髒），我們直接用「刪去法」與「實體狀態」做精準判定
    """
    token = instance.folder_uuid
    sub_folder = "background"  # 預設走背景

    # 🥇 鋼鐵防禦：直接檢查 instance 當前的 avatar 欄位記憶體狀態
    # 如果檔名符合，或者當前 avatar 欄位內的檔案名稱與正要處理的 filename 相同，就進 avatar
    if (
        filename == "avatar.webp"
        or "avatar" in filename.lower()
        or (instance.avatar and instance.avatar.name == filename)
    ):
        sub_folder = "avatar"
    else:
        # 🥈 雙重防線：如果上述沒抓到，去判斷 background_image 是否有對上，沒對上且排除背景特徵才進 avatar
        # 這是為了防範有些萬用壓縮工具把兩個欄位的內部暫存名稱都改成一模一樣的 "main.webp"
        if instance.background_image and instance.background_image.name == filename:
            sub_folder = "background"

    # 🚀 固定輸出，絕不加上防衝突亂碼（配合 save 的清洗）
    return posixpath.join("profiles", token, sub_folder, "main.webp")


class Profile(BaseModel):
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

    city_region = models.CharField(max_length=50, blank=True, verbose_name="縣市行政區")
    address_detail = models.CharField(
        max_length=150, blank=True, verbose_name="詳細地址"
    )
    bio = models.TextField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        # 1. 偵測是否有真正的新檔案從前端進來（防止誤殺舊圖）
        has_new_avatar = False
        has_new_background = False

        if (
            self.avatar
            and hasattr(self.avatar, "file")
            and not isinstance(self.avatar, models.fields.files.FieldFile)
        ):
            has_new_avatar = True

        if (
            self.background_image
            and hasattr(self.background_image, "file")
            and not isinstance(self.background_image, models.fields.files.FieldFile)
        ):
            has_new_background = True

        # 2. 處理新大頭貼
        if has_new_avatar:
            self.avatar.name = "avatar.webp"  # 物理標記：打上 avatar 烙印
            handle_model_image_upload(self, "avatar")
            # 💡 核心拔除亂碼防線：萬一壓縮工具自作聰明改了名字或加上防重複後綴，
            # 我們在存入資料庫前，強行把它的欄位名稱洗回純淨的 "profiles/UUID/avatar/main.webp"
            # 這樣就能徹底截斷 Django 自動生成 main_xxxx.webp 的因果鏈結
            if self.avatar and hasattr(self.avatar, "name"):
                self.avatar.name = get_profile_upload_path(self, "avatar.webp")

        # 3. 處理新背景圖
        if has_new_background:
            self.background_image.name = "background_image.webp"  # 物理標記
            handle_model_image_upload(self, "background_image")
            if self.background_image and hasattr(self.background_image, "name"):
                self.background_image.name = get_profile_upload_path(
                    self, "background_image.webp"
                )

        # 4. 呼叫底層 BaseModel 正式落庫存檔入 R2
        super().save(*args, **kwargs)

        # 5. 沖刷 Cloudflare CDN 快取
        purge_list = []
        if has_new_avatar and self.avatar and hasattr(self.avatar, "url"):
            purge_list.append(self.avatar.url)
        if (
            has_new_background
            and self.background_image
            and hasattr(self.background_image, "url")
        ):
            purge_list.append(self.background_image.url)

        if purge_list:
            purge_cloudflare_cache(purge_list)

    def __str__(self):
        return f"{self.user.username} 的個人檔案"
