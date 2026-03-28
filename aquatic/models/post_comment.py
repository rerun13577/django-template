import posixpath

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.timezone import now

from ..utils import handle_model_image_upload
from .base import BaseModel


def get_blog_upload_path(instance, filename):
    """🚀 文章封面路徑：blog/日期/UUID/cover/cover.webp"""
    token = instance.folder_uuid
    date_str = now().strftime("%Y/%m/%d")
    return posixpath.join("blog", date_str, token, "cover", "cover.webp")


class Post(BaseModel):
    # 🚀 基礎資訊
    title = models.CharField(max_length=150, verbose_name="文章標題")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="作者")

    # 🚀 強大的內容區塊 (JSON 格式)
    content = models.JSONField(
        default=list, blank=True, null=True, help_text="儲存區塊資料的清單"
    )

    # 🚀 封面圖
    image = models.ImageField(
        upload_to=get_blog_upload_path, null=True, blank=True, verbose_name="文章封面"
    )

    # 🚀 數據統計
    like_count = models.IntegerField(default=0, verbose_name="點讚數")
    likes = models.ManyToManyField(User, blank=True, related_name="liked_posts")
    comment_count = models.IntegerField(default=0, verbose_name="留言數")

    def get_image_url(self):
        """預防圖片不在的 Safe URL"""
        if self.image and hasattr(self.image, "url"):
            return self.image.url
        return "https://media.fisshshop.com/media/default-photo/default-blog.webp"

    def get_absolute_url(self):
        """自動導向文章詳情頁"""
        return reverse("article", args=[str(self.id)])

    def save(self, *args, **kwargs):
        # 壓縮封面圖
        handle_model_image_upload(self, "image")
        # 呼叫繼承的 BaseModel 處理 UUID
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """留言模型：支援父子層回覆"""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(verbose_name="留言內容")

    # 🚀 數據統計
    like_count = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, blank=True, related_name="liked_comments")

    # 🚀 時間戳記 (留言不一定要 UUID，所以直接寫)
    created_at = models.DateTimeField(auto_now_add=True)

    # 🚀 [核心] 父層留言：用來實作「回覆」功能 (self 代表連結自己)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )

    class Meta:
        ordering = ["-created_at"]  # 最新留言排上面

    def __str__(self):
        return f"{self.author.username}: {self.content[:20]}"
