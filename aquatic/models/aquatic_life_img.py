import os
import posixpath
from uuid import uuid4

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models
from django.db.models.signals import post_delete  # 🚀 匯入訊號
from django.dispatch import receiver  # 🚀 匯入接收器
from django.utils.safestring import mark_safe
from django.utils.timezone import now

# 匯入你專案內部的工具與基底
from ..utils import handle_model_image_upload, purge_cloudflare_cache
from .base import BaseModel


def get_aquatic_upload_path(instance, filename):
    """🚀 萬用路徑優化版：讓主圖與副圖落戶在同一個 Cloudflare 資料夾下"""
    date_str = now().strftime("%Y/%m/%d")

    if isinstance(instance, AquaticLife):
        owner_id = instance.owner.id
        category = instance.category
        sub_folder = "cover"
        # 主圖拿商品的 UUID
        token = (
            instance.folder_uuid
            if hasattr(instance, "folder_uuid")
            else uuid4().hex[:8]
        )
        file_name = "main.webp"  # 主圖固定叫 main.webp
    else:
        # 🚀 這是副圖 AquaticImage
        owner_id = instance.product.owner.id
        category = instance.product.category
        sub_folder = "gallery"
        # 🚀 因果補丁：副圖直接去搶它大哥(product)的 UUID！這樣在 Cloudflare 就會鎖在同一個資料夾
        token = (
            instance.product.folder_uuid
            if hasattr(instance.product, "folder_uuid")
            else uuid4().hex[:8]
        )
        # 🚀 因為都在同一個 gallery 資料夾下，檔名絕對不能再死掐 main.webp，否則後面的副圖會把前面的物理覆蓋！改用隨機碼
        file_name = f"{uuid4().hex[:8]}.webp"

    return posixpath.join(
        "aquatic", str(owner_id), category, date_str, token, sub_folder, file_name
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
        ("FISH", "魚類"),
        ("SHRIMP", "蝦類"),
        ("PLANT", "水生植物"),
        ("SHELLFISH", "螺蚌類"),
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
    is_active = models.BooleanField(
        default=True, db_index=True, verbose_name="是否有效"
    )
    PRICE_STATUS_CHOICES = [("NORMAL", "正常顯示價格"), ("NOT_FOR_SALE", "非賣品")]

    # --- 欄位定義 ---
    name = models.CharField(max_length=100, verbose_name="品種名稱")
    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        default="SHRIMP",
        verbose_name="產品種類",
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

    # 🚀 核心 5 數據 (固定欄位，純數字)
    # 1. pH值 (存範圍，搜尋更準)
    ph_min = models.FloatField(null=True, blank=True, verbose_name="最小pH值")
    ph_max = models.FloatField(null=True, blank=True, verbose_name="最大pH值")

    # 2. 適宜溫度
    temp_min = models.IntegerField(null=True, blank=True, verbose_name="最小溫度")
    temp_max = models.IntegerField(null=True, blank=True, verbose_name="最大溫度")

    # 3. 成魚體長 (cm)
    adult_length = models.FloatField(null=True, blank=True, verbose_name="成魚體長(cm)")

    # 4. 建議水量 (l)
    min_tank_size = models.IntegerField(
        null=True, blank=True, verbose_name="建議水量(L)"
    )

    # 🚀 剩下的 15 個雜項規格 (存 JSON)
    specs_json = models.JSONField(default=dict, blank=True, verbose_name="其他詳細規格")

    # 🚀 購物須知連結 (這就是你說的：改了全站都要變的東西)
    notice_template = models.ForeignKey(
        "ShopNotice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name="套用的購物須知",
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


@receiver(post_delete, sender=AquaticLife)
def purge_aquatic_life_cache(sender, instance, **kwargs):
    """因果：商品主體被刪 -> 驅逐 Cloudflare 封面圖快取"""
    try:
        if instance.image and hasattr(instance.image, "url") and instance.image.url:
            purge_cloudflare_cache([instance.image.url])
            print("🧹 Cloudflare 封面圖快取清除成功")
    except Exception as e:
        print(f"⚠️ 封面圖快取清除失敗: {e}")


@receiver(post_delete, sender=AquaticImage)
def purge_aquatic_gallery_cache(sender, instance, **kwargs):
    """因果：副圖被刪 (包含連帶刪除) -> 驅逐 Cloudflare 副圖快取"""
    try:
        if instance.image and hasattr(instance.image, "url") and instance.image.url:
            purge_cloudflare_cache([instance.image.url])
            print("🧹 Cloudflare 副圖藝廊快取清除成功")
    except Exception as e:
        print(f"⚠️ 副圖快取清除失敗: {e}")


# 你的儲存路徑aquatic/{使用者ID}/{生物分類}/{年/月/日}/{隨機字串}/{主圖或副圖}/main.webp
