from django.contrib import admin

from .models import (
    AquaticLife,
    Comment,
    Post,
    Profile,
    ShopNotice,
)

# 留言管理
admin.site.register(Comment)


# 個人檔案管理
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "nickname",
        "folder_uuid",
        "created_at",
    ]

    search_fields = [
        "user__username",
        "nickname",
        "folder_uuid",
    ]

    readonly_fields = ["folder_uuid"]


# 水族商品管理
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
        "is_active",
        "created_at",
    ]

    list_display_links = [
        "show_cover",
        "name",
    ]

    list_filter = [
        "category",
        "city",
        "is_active",
        "created_at",
    ]

    search_fields = [
        "name",
        "owner__username",
        "folder_uuid",
    ]

    raw_id_fields = ["owner"]


# 常用備註庫
@admin.register(ShopNotice)
class ShopNoticeAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "user",
        "created_at",
    ]

    search_fields = [
        "title",
        "content",
        "user__username",
    ]

    raw_id_fields = ["user"]


# 文章管理
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_select_related = ("author",)

    raw_id_fields = (
        "likes",
        "author",
    )

    list_display = (
        "title",
        "author",
        "comment_count",
        "like_count",
        "created_at",
    )
