# aquatic/signals.py
from allauth.account.signals import user_signed_up
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

# 🚀 這裡要 import 你剛搬好家的 Profile
from .models.profile import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """當新用戶產生的瞬間，自動建立 Profile"""
    if created:
        Profile.objects.create(user=instance, nickname=instance.username)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """確保 User 存檔時，對應的 Profile 也會跟著存檔"""
    if hasattr(instance, "profile"):
        instance.profile.save()


@receiver(user_signed_up)
def send_welcome_email(request, user, **kwargs):
    """註冊成功發送歡迎信"""
    subject = "歡迎加入 FisshShop 魚缸！"
    message = f"嘿 {user.username}，你已成功註冊！快來分享你的蝦與魚吧。"
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    try:
        send_mail(subject, message, email_from, recipient_list)
    except Exception as e:
        print(f"⚠️ 郵件發送失敗: {e}")
