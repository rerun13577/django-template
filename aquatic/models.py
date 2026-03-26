import os
from io import BytesIO
from uuid import uuid4

from allauth.account.signals import user_signed_up
from django.conf import settings
from django.contrib.auth.models import User  # 引入內建的使用者模型
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

# 1. 先在檔案最上方加入這個引入
from django.urls import reverse
from django.utils.timezone import now
from PIL import Image

#


def compress_image(uploaded_image, threshold_kb=500):
    # 🚀 先檢查大小，沒超過門檻就直接回傳，省下處理時間
    # if uploaded_image.size <= threshold_kb * 1024:
    #     return uploaded_image

    # 🚀 加上這一行，這是你的「偵測雷達」
    print("📢 [DEBUG] 轉檔機器正式啟動！正在處理檔案:", uploaded_image.name)

    img = Image.open(uploaded_image)

    # 自動縮放尺寸 (寬度 1200px)
    max_width = 1200
    if img.width > max_width:
        new_height = int(img.height * (max_width / img.width))
        img = img.resize((max_width, new_height), Image.LANCZOS)

    # 轉成 RGB
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    elif img.mode != "RGB":
        img = img.convert("RGB")

    output = BytesIO()
    # 儲存為 WebP
    img.save(output, format="WEBP", quality=80)
    output.seek(0)

    # 修改副檔名為 .webp
    original_name = uploaded_image.name.rsplit(".", 1)[0]
    new_filename = f"{original_name}.webp"

    return InMemoryUploadedFile(
        output,
        "ImageField",
        new_filename,
        "image/webp",
        output.getbuffer().nbytes,
        None,
    )


# --- 資料庫模型放在下面 ---


# 可以輸入的資料型態 在後台顯示的模式
# CHOICES       定義下拉選單 後面會寫在charfield 後面的框框裡面
# CharField     必須限制長度 (max_length)。適合存短資訊，效能較快。
# TextField     不限長度
# IntegerField  可以輸入數字
# ImageField    可以上傳照片
# DateTimeField 後面通常會加 auto_now_add=True：，系統會自動幫你打卡。
# verbose_name (人看的) 資料庫顯示的名子 你可以改 且不會引響到其他檔案的引用
# blank=True：不填入也沒關西
# upload_to="aquatic_images/" 指定圖片存的地方 後面加照片名子。
# 這裡的 self 指的是「我現在正在存的這一筆資料」
# save不用屌他不知道就不知道
# __str__(self) 幫這筆資料取一個「人類看得懂」的名字 就是你在後台瀏覽小魚他標題名子


class AquaticLife(models.Model):
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

    name = models.CharField(max_length=100, verbose_name="品種名稱")
    category = models.CharField(
        max_length=10, choices=CATEGORY_CHOICES, default="SHRIMP", verbose_name="分類"
    )
    city = models.CharField(
        max_length=5, choices=CITY_CHOICES, default="NTP", verbose_name="所在地點"
    )
    price = models.IntegerField(default=0, verbose_name="價格")
    stock = models.IntegerField(default=0, verbose_name="庫存數量")
    description = models.TextField(blank=True, verbose_name="詳細描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="上架時間")
    image = models.ImageField(upload_to="aquatic_images/", null=True, blank=True)

    def save(self, *args, **kwargs):

        print("======== 📦 開始執行 Save 程序 ========")

        if self.image:
            # 🚀 2. 關鍵修正：檢查這是不是一個剛上傳的檔案物件
            # 只要是新上傳的，它一定是 UploadedFile 類型
            from django.core.files.uploadedfile import UploadedFile

            if isinstance(self.image.file, UploadedFile):
                print(f"📢 偵測到新上傳檔案: {self.image.name}，準備轉檔...")
                try:
                    self.image = compress_image(self.image, threshold_kb=500)
                    print("✅ 轉檔成功，檔名已更換為 .webp")
                except Exception as e:
                    print(f"❌ 轉檔發生錯誤: {e}")
            else:
                print("ℹ️ 這是一張舊圖，跳過轉檔程序。")

        super().save(*args, **kwargs)
        print("======== 🏁 Save 程序執行完畢 ========")

    def __str__(self):
        return f"[{self.get_city_display()}] {self.name}"


# JSONField 就是json 格式
# ForeignKey (外鍵：文章作者) author = models.ForeignKey(User, on_delete=models.CASCADE)
# 這是在做「連結」。它告訴 Django：「這篇文章是由哪個使用者寫的」。
# on_delete=models.CASCADE： 如果這個使用者把帳號刪了，他寫的所有文章也會跟著被自動刪除。
# ManyToManyField (多對多：按讚系統)
# 這是處理「多人對多物」的關係。一篇文章可以被很多人按讚，一個人也可以按很多篇文章讚。

# get_absolute_url (這啥？)
# 以後你在 HTML 模板裡，不需要手寫 /blog/detail/1/ 這種硬編碼。
# 你只要寫 {{ post.get_absolute_url }}，Django 就會自動幫你算出這篇文章正確的網址。

# 補充
# user.liked_posts.all() 瞬間抓出他這輩子按過讚的所有文章。
# related_name="comments"，Django 在執行程式時，會自動跑去 Post 那邊幫它補上一個隱藏屬性。
# 這裡的user 也是一樣概念


def get_blog_upload_path(instance, filename):
    # 🚀 保險絲邏輯：
    # 1. 先看資料庫有沒有存好的 UUID
    # 2. 如果沒有（舊文章），就現場生一個 8 位數亂碼
    token = instance.folder_uuid if instance.folder_uuid else uuid4().hex[:8]

    # 3. 順便把這組新生的 token 存回 instance 身上，
    # 這樣 save() 完之後，資料庫裡這篇舊文章就有 UUID 了！
    if not instance.folder_uuid:
        instance.folder_uuid = token

    date_str = now().strftime("%Y/%m/%d")
    return os.path.join("blog", date_str, token, "cover", "cover.webp")


# editable=False 不能顯示 也不能更改
class Post(models.Model):
    # 💡 建議：加一個隱藏欄位存 UUID，這樣 View 跟 Model 才能共用同一個資料夾
    folder_uuid = models.CharField(max_length=8, editable=False, null=True)
    title = models.CharField(max_length=150)

    content = models.JSONField(
        default=list, blank=True, null=True, help_text="儲存區塊資料的清單"
    )

    # 這裡保留，作為「文章封面圖」
    image = models.ImageField(upload_to=get_blog_upload_path, null=True, blank=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # likes 用來判斷「我有沒有按讚」，like_count 用來快速顯示「總數」（不用每次都讓資料庫數一遍）。
    like_count = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, blank=True, related_name="liked_posts")

    comment_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # 🚀 1. 預防圖片不在的 Safe URL (前端 Template 請改用 {{ post.get_image_url }})
    @property
    def get_image_url(self):
        if self.image and hasattr(self.image, "url"):
            return self.image.url
        return "https://media.fisshshop.com/media/default-photo/ideogram-v3.0_Prompt_Flat_vector_illustration_of_a_small_chibi_dead_shrimp_grey_and_black_mono-0.webp"  # 這裡放你的預設封面圖

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # 🚀 1. 加上最顯眼的 Debug 訊息
        print("======== 📦 開始執行 Save 程序 ========")

        if self.image:
            # 🚀 2. 關鍵修正：檢查這是不是一個剛上傳的檔案物件
            # 只要是新上傳的，它一定是 UploadedFile 類型
            from django.core.files.uploadedfile import UploadedFile

            if isinstance(self.image.file, UploadedFile):
                print(f"📢 偵測到新上傳檔案: {self.image.name}，準備轉檔...")
                try:
                    self.image = compress_image(self.image, threshold_kb=500)
                    print("✅ 轉檔成功，檔名已更換為 .webp")
                except Exception as e:
                    print(f"❌ 轉檔發生錯誤: {e}")
            else:
                print("ℹ️ 這是一張舊圖，跳過轉檔程序。")

        super().save(*args, **kwargs)
        print("======== 🏁 Save 程序執行完畢 ========")

    def get_absolute_url(self):
        return reverse("article", args=[str(self.id)])


@receiver(post_delete, sender=Post)
def delete_r2_image_on_post_delete(sender, instance, **kwargs):
    """當文章被刪除時，自動去 R2 砍掉對應的圖片檔案"""
    if instance.image:
        instance.image.delete(save=False)
        print(f"🗑️ 已從 R2 刪除文章圖片: {instance.image.name}")


@receiver(pre_save, sender=Post)
def delete_old_r2_image_on_change(sender, instance, **kwargs):
    """當文章更新圖片時，自動把 R2 上的『舊圖』砍掉，避免浪費空間"""
    if not instance.pk:  # 如果是新文章，不用處理
        return
    try:
        old_post = Post.objects.get(pk=instance.pk)
    except Post.DoesNotExist:
        return

    # 如果舊的有圖，且跟新的不一樣（代表使用者換圖了）
    if old_post.image and old_post.image != instance.image:
        old_post.image.delete(save=False)
        print(f"♻️ 偵測到更換圖片，已清理 R2 舊圖: {old_post.image.name}")


# "Post" (連線的對象)
# 為什麼加引號？ 如果你的 Comment 類別寫在 Post 類別的上面，Python 執行到這行會找不到 Post。
# 加了引號，Django 會等全部類別都讀完後再幫你連線，避免程式崩潰。

# related_name="comments"
# 所以因為我創造文章，文章是連在user 上面的，但我如果要反向去抓抓不到，所以我可以這樣搞就可以雙向抓
# 但在 後端邏輯 (Views / Signals) 裡
# 我們經常是先拿到一個獨立的「動作」（例如：有人點了這則留言），這時候「由下而上」回溯出它是誰的小孩，就變得超級重要。
# Post -> Comment (related_name)：是為了 「展示」（在文章下顯示所有留言）。
# Comment -> Post (ForeignKey)：是為了 「歸屬」（知道這則留言該往哪裡送


class Comment(models.Model):
    # 關聯到文章 (一篇文章可以有多個留言)
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="comments")

    # 關聯到使用者 (一個使用者可以發多個留言)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # 留言內容
    content = models.TextField()

    # likes 用來判斷「我有沒有按讚」，like_count 用來快速顯示「總數」（不用每次都讓資料庫數一遍）。
    like_count = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, blank=True, related_name="liked_comments")

    comment_count = models.IntegerField(default=0)

    # 4. 建立時間
    created_at = models.DateTimeField(auto_now_add=True)

    # 5. [核心] 父層留言：用來實作「回覆」功能
    # 如果這行是空的(null)，代表它是主留言；如果有值，代表它是某則留言的回覆
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )

    class Meta:
        ordering = ["-created_at"]  # 讓最新的留言排在最上面

    def __str__(self):
        return f"{self.author.username}: {self.content[:20]}"


# 個人頁面處理
# 如何讓他顯示多種的頭貼過濾系統
# 沒辦法直接定義user 這是功能性的user版本 龍馬
class Profile(models.Model):
    # 🚀 這行是關鍵：把這張表跟內建的 User 「焊」死在一起
    # 一個 User 只會對應到一個 Profile
    # 「連鎖刪除」。如果這顆 User 被拔掉（刪除），那麼對應的 Profile
    # 也會自動報廢（刪除），不會留下髒資料
    # 這個只是給user的編號 並非定義名子
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # 🚀 補上這一行，讓「焊點」出現
    nickname = models.CharField(max_length=50, blank=True)

    # 🖼️ 這裡定義你想擴充的「新零件」
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)  # 頭貼
    background_image = models.ImageField(
        upload_to="backgrounds/", null=True, blank=True
    )  # 背景
    bio = models.TextField(max_length=500, blank=True)  # 自我介紹

    def __str__(self):
        return f"{self.user.username} "


# 🚀 這是「自動焊槍」邏輯
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # 當新用戶產生的那一瞬間，自動建立 Profile
        # 並預設把 username 灌進 nickname
        Profile.objects.create(user=instance, nickname=instance.username)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # 🚀 關鍵：用 hasattr 檢查這顆 User 是否真的有裝 Profile 零件
    if hasattr(instance, "profile"):
        instance.profile.save()


@receiver(user_signed_up)
def send_welcome_email(request, user, **kwargs):
    # 🚀 這就是你的「歡迎信封包」
    subject = "歡迎加入 FisshShop 魚缸！"
    message = f"嘿 {user.username}，你已成功註冊！快來分享你的蝦與魚吧。"
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    # 執行發射
    send_mail(subject, message, email_from, recipient_list)
