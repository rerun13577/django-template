# aquatic/models/shop_notice.py
from django.contrib.auth.models import User
from django.db import models


class ShopNotice(models.Model):
    """店長碎碎念：存 SOP 或規則用的模板"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notices")
    title = models.CharField(max_length=200, verbose_name="模板標題")
    content = models.TextField(verbose_name="教學內容")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"
