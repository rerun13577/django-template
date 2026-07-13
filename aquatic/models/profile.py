import posixpath

from django.contrib.auth.models import User
from django.db import models

from aquatic.constants import PRICE_VISIBILITY_CHOICES

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

    # 🚀 新增：LINE 連結欄位
    contact_link = models.URLField(max_length=200, blank=True, verbose_name="聯絡連結")

    # 🚀 新增：價格防護罩總開關 (預設 False：不隱藏，大家都能看)
    price_visibility = models.CharField(
        max_length=20,
        choices=PRICE_VISIBILITY_CHOICES,
        default="PUBLIC",
        verbose_name="價格顯示方式",
    )

    # 1. 紀錄誰追蹤了他 (關聯到 User 表)
    followers = models.ManyToManyField(
        User, related_name="following_profiles", blank=True, verbose_name="追蹤者名單"
    )
    # 2. 獨立的數字快取欄位 (避免每次都要 count() 拖慢效能)
    follower_count = models.PositiveIntegerField(default=0, verbose_name="追蹤總數")

    def save(self, *args, **kwargs):
        print("\n[防線 1] 🟢 進入 models.py 的 Profile.save() 準備儲存！")

        # 🚀 引入上傳檔案的標準型別，用來做絕對精準的判定
        from django.core.files.uploadedfile import UploadedFile

        has_new_avatar = False
        has_new_background = False

        # 1. 檢查大頭貼
        if self.avatar and hasattr(self.avatar, "file"):
            # 🎯 物理透視：直接檢查內部的 .file 是不是剛上傳的 UploadedFile
            if isinstance(self.avatar.file, UploadedFile):
                has_new_avatar = True

        # 2. 檢查背景圖
        print(f"[防線 2] 檢查背景圖狀態: {self.background_image}")
        if self.background_image and hasattr(self.background_image, "file"):
            # 🎯 物理透視：直接看裡面！
            if isinstance(self.background_image.file, UploadedFile):
                has_new_background = True
                print(
                    "[防線 3] 🎯 破除外殼！確認內部是 UploadedFile，判定為【全新背景圖】！"
                )
            else:
                print("[防線 3] ⛔ 內部不是 UploadedFile，判定為【舊圖】。")

        # 3. 處理新大頭貼
        if has_new_avatar:
            # 🚀 修正順序：先讓 utils 轉檔（這樣它才看得到原始副檔名）
            handle_model_image_upload(self, "avatar")
            # 轉檔完畢，強制上制服
            self.avatar.name = "avatar.webp"
            if self.avatar and hasattr(self.avatar, "name"):
                self.avatar.name = get_profile_upload_path(self, "avatar.webp")

        # 4. 處理新背景圖
        if has_new_background:
            print("[防線 4] 🚀 放行！正式發射訊號給 utils.py 進行轉檔！")
            # 🚀 修正順序：先讓 utils 轉檔
            handle_model_image_upload(self, "background_image")
            # 轉檔完畢，強制上制服
            self.background_image.name = "background_image.webp"
            if self.background_image and hasattr(self.background_image, "name"):
                self.background_image.name = get_profile_upload_path(
                    self, "background_image.webp"
                )

        # 5. 正式落庫
        super().save(*args, **kwargs)
        print("[防線 5] 💾 資料庫儲存完畢。")

        # 6. 沖刷快取
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
            print("[防線 6] 🧹 快取清除訊號已發送。")

    def __str__(self):
        return f"{self.user.username} 的個人檔案"
