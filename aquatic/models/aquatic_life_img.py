import os
import posixpath
from uuid import uuid4

from django.conf import settings  # 🚀 記得引入 settings
from django.core.files.storage import default_storage
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from ..utils import handle_model_image_upload, purge_cloudflare_cache
from .base import BaseModel


def get_aquatic_upload_path(instance, filename):
    """🚀 萬用路徑：現在加入了 User ID 作為第一層目錄"""
    date_str = now().strftime("%Y/%m/%d")

    # 1. 取得 owner_id (處理 AquaticLife 或 AquaticImage 兩種情況)
    if isinstance(instance, AquaticLife):
        owner_id = instance.owner.id
        category = instance.category
        sub_folder = "cover"
    else:
        # 這是副圖 AquaticImage，要從 product 往回找 owner
        owner_id = instance.product.owner.id
        category = instance.product.category
        sub_folder = "gallery"

    token = (
        instance.folder_uuid if hasattr(instance, "folder_uuid") else uuid4().hex[:8]
    )

    # 🚀 新路徑：aquatic/{user_id}/{category}/{date}/...
    return posixpath.join(
        "aquatic", str(owner_id), category, date_str, token, sub_folder, "main.webp"
    )


class AquaticLife(BaseModel):
    # --- 原本的 CHOICES 區 (保持原樣，這部分很長但很清楚) ---
    CITY_CHOICES = [
        ("KLU", "基隆市"),
        ("TP", "臺北市"),
        ("NTP", "新北市"),
        ("TY", "桃園市"),
        ("HCU", "新竹市"),
        ("HCH", "新竹縣"),
        ("ILN", "宜蘭縣"),
        ("MLI", "苗栗縣"),
        ("TC", "臺中市"),
        ("CHH", "彰化縣"),
        ("NTO", "南投縣"),
        ("YLN", "雲林縣"),
        ("CYI", "嘉義市"),
        ("CYH", "嘉義縣"),
        ("TN", "臺南市"),
        ("KH", "高雄市"),
        ("PTH", "屏東縣"),
        ("HUA", "花蓮縣"),
        ("TTT", "臺東縣"),
        ("PEH", "澎湖縣"),
        ("KMN", "金門縣"),
        ("LJN", "連江縣"),
    ]

    CATEGORY_CHOICES = [
        ("SHRIMP", "米蝦/螯蝦"),
        ("FISH", "觀賞魚"),
        ("PLANT", "水生植物"),
        ("OTHER", "其他"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="aquatic_items",
        verbose_name="發布者",
        null=True,
        blank=True,
    )
    PRICE_STATUS_CHOICES = [("NORMAL", "正常顯示價格"), ("NOT_FOR_SALE", "非賣品")]

    # --- 欄位定義 ---
    name = models.CharField(max_length=100, verbose_name="品種名稱")
    category = models.CharField(
        max_length=10, choices=CATEGORY_CHOICES, default="SHRIMP", verbose_name="分類"
    )
    city = models.CharField(
        max_length=5, choices=CITY_CHOICES, default="NTP", verbose_name="所在地點"
    )
    price = models.IntegerField(default=0, verbose_name="價格")
    price_status = models.CharField(
        max_length=20,
        choices=PRICE_STATUS_CHOICES,
        default="NORMAL",
        verbose_name="價格狀態",
    )
    stock = models.IntegerField(default=0, verbose_name="庫存數量")
    description = models.TextField(blank=True, verbose_name="詳細描述")
    image = models.ImageField(
        upload_to=get_aquatic_upload_path,
        null=True,
        blank=True,
        verbose_name="商品封面圖",
    )

    # --- 小工具 ---
    def get_display_price(self):
        if self.price_status == "NOT_FOR_SALE":
            return "無價珍寶"
        return f"NT$ {self.price}"

    @property
    def show_cover(self):
        if self.image:
            return mark_safe(
                f'<img src="{self.image.url}" width="100" style="border-radius: 5px;" />'
            )
        return "無首圖"

    # --- 核心 Save 邏輯 ---
    def save(self, *args, **kwargs):
        # 1. 搬家邏輯：如果分類變了，自動把舊照片搬到新分類資料夾
        if self.pk:
            try:
                old_instance = AquaticLife.objects.get(pk=self.pk)
                if old_instance.category != self.category and self.image:
                    old_path = self.image.name.replace("\\", "/")
                    new_path = get_aquatic_upload_path(self, os.path.basename(old_path))
                    if default_storage.exists(old_path) and old_path != new_path:
                        with default_storage.open(old_path) as f:
                            default_storage.save(new_path, f)
                        default_storage.delete(old_path)
                        self.image.name = new_path
                        print(f"🚚 搬家成功: {old_path} -> {new_path}")
            except Exception as e:
                print(f"⚠️ 搬家失敗預警: {e}")

        # 2. 壓縮轉檔
        handle_model_image_upload(self, "image")

        # 3. 呼叫 BaseModel 的 save (它會處理 UUID 並執行真正的存檔)
        super().save(*args, **kwargs)

        # 4. 清除快取
        if self.image:
            purge_cloudflare_cache([self.image.url])

    def __str__(self):
        return f"[{self.get_city_display()}] {self.name}"


class AquaticImage(models.Model):
    """副圖模型：連結主商品"""

    product = models.ForeignKey(
        AquaticLife, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to=get_aquatic_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def show_gallery_image(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="100" />')
        return "無圖片"

    def save(self, *args, **kwargs):
        handle_model_image_upload(self, "image")
        super().save(*args, **kwargs)
