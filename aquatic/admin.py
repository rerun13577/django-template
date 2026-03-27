from django.contrib import admin

# aquatic/admin.py
from .models import AquaticImage, AquaticLife, Comment, Post, Profile

# 1. 簡單的直接登記
admin.site.register(Comment)
# 🚀 2. 把零件註冊到儀表板
admin.site.register(Profile)


# 🌟 進階技巧：讓副圖可以「內嵌」在商品頁面上傳
class AquaticImageInline(admin.TabularInline):
    model = AquaticImage
    extra = 1  # 預設多出一個空白上傳框
    readonly_fields = ["show_gallery_image"]  # 讓你在上傳後能看到縮圖
    fields = ["image", "show_gallery_image"]  # 決定要顯示哪些欄位


@admin.register(AquaticLife)
class AquaticLifeAdmin(admin.ModelAdmin):
    show_full_result_count = False  # 🚀 讓 Django 不要每次都精確計算總數

    # 1. 列表頁要顯示哪些欄位 (把 show_cover 放第一格)
    list_display = [
        "show_cover",
        "name",
        "category",
        "city",
        "price",
        "stock",
        "created_at",
    ]

    # 2. 點擊哪些欄位可以進入編輯頁
    list_display_links = ["show_cover", "name"]

    # 3. 右側過濾器
    list_filter = ["category", "city", "created_at"]

    # 4. 搜尋欄位 (支援搜尋品種名稱)
    search_fields = ["name"]

    # 5. 🚀 關鍵：把副圖的 Inline 加進來
    # 這樣你點進一隻魚的編輯頁，下方就會直接出現它的寫真集上傳區
    inlines = [AquaticImageInline]


# 如果你也想單獨管理副圖 (雖然有了 Inline 通常不需要)
@admin.register(AquaticImage)
class AquaticImageAdmin(admin.ModelAdmin):
    list_display = ["show_gallery_image", "product", "created_at"]
    list_display_links = ["show_gallery_image"]
    raw_id_fields = ["product"]  # 方便在大量商品中選擇


# 2. 需要「特異功能」的用這個寫法
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_select_related = ("author",)  # 🚀 預先抓好作者，不要一筆一筆抓
    # 🚀 這一行是解決轉圈圈的神藥
    raw_id_fields = ("likes", "author")

    # 加這行可以讓你一眼看到誰是作者
    list_display = ("title", "author", "created_at")
