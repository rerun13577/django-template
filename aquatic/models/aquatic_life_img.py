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
        # 如果你未來還有保留副圖 (AquaticImage) 功能，這段邏輯依然能通電
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
    # --- 原本的 CHOICES 區 (保持原樣，這部分很長但很清楚) ---

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="aquatic_items",
        verbose_name="發布者",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        default=True, db_index=True, verbose_name="是否上架"
    )
    # PRICE_STATUS_CHOICES = [("NORMAL", "正常顯示價格"), ("NOT_FOR_SALE", "非賣品")]

    # --- 欄位定義 ---
    name = models.CharField(max_length=100, verbose_name="品種名稱")
    category = models.CharField(
        max_length=10,
        choices=AQUATIC_CATEGORIES,
        default=DEFAULT_CATEGORY,
        verbose_name="產品種類",
    )
    city = models.CharField(
        max_length=50,
        choices=CITY_CHOICES,
        default="NONE",  # 🚀 只要沒填，物理預設就是 "NONE"，絕對不給空
        # 🎯 物理砍掉 null=True 和 blank=True，斷絕任何變為 NULL 或空字串的因果可能
        verbose_name="所在地點",
    )
    price = models.IntegerField(default=0, verbose_name="價格")
    # price_status = models.CharField(
    #     max_length=20,
    #     choices=PRICE_STATUS_CHOICES,
    #     default="NORMAL",
    #     verbose_name="價格狀態",
    # )

    video = models.FileField(
        upload_to=get_aquatic_upload_path,  # 🚀 直接沿用你寫的超讚路徑機制
        null=True,
        blank=True,
        verbose_name="商品影片(MP4/WebM)",
    )

    # --- 核心 5 數據 (環境規格) ---
    ph_min = models.FloatField(null=True, blank=True, verbose_name="最小pH值")
    ph_max = models.FloatField(null=True, blank=True, verbose_name="最大pH值")
    temp_min = models.IntegerField(null=True, blank=True, verbose_name="最小溫度")
    temp_max = models.IntegerField(null=True, blank=True, verbose_name="最大溫度")
    adult_length = models.FloatField(null=True, blank=True, verbose_name="成魚體長(cm)")
    min_tank_size = models.IntegerField(
        null=True, blank=True, verbose_name="建議水量(L)"
    )

    # --- 擴充與附屬欄位 ---
    specs_json = models.JSONField(default=dict, blank=True, verbose_name="其他詳細規格")
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
    # def get_display_price(self):
    #     if self.price_status == "NOT_FOR_SALE":
    #         return "無價珍寶"
    #     return f"NT$ {self.price}"

    # 如果沒有寫跟有寫
    # 有寫product.sale_price()
    # 沒有寫self.price
    @property
    def show_cover(self):
        if self.image:
            return mark_safe(
                f'<img src="{self.image.url}" width="100" style="border-radius: 5px;" />'
            )
        return "無首圖"

    def _sync_owner_city(self):
        """自動與發布者的 Profile 地址進行行政區代碼同步（前端為 select 100% 精准）"""
        # 1. 安全攔截：沒 owner 或沒 profile 直接設為 NONE
        if not (self.owner and hasattr(self.owner, "profile")):
            self.city = "NONE"
            return

        user_address = self.owner.profile.city_region
        if not user_address:
            self.city = "NONE"
            return

        # 2. 核心比對：直接檢查 TAIWAN_CITIES 裡哪個縣市有在 user_address 裡面
        # 因為是 select 傳入，這行 next 跑出來的結果一定 100% 精準
        matched_city_name = next(
            (city for city in TAIWAN_CITIES if city in user_address), None
        )

        # 3. 寫入欄位：因為我們的 CITY_CHOICES 已經重構成 (city, city)，
        # 儲存值（Code）跟顯示名稱（Name）一模一樣（例如：("臺南市", "臺南市")）
        # 所以完全不需要再經過第二層 next 去查代碼，直接把 matched_city_name 塞給 self.city 就收工了！
        if matched_city_name:
            self.city = matched_city_name
        else:
            self.city = "NONE"

    def _handle_category_media_move(self):
        """當分類變更時，自動將舊圖片與影片搬移至新分類資料夾"""
        # 安全防線：如果是剛建立還沒存進資料庫 (沒有pk)，就不需要搬家
        if not self.pk:
            return

        try:
            old_instance = AquaticLife.objects.get(pk=self.pk)

            # 因：分類根本沒改。果：提早結束，節省伺服器效能
            if old_instance.category == self.category:
                return

            # 🚀 物理擴充：建立需要檢查搬家的媒體清單
            media_fields = ["image", "video"]

            for field in media_fields:
                old_media = getattr(old_instance, field)  # 抓出舊檔案實體
                current_media = getattr(self, field)  # 抓出當前(新)檔案實體

                # 如果這個欄位以前有檔案，而且現在也還有檔案，才進行搬家
                if old_media and old_media.name and current_media:
                    old_path = old_media.name.replace("\\", "/")
                    # 重新計算新分類底下的路徑
                    new_path = get_aquatic_upload_path(self, os.path.basename(old_path))

                    # 物理搬移與覆寫
                    if default_storage.exists(old_path) and old_path != new_path:
                        with default_storage.open(old_path) as f:
                            default_storage.save(new_path, f)
                        default_storage.delete(old_path)

                        # 讓當前的欄位指向新路徑
                        current_media.name = new_path
                        print(f"🚚 搬家成功 ({field}): {old_path} -> {new_path}")

        except Exception as e:
            print(f"⚠️ 媒體搬家失敗預警: {e}")

    # --- 核心 Save 邏輯 ---
    def save(self, *args, **kwargs):
        # 1. 🚀 鋼鐵防線：自動跟 owner 的 Profile 地址同步
        self._sync_owner_city()

        # 2. 🚀 媒體搬家：圖片與影片一起處理
        self._handle_category_media_move()

        # 3. 圖片壓縮轉檔 (保持原樣不動)
        handle_model_image_upload(self, "image")

        # 4. 真正寫入資料庫
        super().save(*args, **kwargs)

        # 5. 🚀 擴大快取打擊範圍：把有更新的圖片和影片網址都搜集起來，一次發給 Cloudflare 殺掉
        cache_urls = []
        if self.image:
            cache_urls.append(self.image.url)
        if self.video:
            cache_urls.append(self.video.url)

        if cache_urls:
            purge_cloudflare_cache(cache_urls)

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
