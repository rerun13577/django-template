import json  # 🚀 處理前端傳來的 JSON 字串
from uuid import uuid4

from django.contrib.auth import authenticate, login  # 補上 authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
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
    Post,
)

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


# -----------------------------------------------------------------------------------------------------
# def index(request):
#     # 撈出資料庫裡所有的水生生物
#     items = AquaticLife.objects.all()

#     # request有關係這個使用者的各種資訊 傳過來的個人資訊也要傳回去 訂單詳細貼紙
#     # 指定這些東西要塞去哪裡 要送去哪裡
#     # 回傳水生生物 訂單內容
#     return render(request, "index.html", {"items": items})


# def blog(request):
#     user = request.user

#     # 解決N+1的問題
#     # select_related("author")：這是一個 SQL JOIN。
#     # 它在抓文章時，順便把作者的名字、頭像通通「焊」在一起帶過來。
#     # 我要先進auther 再去社交帳號 因為他有可能是用他自己的帳號密碼登入
#     # 如果直接跳社交帳號就是預設立場我的客人只會用第三方軟件登入
#     # 使用者（User）可能有「多個」社群帳號
#     posts = (
#         Post.objects.select_related("author")
#         .prefetch_related("author__socialaccount_set")
#         .order_by("-created_at")
#     )

#     if user.is_authenticated:
#         posts = posts.annotate(
#             is_liked=Exists(Post.objects.filter(id=OuterRef("pk"), likes=user))
#         )

#     return render(request, "blog.html", {"posts": posts})


# 下面是html的環節


# def home(request):
#     return render(request, "index.html")


# def login_view(request):
#     next_url = request.GET.get("next", "/")

#     if request.method == "POST":
#         # 1. 抓取表單填寫的內容
#         username = request.POST.get("username")
#         password = request.POST.get("password")

#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             login(request, user)

#             redirect_to = request.POST.get("next", next_url)
#             return redirect(redirect_to)
#         else:
#             return render(
#                 request,
#                 "login.html",
#                 {"next": next_url, "error_message": "帳號或密碼錯誤，請再試一次"},
#             )

#     return render(request, "login.html", {"next": next_url})


# def article_view(request, pk):
#     user = request.user

#     reply_queryset = Comment.objects.select_related("author")
#     if user.is_authenticated:
#         reply_queryset = reply_queryset.annotate(
#             is_liked=Exists(Comment.objects.filter(id=OuterRef("pk"), likes=user))
#         )

#     comment_queryset = Comment.objects.select_related("author").prefetch_related(
#         Prefetch("replies", queryset=reply_queryset.order_by("created_at"))  # 標記回覆
#     )

#     if user.is_authenticated:
#         comment_queryset = comment_queryset.annotate(
#             is_liked=Exists(Comment.objects.filter(id=OuterRef("pk"), likes=user))
#         )

#     post_queryset = Post.objects.select_related("author").prefetch_related(
#         Prefetch("comments", queryset=comment_queryset.filter(parent=None))
#     )

#     if user.is_authenticated:
#         post_queryset = post_queryset.annotate(
#             is_liked=Exists(Post.objects.filter(id=OuterRef("pk"), likes=user))
#         )

#     post = get_object_or_404(post_queryset, pk=pk)
#     return render(request, "article.html", {"post": post})


# # requset 傳入前端的要求到函數裡面處理
# def toggle_like(request, post_id):
#     if not request.user.is_authenticated:
#         return JsonResponse(
#             {
#                 "status": "unauthorized",  # 改成這樣
#                 "login_url": f"/accounts/login/?next={request.path}",
#             },
#             status=401,
#         )

#     post = get_object_or_404(Post, id=post_id)
#     user = request.user

#     if post.likes.filter(id=user.id).exists():
#         post.likes.remove(user)
#         is_liked = False
#     else:
#         post.likes.add(user)
#         is_liked = True

#     current_count = post.likes.count()
#     Post.objects.filter(id=post_id).update(like_count=current_count)

#     return JsonResponse({"is_liked": is_liked, "new_count": current_count})


# def toggle_comment_like(request, comment_id):

#     if not request.user.is_authenticated:
#         return JsonResponse(
#             {
#                 "status": "unauthorized",  # 改成這樣
#                 "login_url": f"/accounts/login/?next={request.path}",
#             },
#             status=401,
#         )

#     comment = get_object_or_404(Comment, id=comment_id)
#     user = request.user

#     if comment.likes.filter(id=user.id).exists():
#         comment.likes.remove(user)
#         is_liked = False
#     else:
#         comment.likes.add(user)
#         is_liked = True

#     return JsonResponse({"is_liked": is_liked, "new_count": comment.likes.count()})


# @login_required  # 確保有登入才能留言
# def add_comment(request, post_id):
#     if request.method == "POST":
#         post = get_object_or_404(Post, id=post_id)
#         content = request.POST.get("content")

#         if content:
#             # 建立留言物件但先不存檔
#             comment = Comment(post=post, author=request.user, content=content)

#             # 如果是回覆某則留言，抓取 parent_id
#             parent_id = request.POST.get("parent_id")
#             if parent_id:
#                 comment.parent = Comment.objects.get(id=parent_id)

#             comment.save()  # 正式存入資料庫

#     return redirect("article", pk=post_id)


# # 發文邏輯-----------------------------------------------------------------------------------------------------
# @login_required
# def create_post_api(request):
#     if request.method == "POST":
#         title = request.POST.get("title")
#         cover_image = request.FILES.get("cover_image")
#         raw_content = request.POST.get("content_json", "[]")
#         content_list = json.loads(raw_content)

#         # 🚀 1. 產生這篇文章唯一的「門牌號碼」
#         date_str = now().strftime("%Y/%m/%d")
#         article_token = uuid4().hex[:8]

#         # 2. 處理內文中的多張照片 (這部分不變)
#         for block in content_list:
#             if block["type"] == "image_group":
#                 real_urls = []
#                 for secret_key in block["value"]:
#                     file_obj = request.FILES.get(secret_key)
#                     if file_obj:
#                         compressed_file = compress_image(file_obj)

#                         # 🚀 3. 內文路徑對齊 (使用剛剛產生的 article_token)
#                         content_file_path = f"blog/{date_str}/{article_token}/content/{uuid4().hex[:8]}.webp"

#                         path = default_storage.save(content_file_path, compressed_file)
#                         real_urls.append(default_storage.url(path))

#                 block["value"] = real_urls

#         # 🚀 4. 正式存入資料庫 (關鍵修改處！)
#         new_post = Post.objects.create(
#             title=title,
#             folder_uuid=article_token,  # 🔥 補上這行！讓 Model 知道門牌號碼
#             image=cover_image,  # 此時 Model 會抓到 folder_uuid 並算對路徑
#             content=content_list,
#             author=request.user,
#         )

#         return JsonResponse(
#             {
#                 "status": "success",
#                 "url": f"/blog/post/{new_post.id}/",
#             }
#         )

#     return JsonResponse({"status": "error", "message": "無效請求"}, status=400)
