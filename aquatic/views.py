import json  # 🚀 處理前端傳來的 JSON 字串
from uuid import uuid4

from django.contrib.auth import authenticate, login  # 補上 authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.files.storage import default_storage  # 🚀 處理內文照片的儲存
from django.db import transaction
from django.db.models import Exists, OuterRef, Prefetch
from django.http import (
    HttpResponse,
    HttpResponseForbidden,  # 🛡️ 引入禁止存取的物理訊號
    JsonResponse,  # 🚀 回傳成功或失敗的訊息給 JS
)
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string  # 🚀 補上這行，紅燈當場熄滅
from django.utils.timezone import now  # 🚀 這是用來抓現在時間的機器
from django.views import View

from .constants import (
    CORE_SPECS_CONFIG,
    EXTRA_SPECS,
    FISH_SPECS_LABELS,
    TAIWAN_REGIONS,  # 🚀 物理引入你的常數庫
)

# 🚀 既然 CORE_SPECS 已經不存在了，就不要 import 它
# 1. Model 從 models 資料夾抓
from .models import (  # 🚀 核心修正：手動補上副圖模型  # 記得引入模型
    AquaticImage,
    AquaticLife,
    Comment,
    PetFish,
    Post,
    Profile,
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
        items = AquaticLife.objects.filter(is_active=True).order_by("-created_at")[:10]
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


class ProfileView(View):  # 🎯 因果修正 A：改繼承純粹的 View，解除強迫登入的物理鎖
    def get(self, request, username=None):

        # ────────────────────────────────────────────────────────
        # 🚀 第一關：網址「沒帶名字」的情境 (例如直接按導覽列的 /profile/)
        # ────────────────────────────────────────────────────────
        if not username:
            if request.user.is_authenticated:
                # 因：有登入但沒帶名字。果：自動重導向到他自己的專屬頁面
                return redirect("user_profile", username=request.user.username)
            else:
                # 因：沒登入也沒帶名字。果：不知道要看誰，物理踢去登入頁面
                return redirect("account_login")

        # ────────────────────────────────────────────────────────
        # 🚀 第二關：網址「有帶名字」的情境 (不論是看自己還是看別人)
        # ────────────────────────────────────────────────────────
        user_qs = User.objects.select_related("profile").prefetch_related(
            "socialaccount_set"
        )

        # 抓取目標使用者，不存在就噴 404
        target_user = get_object_or_404(user_qs, username=username)

        # ────────────────────────────────────────────────────────
        # 🚀 第三關：區分「看自己」與「看別人」的資料庫優化防線
        # ────────────────────────────────────────────────────────

        # 🎯 因果修正 B：判定當前瀏覽網頁的人是誰
        is_me = request.user == target_user
        is_guest = not request.user.is_authenticated

        # 1. 處理貼文與點讚狀況（防止匿名使用者踩到 request.user.id 造成的 SQL 崩潰）
        if is_guest:
            # 沒登入的人看別人：物理上「不可能有點讚紀錄」，直接硬編碼為 False，不查點讚表
            user_posts = (
                Post.objects.filter(author=target_user)
                .select_related("author")
                .order_by("-created_at")
            )
            # 在 Python 層面幫貼文塞入 False，防前端噴 Template 錯誤
            for post in user_posts:
                post.is_liked = False
        else:
            # 有登入（看自己或看別人）：啟動 Exists 點讚雷達
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

        # 2. 商品清單（items）與寵物魚（pets）
        # 💡 因果邏輯：如果是「看自己」，可能需要看到下架或隱藏的魚；
        # 但你給的邏輯是統一 filter(is_active=True)，這裡完全沿用你的物理變數
        user_aquatics = AquaticLife.objects.filter(
            owner=target_user, is_active=True
        ).order_by("-created_at")

        user_pets = PetFish.objects.filter(owner=target_user).order_by("-created_at")

        # 3. 店家公告（ShopNotice）
        # 💡 因果邏輯：只有「看自己」才會載入公告（你原本寫的邏輯非常精準！）
        user_notices = []
        if is_me:
            user_notices = ShopNotice.objects.filter(user=target_user).order_by(
                "-created_at"
            )

        # ────────────────────────────────────────────────────────
        # 🚀 第四關：打包傳輸
        # ────────────────────────────────────────────────────────
        context = {
            "target_user": target_user,
            "user": request.user,
            "posts": user_posts,
            "items": user_aquatics,  # 變數名稱物理鎖死，完美對接
            "pets": user_pets,
            "notices": user_notices,
            "is_me": is_me,  # 🎯 順手塞一個布林值給前端，讓你方便隱藏「編輯個人資料」的按鈕
        }
        return render(request, "profile.html", context)


# 1. 範本 API (負責 存/改/刪)
class ManageTemplateView(FisshAPIBase):
    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            notice = ShopNotice.objects.get(id=pk, user=request.user)
            return render(request, "partials/notice_edit_form.html", {"n": notice})
        return HttpResponse("沒有提供 ID", status=400)

    def post(self, request, *args, **kwargs):
        temp_id = request.POST.get("id")
        action = request.POST.get("action")

        # --- 1. 刪除邏輯 ---
        # --- 1. 刪除邏輯 ---
        if action == "delete":
            ShopNotice.objects.filter(id=temp_id, user=request.user).delete()

            # 🚀 核心刪除同步補丁：利用正則表達式物理清除字串記憶體，並拔除畫面 option
            sync_script = f"""
            <script>
                (function() {{
                    const deletedId = "{temp_id}";

                    // 因：全域變數記憶體存在。果：用正則把對應的 <option> 標籤整條抹除
                    if (typeof GLOBAL_NOTICE_OPTIONS !== 'undefined') {{
                        const regex = new RegExp('<option value="' + deletedId + '">.*?</option>', 'g');
                        GLOBAL_NOTICE_OPTIONS = GLOBAL_NOTICE_OPTIONS.replace(regex, '');
                    }}

                    // 因：掃描畫面上所有的提醒下拉選單。果：抓到該 ID 的 option 直接 .remove() 物理消滅
                    document.querySelectorAll('select[name="fish_notice[]"], select[name="global_notice"], #global_notice').forEach(select => {{
                        const opt = select.querySelector('option[value="' + deletedId + '"]');
                        if (opt) opt.remove();
                    }});
                }})();
            </script>
            """
            return HttpResponse(
                sync_script
            )  # 🚀 回傳腳本，HTMX 會用它替換掉原本的卡片卡槽

        # --- 2. 儲存/更新邏輯 ---
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()

        if not title or not content:
            return HttpResponse("內容不可為空", status=400)

        # 執行更新或新增
        notice_obj, created = ShopNotice.objects.update_or_create(
            id=temp_id if temp_id else None,
            user=request.user,
            defaults={"title": title, "content": content},
        )

        notices = ShopNotice.objects.filter(user=request.user).order_by("-created_at")

        # 🚀 因：先渲染出常規的 HTML 清單
        response = render(
            request, "component/notice_list_items.html", {"notices": notices}
        )

        # 🚀 過：打包前端同步腳本。
        # 註：因為前端已經改成 let，底下的 GLOBAL_NOTICE_OPTIONS += newOptHtml 就會精準解鎖。
        new_opt_html = f'<option value="{notice_obj.id}">{notice_obj.title}</option>'
        sync_script = f"""
        <script>
            (function() {{
                const newId = "{notice_obj.id}";
                const newName = "{notice_obj.title}";
                const newOptHtml = '{new_opt_html}';

                if (typeof GLOBAL_NOTICE_OPTIONS !== 'undefined' && !GLOBAL_NOTICE_OPTIONS.includes('value="' + newId + '"')) {{
                    GLOBAL_NOTICE_OPTIONS += newOptHtml;
                }}

                document.querySelectorAll('select[name="fish_notice[]"], select[name="global_notice"], #global_notice').forEach(select => {{
                    const existingOpt = select.querySelector('option[value="' + newId + '"]');
                    if (!existingOpt) {{
                        const opt = document.createElement('option');
                        opt.value = newId;
                        opt.textContent = newName;
                        select.appendChild(opt);
                    }} else {{
                        existingOpt.textContent = newName;
                    }}
                }});
            }})();
        </script>
        """
        # 🚀 果：把腳本用二進位編碼，暴力黏在原有 HTML 屁股後面發射給 HTMX
        response.content = response.content + sync_script.encode("utf-8")
        return response


# 2. 規格範本 API (負責 存/改/刪)
class ManageSpecAPIView(FisshAPIBase):
    def post(self, request, *args, **kwargs):
        try:
            temp_id = request.POST.get("id")
            action = request.POST.get("action")
            name = request.POST.get("name")

            # --- 1. 刪除邏輯 ---
            # --- 1. 刪除邏輯 ---
            if action == "delete":
                SpecTemplate.objects.filter(id=temp_id, user=request.user).delete()

                # 🚀 核心刪除同步補丁：利用正則表達式物理清除字串記憶體，並拔除畫面 option
                sync_script = f"""
                <script>
                    (function() {{
                        const deletedId = "{temp_id}";

                        // 因：全域變數記憶體存在。果：用正則把對應的 <option> 標籤整條抹除
                        if (typeof GLOBAL_SPEC_OPTIONS !== 'undefined') {{
                            const regex = new RegExp('<option value="' + deletedId + '">.*?</option>', 'g');
                            GLOBAL_SPEC_OPTIONS = GLOBAL_SPEC_OPTIONS.replace(regex, '');
                        }}

                        // 因：掃描畫面上所有的規格下拉選單。果：抓到該 ID 的 option 直接 .remove() 物理消滅
                        document.querySelectorAll('select[name="fish_spec[]"], select[name="global_spec"], #global_spec').forEach(select => {{
                            const opt = select.querySelector('option[value="' + deletedId + '"]');
                            if (opt) opt.remove();
                        }});
                    }})();
                </script>
                """
                return HttpResponse(
                    sync_script
                )  # 🚀 回傳腳本，HTMX 會用它替換掉原本的卡片卡槽

            # --- 2. 儲存/更新邏輯 ---
            if not name:
                return JsonResponse(
                    {"status": "error", "message": "印章名稱不能為空"}, status=400
                )

            exclude_keys = ["id", "action", "name", "csrfmiddlewaretoken"]
            spec_data = {
                k: v
                for k, v in request.POST.items()
                if k not in exclude_keys and v.strip() != ""
            }

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
            spec_obj.data = spec_data
            spec_obj.save()

            # --- 3. 獲取原有的清單 HTML 回傳（呼叫下方補好的工具） ---
            response = self.render_spec_list(request)

            # 核心因果同步線：利用 JS 強行修改前端記憶體與即時選單
            new_opt_html = f'<option value="{spec_obj.id}">{spec_obj.name}</option>'
            sync_script = f"""
            <script>
                (function() {{
                    const newId = "{spec_obj.id}";
                    const newName = "{spec_obj.name}";
                    const newOptHtml = '{new_opt_html}';

                    if (typeof GLOBAL_SPEC_OPTIONS !== 'undefined' && !GLOBAL_SPEC_OPTIONS.includes('value="' + newId + '"')) {{
                        GLOBAL_SPEC_OPTIONS += newOptHtml;
                    }}

                    document.querySelectorAll('select[name="fish_spec[]"], select[name="global_spec"], #global_spec').forEach(select => {{
                        const existingOpt = select.querySelector('option[value="' + newId + '"]');
                        if (!existingOpt) {{
                            const opt = document.createElement('option');
                            opt.value = newId;
                            opt.textContent = newName;
                            select.appendChild(opt);
                        }} else {{
                            existingOpt.textContent = newName;
                        }}
                    }});
                }})();
            </script>
            """
            # 這裡就不會再噴 NoneType 錯誤了，因為 response 拿到了實體物件
            response.content = response.content + sync_script.encode("utf-8")
            return response

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # 🚀 實體修復線：把原本洗掉的渲染代碼刻回來
    def render_spec_list(self, request):
        # 1. 撈出該用戶的實體規格資料
        spec_templates = SpecTemplate.objects.filter(user=request.user).order_by("-id")

        # 2. 🚀 核心因果補丁 A：定義核心規格的標籤與型態，對齊你 HTML 裡的 item.type 與 item.label
        core_config = [
            {"label": "pH值", "type": "range"},
            {"label": "適宜溫度", "type": "range"},
            {"label": "體長(cm)", "type": "single"},
            {"label": "建議水量(L)", "type": "single"},
        ]

        # 3. 🚀 核心因果補丁 B：定義次要規格的字串陣列，對齊你 HTML 裡的 {% for label in extra_labels %}
        extra_labels = [
            "GH硬度",
            "KH硬度",
            "性情",
            "食性",
            "比重",
            "水流強度",
            "光照需求",
        ]

        # 4. 把所有必備零件打包發射給前端 HTML
        return render(
            request,
            "component/spec_list_items.html",
            {
                "spec_templates": spec_templates,
                "templates": spec_templates,  # 備用名牌
                "core_config": core_config,  # 🚀 讓前端核心迴圈動起來
                "extra_labels": extra_labels,  # 🚀 讓前端次要迴圈動起來
            },
        )


# 3. 頁面大總管 (負責 GET 顯示 HTML)
# views.py
class ManageDashboardView(FisshPageBase):
    def get(self, request, *args, **kwargs):
        user = request.user

        # 🚀 1. 基礎資料流：撈出該使用者所有的商品（不論上下架）
        products = AquaticLife.objects.filter(owner=user).order_by("-created_at")

        # 🚀 2. 因果分流：利用同一個 QuerySet 在記憶體內進行狀態拆分（不增加資料庫負擔）
        active_products = products.filter(is_active=True)
        inactive_products = products.filter(is_active=False)

        # 🚀 3. 整合所有資料進 Context
        context = {
            # 🔒 安全防線：完全保留你原本的 items，後續接的任何功能絕對 100% 不會壞
            "items": products,
            # 🎯 分區新變數：供你在 HTML 裡渲染「上架區」與「下架區」的兩組獨立 grid 迴圈
            "active_items": active_products,
            "inactive_items": inactive_products,
            # 範本與提醒 (原本的配置完全保留)
            "notices": ShopNotice.objects.filter(user=user).order_by("-created_at"),
            "spec_templates": SpecTemplate.objects.filter(user=user).order_by("-id"),
            # 核心：表單欄位配置
            "core_config": CORE_SPECS_CONFIG,
            "extra_labels": EXTRA_SPECS,
            "master_labels": FISH_SPECS_LABELS,
            "target_user": user,
        }

        # 🚀 4. 渲染「主頁面」
        return render(request, "manage.html", context)


# 注意：manage_spec_template 已經被上面這個整合了，可以直接刪除，
# 只要把 URL 指向 ManageDashboardView 即可。

# 🚀 記得引入你的 Model (假設 SpecTemplate 是你存規格範本的名字)


# aquatic/views.py


class AddProductBatchView(FisshPageBase, View):
    def post(self, request, *args, **kwargs):
        category_map = {
            "魚類": "FISH",
            "蝦類": "SHRIMP",
            "水草類": "PLANT",
            "螺蚌類": "SHELLFISH",
            "其他": "OTHER",
        }

        # 🚀 智慧相容防線：不管前端寫 fish_name[] 還是 fish_name，getlist 都能相容抓成 Python 陣列
        fish_names = request.POST.getlist("fish_name[]") or request.POST.getlist(
            "fish_name"
        )
        fish_prices = request.POST.getlist("fish_price[]") or request.POST.getlist(
            "fish_price"
        )
        fish_specs = request.POST.getlist("fish_spec[]") or request.POST.getlist(
            "fish_spec"
        )
        fish_notices = request.POST.getlist("fish_notice[]") or request.POST.getlist(
            "fish_notice"
        )

        global_spec = request.POST.get("global_spec")
        global_notice = request.POST.get("global_notice")
        custom_content = request.POST.get("content")

        try:
            created_products = []
            with transaction.atomic():
                for i, name in enumerate(fish_names):
                    if not name.strip():
                        continue

                    # 價格匹配
                    price_str = fish_prices[i] if i < len(fish_prices) else "0"
                    price_integer = int(price_str) if price_str.strip().isdigit() else 0

                    # 提醒範本處理
                    if (
                        fish_notices
                        and i < len(fish_notices)
                        and fish_notices[i].strip()
                    ):
                        current_notice_id = fish_notices[i]
                    else:
                        current_notice_id = global_notice

                    notice_instance = None
                    final_description = ""

                    if current_notice_id and str(current_notice_id).strip():
                        notice_instance = ShopNotice.objects.filter(
                            id=current_notice_id
                        ).first()
                    elif custom_content and custom_content.strip():
                        final_description = custom_content.strip()
                    else:
                        return HttpResponse("上架失敗：提醒範本不可為空！", status=400)

                    # 建立生物主體
                    new_fish = AquaticLife(
                        owner=request.user,
                        name=name,
                        price=price_integer,
                        notice_template=notice_instance,
                        description=final_description,
                    )

                    if hasattr(request.user, "city") and request.user.city:
                        new_fish.city = request.user.city

                    # 規格範本處理
                    if fish_specs and i < len(fish_specs) and fish_specs[i].strip():
                        current_spec_id = fish_specs[i]
                    else:
                        current_spec_id = global_spec

                    spec_template = (
                        SpecTemplate.objects.filter(id=current_spec_id).first()
                        if current_spec_id
                        else None
                    )

                    def safe_float(v):
                        return float(v) if v and str(v).strip() else None

                    def safe_int(v):
                        return int(float(v)) if v and str(v).strip() else None

                    extra_keys = [
                        "GH硬度",
                        "KH硬度",
                        "性情",
                        "食性",
                        "比重",
                        "水流強度",
                        "光照需求",
                    ]

                    if spec_template:
                        data = spec_template.data if spec_template else {}
                        raw_cat = data.get("生物種類", "其他")
                        new_fish.ph_min = data.get("pH值_min")
                        new_fish.ph_max = data.get("pH值_max")
                        new_fish.temp_min = data.get("適宜溫度_min")
                        new_fish.temp_max = data.get("適宜溫度_max")
                        new_fish.adult_length = data.get("體長(cm)")
                        new_fish.min_tank_size = data.get("建議水量(L)")
                        new_fish.specs_json = {
                            k: data[k] for k in extra_keys if k in data
                        }
                    else:
                        raw_cat = request.POST.get("生物種類", "其他")
                        new_fish.ph_min = safe_float(request.POST.get("pH值_min"))
                        new_fish.ph_max = safe_float(request.POST.get("pH值_max"))
                        new_fish.temp_min = safe_int(request.POST.get("適宜溫度_min"))
                        new_fish.temp_max = safe_int(request.POST.get("適宜溫度_max"))
                        new_fish.adult_length = safe_float(request.POST.get("體長(cm)"))
                        new_fish.min_tank_size = safe_int(
                            request.POST.get("建議水量(L)")
                        )

                        manual_specs = {}
                        for k in extra_keys:
                            val = request.POST.get(k)
                            if val and val.strip():
                                manual_specs[k] = val.strip()
                        new_fish.specs_json = manual_specs

                    new_fish.category = category_map.get(raw_cat, "OTHER")

                    # ────────────────────────────────────────────────────────
                    # 🚀 核心共用補丁 D：完美合體單獨與批量的多圖分流
                    # ────────────────────────────────────────────────────────
                    # ────────────────────────────────────────────────────────
                    # 🚀 核心共用補丁 D：完美合體單獨與批量的多圖分流（已加入去重防線）
                    # ────────────────────────────────────────────────────────
                    slot_num = i + 1
                    # 1. 優先撈取批量專用的獨立群組名牌
                    current_fish_images = request.FILES.getlist(
                        f"fish_image_{slot_num}[]"
                    )

                    # 2. 因果降級防線：如果批量名字落空，且目前是第 1 隻魚，就直接抓單獨版的 fish_image[]
                    if not current_fish_images and i == 0:
                        current_fish_images = request.FILES.getlist("fish_image[]")

                    if current_fish_images:
                        # 🚀 核心去重核心：利用 (檔名, 大小) 作為 Unique Key，物理清除因為多選產生的重疊檔案
                        seen_files = set()
                        unique_fish_images = []
                        for f in current_fish_images:
                            file_key = (f.name, f.size)
                            if file_key not in seen_files:
                                seen_files.add(file_key)
                                unique_fish_images.append(f)

                        # 重新寫入乾淨、無重複的陣列（此時長度會精準回歸為最大 4 張）
                        current_fish_images = unique_fish_images

                        # 第一張強制做封面
                        new_fish.image = current_fish_images[0]

                    # 先存主體拿到 PK
                    new_fish.save()

                    # 剩餘的圖進副圖藝廊 (此時長度減 1，最多只會跑 3 次，完美避坑)
                    if len(current_fish_images) > 1:
                        for extra_img in current_fish_images[1:]:
                            AquaticImage.objects.create(
                                product=new_fish, image=extra_img
                            )
                    created_products.append(new_fish)
            # 因為你用了 HTMX (hx-post)，回傳這行腳本一樣能完美觸發前端重新整理
            cards_html = ""
            for prod in created_products:
                cards_html += render_to_string(
                    "component/new-creature-card.html", {"item": prod}, request=request
                )

            # 🚀 補丁四：重新編排回傳的 HTML 盒子
            # 利用 hx-swap-oob="beforeend:.grid"，強迫 HTMX 把裡面的卡片追加到你的 .grid 容器尾端
            success_html = f"""
                <div class="alert alert-success" style="padding: 1rem; background-color: oklch(0.85 0.05 140); border-radius: 0.5rem; margin-bottom: 1rem;">
                    🎉 {len(created_products)} 件商品上架成功！
                </div>
                
                <script>
                    (function() {{
                        
                        const activeGrid = document.getElementById("active-grid");
                        if (activeGrid) {{
                            const emptyHint = activeGrid.querySelector('.empty-hint');
                            if (emptyHint) emptyHint.remove();
                            activeGrid.insertAdjacentHTML("afterbegin", `{cards_html}`);
                        }}

                        // ❌ 【物理拔除這幾行！】不准在後端回傳時清空表單，否則後面批次會死
                        // const singleForm = document.getElementById("singleUploadForm");
                        // const batchForm = document.getElementById("batchUploadForm");
                        // if (singleForm) singleForm.reset();
                        // if (batchForm) batchForm.reset();

                        // 原本的圖片預覽清空依然保留...
                        document.querySelectorAll('.preview-img').forEach(img => {{ img.src = ""; img.style.display = 'none'; }});
                        document.querySelectorAll('.upload-placeholder').forEach(p => {{ p.style.display = ''; }});
                        document.querySelectorAll('.delete-prod-pic-btn').forEach(btn => {{ btn.style.display = 'none'; }});
                    }})();
                </script>
            """
            return HttpResponse(success_html)

        except Exception as e:
            return HttpResponse(f"儲存失敗：{str(e)}", status=400)


class ProductToggleActiveView(FisshPageBase, View):
    """🚀 終極合體：單一類別搞定商品 上架 / 下架 / 刪除"""

    def post(self, request, pk, action, *args, **kwargs):
        # 因：透過網址拿到商品 ID，並經由 FisshPageBase 安全鎖定 owner
        product = get_object_or_404(AquaticLife, pk=pk, owner=request.user)

        # 過：根據行為變數進行因果分流
        if action == "delist":
            product.is_active = False
            product.save()
        elif action == "relist":
            product.is_active = True
            product.save()

        # 💥 全新追加：物理刪除防線
        elif action == "delete":
            # 因果效應：呼叫 .delete() 會引發級聯反應（Cascade）
            # 資料庫會連帶把綁定這隻魚的副圖藝廊（AquaticImage）紀錄一併抹除
            product.delete()

        else:
            return HttpResponse("非法操作", status=400)

        # 果：統一回傳真空字串，告訴前端 JS 電流可以放行了
        return HttpResponse("")


class ShopListView(View):
    def get(self, request):

        # ────────────────────────────────────────────────────────
        # 💡 因果邏輯：全表查詢與效能優化
        # ────────────────────────────────────────────────────────
        # 因：要展示全站所有人的商品，且前端卡片一定會顯示「商家名稱（owner）」
        # 過：拿掉 filter(owner=...) 限制，改用 select_related("owner") 一口氣把發布者資料綁定進來
        # 果：避免產生 N+1 次 SQL 查詢地獄，一行指令抓出全站最新上架的生物
        aquatics = (
            AquaticLife.objects.filter(is_active=True)
            .select_related("owner")
            .order_by("-created_at")
        )

        context = {
            "items": aquatics,  # 變數名稱完全沿用，後端與前端絕對不相撞
        }
        return render(request, "shop.html", context)


class ProductDetailView(View):
    """
    🔗 小魚公開詳細頁面視圖
    因：需要展示特定生物的完整水族規格
    果：捞出單一 AquaticLife 物件並綁定 owner 資料，完全免登入開放
    """

    def get(self, request, product_id, *args, **kwargs):
        # 1. 抓取單一生物並預先載入 owner 關係，與 ShopListView 邏輯對稱
        product = get_object_or_404(
            AquaticLife.objects.select_related("owner"), id=product_id
        )

        context = {
            "product": product,  # 後端變數與你前端模板完全對齊
        }
        return render(request, "component/product-detail.html", context)


# 🎯 1. GET 類別：專門負責吐出編輯表單片段（降落在彈窗外殼）
class EditProfileFormView(FisshPageBase):
    # 🎯 物理關鍵：參數列加上 username 去接收 urls.py 射進來的動態網址變數
    def get(self, request, username, *args, **kwargs):

        # 🛡️ 鋼鐵因果防線：如果網址上的名字不是你本人，立刻物理阻斷、彈飛！
        if request.user.username != username:
            return HttpResponseForbidden("你不准偷看或編輯別人的格子！")

        # 以下因果邏輯維持不變
        profile, created = Profile.objects.get_or_create(user=request.user)

        current_city = ""
        current_zone = ""

        if profile.city_region:
            for city in TAIWAN_REGIONS.keys():
                if profile.city_region.startswith(city):
                    current_city = city
                    current_zone = profile.city_region.replace(city, "")
                    break

        context = {
            "profile": profile,
            "taiwan_regions": TAIWAN_REGIONS,
            "taiwan_regions_json": json.dumps(TAIWAN_REGIONS, ensure_ascii=False),
            "current_city": current_city,
            "current_zone": current_zone,
        }
        return render(request, "component/profile_edit_form.html", context)


# 🎯 2. POST 類別：專門負責接收彈窗數據，寫入 R2 並局部刷新前台
# 🎯 2. POST 類別：專門負責接收彈窗數據，寫入 R2 並局部刷新前台


# 🎯 2. POST 類別：專門負責接收彈窗數據，寫入 R2 並刷新前台
class UpdateProfileView(FisshPageBase):
    def post(self, request, username, *args, **kwargs):
        if request.user.username != username:
            return HttpResponseForbidden("你不准修改別人的格子！")

        profile = get_object_or_404(Profile, user=request.user)

        profile.nickname = request.POST.get("nickname", "").strip()
        profile.bio = request.POST.get("bio", "").strip()
        profile.city_region = request.POST.get("city_region", "").strip()
        profile.address_detail = request.POST.get("address_detail", "").strip()

        if "avatar" in request.FILES:
            profile.avatar = request.FILES["avatar"]
        if "background_image" in request.FILES:
            profile.background_image = request.FILES["background_image"]

        profile.save()

        # 🔄 關鍵修正：不再回傳局部 HTML，直接下達命令讓前端全自動 Reload
        from django.http import HttpResponse

        response = HttpResponse()
        response["HX-Refresh"] = "true"
        return response
