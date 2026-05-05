import json  # 🚀 處理前端傳來的 JSON 字串
from uuid import uuid4

from django.contrib.auth import authenticate, login  # 補上 authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.files.storage import default_storage  # 🚀 處理內文照片的儲存
from django.db.models import Exists, OuterRef, Prefetch
from django.http import (
    HttpResponse,
    JsonResponse,  # 🚀 回傳成功或失敗的訊息給 JS
)
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now  # 🚀 這是用來抓現在時間的機器
from django.views import View

from .constants import CORE_SPECS_CONFIG, EXTRA_SPECS, FISH_SPECS_LABELS

# 🚀 既然 CORE_SPECS 已經不存在了，就不要 import 它
# 1. Model 從 models 資料夾抓
from .models import (  # 記得引入模型
    AquaticLife,
    Comment,
    PetFish,
    Post,
    SpecTemplate,
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


# 1. 範本 API (負責 存/改/刪)
class ManageTemplateView(FisshAPIBase):
    # 🚀 GET 負責「變身」
    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            notice = ShopNotice.objects.get(id=pk, user=request.user)
            # 這裡回傳你那個有 <input> 的編輯零件
            return render(request, "partials/notice_edit_form.html", {"n": notice})
        return HttpResponse("沒有提供 ID", status=400)

    # 🚀 POST 負責「動作」
    def post(self, request, *args, **kwargs):
        temp_id = request.POST.get("id")
        action = request.POST.get("action")

        # --- 刪除邏輯 ---
        if action == "delete":
            ShopNotice.objects.filter(id=temp_id, user=request.user).delete()
            return HttpResponse("")  # 刪除成功回傳空，HTMX 會移除該元素

        # --- 儲存邏輯 ---
        title = request.POST.get("title")
        content = request.POST.get("content")

        # 執行更新或新增
        ShopNotice.objects.update_or_create(
            id=temp_id if temp_id else None,
            user=request.user,
            defaults={"title": title, "content": content},
        )

        # 🚀 關鍵改動：不要只回傳一小塊，要重新抓取所有範本，回傳整排清單
        notices = ShopNotice.objects.filter(user=request.user).order_by("-created_at")

        # 🚀 這裡要對應你截圖中的那個檔案路徑
        return render(request, "component/notice_list_items.html", {"notices": notices})


# 2. 規格範本 API (負責 存/改/刪)
class ManageSpecAPIView(FisshAPIBase):
    def post(self, request, *args, **kwargs):
        try:
            # 🚀 因：HTMX 發送的是標準 POST 表單。果：改用 request.POST 拿資料。
            # 不再使用 json.loads(request.body)
            temp_id = request.POST.get("id")
            action = request.POST.get("action")
            name = request.POST.get("name")

            # --- 1. 刪除邏輯 ---
            if action == "delete":
                SpecTemplate.objects.filter(id=temp_id, user=request.user).delete()
                # 🚀 改這裡！不要回傳 render_spec_list
                # 因：前端 hx-target 是單一卡片的 ID。
                # 果：回傳空字串，讓 HTMX 直接把該卡片「拔除」而不補東西。
                return HttpResponse("")

            # --- 2. 儲存/更新邏輯 ---
            if not name:
                return JsonResponse(
                    {"status": "error", "message": "印章名稱不能為空"}, status=400
                )

            # 🚀 核心改動：手動把 POST 裡面的規格欄位抓出來，重新打包成 JSON 格式
            # 我們過濾掉不需要的欄位（如 id, name, action, csrf）
            exclude_keys = ["id", "action", "name", "csrfmiddlewaretoken"]
            spec_data = {
                k: v
                for k, v in request.POST.items()
                if k not in exclude_keys and v.strip() != ""
            }

            # 執行更新或新增
            if temp_id:
                spec_obj = SpecTemplate.objects.filter(
                    id=temp_id, user=request.user
                ).first()
                if not spec_obj:
                    return JsonResponse(
                        {"status": "error", "message": "無權編輯"}, status=403
                    )
            else:
                spec_obj = SpecTemplate(user=request.user)

            spec_obj.name = name
            spec_obj.data = spec_data  # 🚀 這裡存入資料庫時，Django 會自動轉成 JSON
            spec_obj.save()

            # --- 3. 回傳整排清單 ---
            return self.render_spec_list(request)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # 封裝一個小工具，讓刪除跟儲存都能共用回傳清單的邏輯
    def render_spec_list(self, request):
        spec_templates = SpecTemplate.objects.filter(user=request.user).order_by("-id")
        return render(
            request,
            "component/spec_list_items.html",
            {
                "spec_templates": spec_templates,
                "core_config": CORE_SPECS_CONFIG,
                "extra_labels": EXTRA_SPECS,
            },
        )


# 3. 頁面大總管 (負責 GET 顯示 HTML)
# views.py
class ManageDashboardView(FisshPageBase):
    def get(self, request):
        user = request.user
        context = {
            "notices": ShopNotice.objects.filter(user=user).order_by("-created_at"),
            "spec_templates": SpecTemplate.objects.filter(user=user).order_by("-id"),
            "aquatics": AquaticLife.objects.filter(owner=user).order_by("-created_at"),
            # 🚀 核心：傳送結構化設定
            "core_config": CORE_SPECS_CONFIG,
            "extra_labels": EXTRA_SPECS,  # 雜項標籤
            # 如果前端某些地方還需要「全體標籤清單」，再留著這個
            "master_labels": FISH_SPECS_LABELS,
        }
        return render(request, "manage.html", context)


# 注意：manage_spec_template 已經被上面這個整合了，可以直接刪除，
# 只要把 URL 指向 ManageDashboardView 即可。
