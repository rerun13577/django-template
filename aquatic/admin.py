from django.contrib import admin

from .models import (
    AquaticImage,
    AquaticLife,
    Comment,
    PetFish,
    Post,
    Profile,
    ShopNotice,
)

# 🚀 1. 簡單登記 (留言)
admin.site.register(Comment)


# 🚀 2. 個人檔案 (加上搜尋與列表優化)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "nickname", "folder_uuid", "created_at"]
    search_fields = ["user__username", "nickname", "folder_uuid"]
    readonly_fields = ["folder_uuid"]  # UUID 通常不給手改


# 🚀 3. 「副圖」零件：內嵌在商品頁面上傳
class AquaticImageInline(admin.TabularInline):
    model = AquaticImage
    extra = 1
    readonly_fields = ["show_gallery_image"]
    fields = ["image", "show_gallery_image"]


# 🚀 4. 水族商品管理 (你原本的專業寫法)
@admin.register(AquaticLife)
class AquaticLifeAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_display = [
        "show_cover",
        "name",
        "category",
        "city",
        "price",
        "stock",
        "created_at",
    ]
    list_display_links = ["show_cover", "name"]
    list_filter = ["category", "city", "created_at"]
    search_fields = ["name", "folder_uuid"]
    inlines = [AquaticImageInline]


# 🚀 5. 「電子雞」寵物魚管理
@admin.register(PetFish)
class PetFishAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "feeding_count", "is_hungry", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "owner__username"]
    raw_id_fields = ["owner"]  # 避免使用者太多時下拉選單跑不動
    # 🚀 在編輯頁面（你截圖這頁）顯示唯讀欄位
    readonly_fields = ["is_hungry"]


# 🚀 6. 「店長碎碎念」模板
@admin.register(ShopNotice)
class ShopNoticeAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "created_at"]
    search_fields = ["title", "content"]
    raw_id_fields = ["user"]


# 🚀 7. 文章管理 (保留你的 select_related 優化)
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_select_related = ("author",)
    raw_id_fields = ("likes", "author")
    list_display = ("title", "author", "comment_count", "like_count", "created_at")
