import os
import posixpath
from uuid import uuid4

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models
from django.db.models.signals import (
    post_delete,  # 🚀 匯入訊號
    post_save,
)
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from django.utils.timezone import now

# 🚀 寫在 models.py 的最上方
# 🚀 物理向後退一層，到 aquatic/ 底下抓 constants
from ..constants import (
    AQUATIC_CATEGORIES,
    CITY_CHOICES,
    DEFAULT_CATEGORY,
    TAIWAN_CITIES,
    TAIWAN_REGIONS,
)

# 匯入你專案內部的工具與基底
from ..utils import handle_model_image_upload, purge_cloudflare_cache
from .base import BaseModel


def get_aquatic_upload_path(instance, filename):
    """🚀 萬用路徑：保留原本 UUID 架構，透過副檔名物理分流圖片與影片"""
    date_str = now().strftime("%Y/%m/%d")

    # 🎯 核心因果：物理抽出副檔名 (例如 webp, mp4, webm)
    ext = filename.split(".")[-1].lower()

    if (
        getattr(instance, "__class__", None)
        and instance.__class__.__name__ == "AquaticLife"
    ):
        owner_id = instance.owner.id
        category = instance.category

        # 繼承商品 UUID，鎖定在同一個資料夾
        token = (
            instance.folder_uuid
            if hasattr(instance, "folder_uuid") and instance.folder_uuid
            else uuid4().hex[:8]
        )

        # 🎯 因果分流閘門：看副檔名決定資料夾與檔名
        if ext in ["mp4", "webm", "mov", "avi"]:
            sub_folder = "video"
            file_name = f"main.{ext}"  # 影片就叫 main.mp4
        else:
            sub_folder = "cover"
            file_name = f"main.{ext}"  # 圖片通常經過壓縮會是 main.webp

    else:
        owner_id = instance.product.owner.id
        category = instance.product.category
        token = (
            instance.product.folder_uuid
            if hasattr(instance.product, "folder_uuid") and instance.product.folder_uuid
            else uuid4().hex[:8]
        )
        sub_folder = "gallery"
        # 副圖避免覆蓋，加上隨機碼
        file_name = f"{uuid4().hex[:8]}.{ext}"

    return posixpath.join(
        "aquatic", str(owner_id), category, date_str, token, sub_folder, file_name
    )


class AquaticLife(BaseModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="aquatic_items",
        verbose_name="發布者",
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="是否上架",
    )

    name = models.CharField(
        max_length=100,
        verbose_name="品種名稱",
    )

    # 種類維持必填，不需要修改
    category = models.CharField(
        max_length=10,
        choices=AQUATIC_CATEGORIES,
        default=DEFAULT_CATEGORY,
        verbose_name="產品種類",
    )

    city = models.CharField(
        max_length=50,
        choices=CITY_CHOICES,
        default="NONE",
        verbose_name="所在地點",
    )

    price = models.IntegerField(
        default=0,
        verbose_name="價格",
    )

    video = models.FileField(
        upload_to=get_aquatic_upload_path,
        null=True,
        blank=True,
        verbose_name="商品影片(MP4/WebM)",
    )

    # =========================================================
    # 新版簡化規格
    # =========================================================

    # 使用文字欄位，不強迫拆成最低與最高溫度。
    # 可以輸入：
    # 24～28°C
    # 24°C
    # 室溫即可
    temp = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="適合溫度",
    )

    # 使用文字欄位，允許描述目前體長或成魚體長。
    # 可以輸入：
    # 約 3 cm
    # 4～5 cm
    # 成魚約 8 cm
    body_length = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="體長",
    )

    # =========================================================
    # 舊版規格欄位
    # 暫時保留，等待資料轉移完成後才刪除
    # =========================================================

    ph_min = models.FloatField(
        null=True,
        blank=True,
        verbose_name="最小pH值",
    )

    ph_max = models.FloatField(
        null=True,
        blank=True,
        verbose_name="最大pH值",
    )

    temp_min = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="最小溫度",
    )

    temp_max = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="最大溫度",
    )

    adult_length = models.FloatField(
        null=True,
        blank=True,
        verbose_name="成魚體長(cm)",
    )

    min_tank_size = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="建議水量(L)",
    )

    specs_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="其他詳細規格",
    )

    notice_template = models.ForeignKey(
        "ShopNotice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name="套用的購物須知",
    )

    stock = models.IntegerField(
        default=0,
        verbose_name="庫存數量",
    )

    description = models.TextField(
        blank=True,
        verbose_name="詳細描述",
    )

    image = models.ImageField(
        upload_to=get_aquatic_upload_path,
        null=True,
        blank=True,
        verbose_name="商品封面圖",
    )

    @property
    def show_cover(self):
        if self.image:
            return mark_safe(
                f'<img src="{self.image.url}" width="100" '
                'style="border-radius: 5px;" />'
            )
        return "無首圖"

    def _sync_owner_city(self):
        """自動與發布者 Profile 的地址同步。"""
        if not (self.owner and hasattr(self.owner, "profile")):
            self.city = "NONE"
            return

        user_address = self.owner.profile.city_region

        if not user_address:
            self.city = "NONE"
            return

        matched_city_name = next(
            (city for city in TAIWAN_CITIES if city in user_address),
            None,
        )

        self.city = matched_city_name or "NONE"

    def _handle_category_media_move(self):
        """分類變更時，將舊圖片與影片移到新分類路徑。"""
        if not self.pk:
            return

        try:
            old_instance = AquaticLife.objects.get(pk=self.pk)

            if old_instance.category == self.category:
                return

            media_fields = ["image", "video"]

            for field in media_fields:
                old_media = getattr(old_instance, field)
                current_media = getattr(self, field)

                if old_media and old_media.name and current_media:
                    old_path = old_media.name.replace("\\", "/")
                    new_path = get_aquatic_upload_path(
                        self,
                        os.path.basename(old_path),
                    )

                    if default_storage.exists(old_path) and old_path != new_path:
                        with default_storage.open(old_path) as file_obj:
                            default_storage.save(new_path, file_obj)

                        default_storage.delete(old_path)
                        current_media.name = new_path

                        print(f"媒體搬移成功 ({field}): " f"{old_path} -> {new_path}")

        except Exception as error:
            print(f"媒體搬移失敗：{error}")

    def save(self, *args, **kwargs):
        self._sync_owner_city()
        self._handle_category_media_move()

        handle_model_image_upload(self, "image")

        super().save(*args, **kwargs)

        cache_urls = []

        if self.image:
            cache_urls.append(self.image.url)

        if self.video:
            cache_urls.append(self.video.url)

        if cache_urls:
            purge_cloudflare_cache(cache_urls)

    def __str__(self):
        return f"[{self.get_city_display()}] {self.name}"


@receiver(post_delete, sender=AquaticLife)
def purge_aquatic_life_cache(sender, instance, **kwargs):
    """因果：商品主體被刪 -> 驅逐 Cloudflare 封面圖快取"""
    try:
        if instance.image and hasattr(instance.image, "url") and instance.image.url:
            purge_cloudflare_cache([instance.image.url])
            print("🧹 Cloudflare 封面圖快取清除成功")
    except Exception as e:
        print(f"⚠️ 封面圖快取清除失敗: {e}")


# 你的儲存路徑aquatic/{使用者ID}/{生物分類}/{年/月/日}/{隨機字串}/{主圖或副圖}/main.webp


# 🚀 1. 物理引入你就在隔壁資料夾的 Profile（同一個 package，用相對路徑最穩）
from .profile import Profile


@receiver(
    post_save, sender=Profile
)  # 🎯 監聽：直接吃實體 Profile 類別，100% 不可能再跳電說找不到 App
@receiver(post_save, sender=Profile)
def sync_all_aquatic_location_on_profile_change(sender, instance, **kwargs):
    if not hasattr(instance, "user") or not instance.user:
        return

    user = instance.user
    user_address_string = instance.city_region

    new_city_code = "NONE"
    if user_address_string:
        matched_city_name = None
        for city_name in TAIWAN_REGIONS.keys():
            if city_name in user_address_string:
                matched_city_name = city_name
                break

        if matched_city_name:
            for code, name in CITY_CHOICES:
                if name == matched_city_name:
                    new_city_code = code
                    break

    # 🎯 大轟炸直接精簡成一行：只更新大方向縣市代碼，完全不碰 specs_json
    AquaticLife.objects.filter(owner=user).update(city=new_city_code)
    print(
        f"⚡ [信號同步通電] 已將用戶 {user.username} 名下小魚地點同步為: {new_city_code}"
    )
