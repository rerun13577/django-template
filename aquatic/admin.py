from django.contrib import admin
from .models import AquaticLife, Post, Comment

# 1. 簡單的直接登記
admin.site.register(Comment)
admin.site.register(AquaticLife)

# 2. 需要「特異功能」的用這個寫法
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # 🚀 這一行是解決轉圈圈的神藥
    raw_id_fields = ('likes', 'author') 
    
    # 加這行可以讓你一眼看到誰是作者
    list_display = ('title', 'author', 'created_at')