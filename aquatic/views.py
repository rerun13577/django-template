import json  # 🚀 處理前端傳來的 JSON 字串
from uuid import uuid4

from django.contrib.auth import authenticate, login  # 補上 authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.files.storage import default_storage  # 🚀 處理內文照片的儲存
from django.db.models import Exists, OuterRef, Prefetch
from django.http import JsonResponse  # 🚀 回傳成功或失敗的訊息給 JS
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now  # 🚀 這是用來抓現在時間的機器
from django.views import View

# 1. Model 從 models 資料夾抓
from .models import (  # 記得引入模型
    AquaticLife,
    Comment,
    PetFish,
    Post,
)
from .models.shop_notice import ShopNotice

# 2. 工具從 utils 檔案抓 🚀
from .utils import compress_image


# 🚀 1. 一般網頁用的保險箱 (沒登入就踢去登入頁)
class FisshPageBase(LoginRequiredMixin, View):
    login_url = "/accounts/login/"
    redirect_field_name = "next"


# 🚀 2. API 用的保險箱 (沒登入就回傳 401 錯誤，讓 JS 處理彈窗)
class FisshAPIBase(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # 🚀 關鍵：不回傳 redirect，而是回傳 JsonResponse
            return JsonResponse(
                {
                    "status": "unauthorized",
                    "message": "請先登入才能操作喔！",
                    "login_url": f"/accounts/login/?next={request.path}",
                },
                status=401,
            )  # 401 代表「未經授權」

        return super().dispatch(request, *args, **kwargs)


class IndexView(View):
    def get(self, request):
        # 撈出資料庫裡所有的水生生物
        items = AquaticLife.objects.all()
        return render(request, "index.html", {"items": items})


class BlogView(View):
    def get(self, request):
        user = request.user

        # 這裡是你原本寫的優化查詢邏輯
        posts = (
            Post.objects.select_related("author")
            .prefetch_related("author__socialaccount_set")
            .order_by("-created_at")
        )

        # 如果有登入，動態增加 is_liked 標籤
        if user.is_authenticated:
            posts = posts.annotate(
                is_liked=Exists(Post.objects.filter(id=OuterRef("pk"), likes=user))
            )

        return render(request, "blog.html", {"posts": posts})


class HomeView(View):
    def get(self, request):
        return render(request, "index.html")


class LoginView(View):
    # 🚀 GET：當使用者「看到」登入頁面時執行
    def get(self, request):
        next_url = request.GET.get("next", "/")
        return render(request, "login.html", {"next": next_url})

    # 🚀 POST：當使用者「按下」登入按鈕送出表單時執行
    def post(self, request):
        next_url = request.POST.get("next", "/")
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # 登入成功，去他想去的地方
            return redirect(next_url)
        else:
            # 登入失敗，帶著錯誤訊息回原頁面
            return render(
                request,
                "login.html",
                {"next": next_url, "error_message": "帳號或密碼錯誤，請再試一次"},
            )


# 1. 文章詳情頁：繼承普通 View (路人也能看)
class ArticleDetailView(View):
    def get(self, request, pk):
        user = request.user

        # --- 這裡是你的高效能查詢邏輯 (完全沒變，搬進來縮進一格而已) ---
        reply_queryset = Comment.objects.select_related("author")
        if user.is_authenticated:
            reply_queryset = reply_queryset.annotate(
                is_liked=Exists(Comment.objects.filter(id=OuterRef("pk"), likes=user))
            )

        comment_queryset = Comment.objects.select_related("author").prefetch_related(
            Prefetch("replies", queryset=reply_queryset.order_by("created_at"))
        )

        if user.is_authenticated:
            comment_queryset = comment_queryset.annotate(
                is_liked=Exists(Comment.objects.filter(id=OuterRef("pk"), likes=user))
            )

        post_queryset = Post.objects.select_related("author").prefetch_related(
            Prefetch("comments", queryset=comment_queryset.filter(parent=None))
        )

        if user.is_authenticated:
            post_queryset = post_queryset.annotate(
                is_liked=Exists(Post.objects.filter(id=OuterRef("pk"), likes=user))
            )

        post = get_object_or_404(post_queryset, pk=pk)
        return render(request, "article.html", {"post": post})


# 2. 按讚 API：繼承 FisshAPIBase (保險箱自動檢查登入)
class ToggleLikeView(FisshAPIBase):
    def post(self, request, post_id):
        # ✅ 重點：不用再寫 if not user.is_authenticated 了！
        # 因為 FisshAPIBase 已經幫你在門口擋掉了。

        post = get_object_or_404(Post, id=post_id)
        user = request.user

        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            is_liked = False
        else:
            post.likes.add(user)
            is_liked = True

        current_count = post.likes.count()
        # 這裡用 update 是對的，效率比較高
        Post.objects.filter(id=post_id).update(like_count=current_count)

        return JsonResponse({"is_liked": is_liked, "new_count": current_count})


# 1. 留言按讚 API (繼承 API 保險箱)
class ToggleCommentLikeView(FisshAPIBase):
    def post(self, request, comment_id):
        # ✅ 自動檢查登入，沒登入會回傳 401
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user

        if comment.likes.filter(id=user.id).exists():
            comment.likes.remove(user)
            is_liked = False
        else:
            comment.likes.add(user)
            is_liked = True

        return JsonResponse({"is_liked": is_liked, "new_count": comment.likes.count()})


# 2. 新增留言 (繼承 網頁保險箱)
class AddCommentView(FisshPageBase):
    def post(self, request, post_id):
        # ✅ 自動檢查登入，沒登入會踢去登入頁
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get("content")

        if content:
            comment = Comment(post=post, author=request.user, content=content)
            parent_id = request.POST.get("parent_id")
            if parent_id:
                comment.parent = Comment.objects.get(id=parent_id)
            comment.save()

        return redirect("article", pk=post_id)


# 3. 發文 API (繼承 API 保險箱)
class CreatePostView(FisshAPIBase):
    def post(self, request):
        # ✅ 自動檢查登入
        title = request.POST.get("title")
        cover_image = request.FILES.get("cover_image")
        raw_content = request.POST.get("content_json", "[]")
        content_list = json.loads(raw_content)

        date_str = now().strftime("%Y/%m/%d")
        article_token = uuid4().hex[:8]

        # 圖片處理邏輯維持不變
        for block in content_list:
            if block["type"] == "image_group":
                real_urls = []
                for secret_key in block["value"]:
                    file_obj = request.FILES.get(secret_key)
                    if file_obj:
                        compressed_file = compress_image(file_obj)
                        content_file_path = f"blog/{date_str}/{article_token}/content/{uuid4().hex[:8]}.webp"
                        path = default_storage.save(content_file_path, compressed_file)
                        real_urls.append(default_storage.url(path))
                block["value"] = real_urls

        new_post = Post.objects.create(
            title=title,
            folder_uuid=article_token,
            image=cover_image,
            content=content_list,
            author=request.user,
        )

        return JsonResponse(
            {
                "status": "success",
                "url": f"/blog/post/{new_post.id}/",
            }
        )


# 記得匯入你的 Model
# from .models import Post, AquaticLife, PetFish


class ProfileView(FisshPageBase):
    def get(self, request, username=None):
        # 🚀 第一關：沒名字的情況
        if not username:
            if request.user.is_authenticated:
                # 有登入：帶他去 /profile/你的名字/ (這樣連結就帶名字了)
                return redirect("user_profile", username=request.user.username)
            else:
                # 沒登入：直接踢去登入頁面
                return redirect("account_login")

        # 🚀 第二關：有名字（不管是自己的還是別人的）
        user_qs = User.objects.select_related("profile").prefetch_related(
            "socialaccount_set"
        )

        # 抓取目標使用者，不存在就噴 404
        target_user = get_object_or_404(user_qs, username=username)

        # 直接抓人，不用再 if/else 判斷了
        target_user = get_object_or_404(user_qs, username=username)

        # --- 以下維持原樣 ---
        user_posts = (
            Post.objects.filter(author=target_user)
            .select_related("author")
            .annotate(
                is_liked=Exists(
                    Post.likes.through.objects.filter(
                        post_id=OuterRef("pk"), user_id=request.user.id
                    )
                )
            )
            .order_by("-created_at")
        )

        user_aquatics = AquaticLife.objects.filter(owner=target_user).order_by(
            "-created_at"
        )
        user_pets = PetFish.objects.filter(owner=target_user).order_by("-created_at")

        user_notices = []
        if request.user == target_user:
            user_notices = ShopNotice.objects.filter(user=target_user).order_by(
                "-created_at"
            )

        context = {
            "target_user": target_user,
            "user": request.user,
            "posts": user_posts,
            "items": user_aquatics,
            "pets": user_pets,
            "notices": user_notices,
        }
        return render(request, "profile.html", context)


class ManageTemplateView(FisshAPIBase):
    """
    整合型 API：處理範本的 新增、修改、刪除
    URL: /api/manage-template/
    """

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            temp_id = data.get("id")
            title = data.get("title")
            content = data.get("content")
            action = data.get("action")  # 🚀 增加一個動作標記

            # -------------------------------------------------------
            # 🚀 動作 1：刪除 (如果前端傳了 action: 'delete')
            # -------------------------------------------------------
            if action == "delete":
                if not temp_id:
                    return JsonResponse(
                        {"status": "error", "message": "刪除失敗：缺少 ID"}, status=400
                    )

                # 確保只能刪除「自己的」範本
                deleted_count, _ = ShopNotice.objects.filter(
                    id=temp_id, user=request.user
                ).delete()

                if deleted_count > 0:
                    return JsonResponse({"status": "success", "message": "範本已刪除"})
                return JsonResponse(
                    {"status": "error", "message": "找不到該範本"}, status=404
                )

            # -------------------------------------------------------
            # 🚀 動作 2：新增 或 修改 (共用邏輯)
            # -------------------------------------------------------
            if not title or not content:
                return JsonResponse(
                    {"status": "error", "message": "標題與內容不能為空"}, status=400
                )

            if temp_id:
                # 👉 修改模式 (因：前端有傳 ID)
                notice = ShopNotice.objects.filter(
                    id=temp_id, user=request.user
                ).first()
                if not notice:
                    return JsonResponse(
                        {"status": "error", "message": "權限不足或範本不存在"},
                        status=404,
                    )

                notice.title = title
                notice.content = content
                notice.save()
                msg = "範本修改成功"
            else:
                # 👉 新增模式 (因：前端沒傳 ID)
                notice = ShopNotice.objects.create(
                    user=request.user, title=title, content=content
                )
                msg = "範本儲存成功"

            return JsonResponse(
                {
                    "status": "success",
                    "message": msg,
                    "id": notice.id,  # 把 ID 丟回去讓前端更新按鈕
                }
            )

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
