# 🎯 終極防線：直接用 method_decorator 確保不管前端丟什麼 Method
import json  # 🚀 處理前端傳來的 JSON 字串

from django.contrib.auth.models import User

# 這是最後渲染的工具
from django.http import (
    HttpResponse,
    HttpResponseForbidden,  # 🛡️ 引入禁止存取的物理訊號
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse  # 記得在上方 import 這個
from django.views import View

from aquatic.constants import (
    TAIWAN_REGIONS,  # 🚀 物理引入你的常數庫
)

# 🚀 既然 CORE_SPECS 已經不存在了，就不要 import 它
# 1. Model 從 models 資料夾抓
from aquatic.models import (  # 🚀 核心修正：手動補上副圖模型  # 記得引入模型
    AquaticLife,
    PetFish,
    Profile,
)

# 2. 工具從 utils 檔案抓
# 我設定他的絕對路徑就不會抓錯了錯了
# 🚀 因：從 utility 引入剛剛寫好的共用函式
from .utility import (
    FisshPageBase,
    get_user_profile_posts,
    split_taiwan_city_zone,
)


# 這裡都是只有瀏覽的
class ProfileView(View):  # 改繼承純粹的 View，解除強迫登入的物理鎖
    def get(self, request, username=None):

        # ────────────────────────────────────────────────────────
        # 1.網址「沒帶名字」的情境 (例如直接按導覽列的 /profile/)
        # ────────────────────────────────────────────────────────
        if not username:
            if request.user.is_authenticated:
                # 有登入但沒帶名字 就自動重導向到他自己的專屬頁面
                return redirect("user_profile", username=request.user.username)
            else:
                # 因：沒登入也沒帶名字。果：不知道要看誰，物理踢去登入頁面
                return redirect("account_login")

        # ────────────────────────────────────────────────────────
        # 2.可以順便解決N+1 查詢 然後抓順便抓他的頭貼
        # ────────────────────────────────────────────────────────
        user_qs = User.objects.select_related("profile").prefetch_related(
            "socialaccount_set"
        )

        # 抓取目標使用者，不存在就噴 404
        # 左邊是資料庫的欄位 右邊是我手上的正要進來的人
        profile_owner = get_object_or_404(user_qs, username=username)

        # ────────────────────────────────────────────────────────
        # 3.區分「看自己」與「看別人」的資料庫優化防線
        # ────────────────────────────────────────────────────────

        # 把後面的東西存入布林直 如果兩個相等就是true
        # 後面的request.user是現在正在逛網頁的人 前面的profile_owner是這個個人頁面的主人
        is_me = request.user == profile_owner

        # 處理貼文與點讚狀況（呼叫抽離出去的物理工人）
        user_posts = get_user_profile_posts(profile_owner, request.user)

        # annotate是利用計算加權的一張紙，我只看他真假，或者單一數值

        # 💡 因果邏輯：如果是「看自己」，可能需要看到下架或隱藏的魚；
        # 但你給的邏輯是統一 filter(is_active=True)，這裡完全沿用你的物理變數
        user_aquatics = AquaticLife.objects.filter(
            owner=profile_owner, is_active=True
        ).order_by("-created_at")

        # 先沒有
        user_pets = PetFish.objects.filter(owner=profile_owner).order_by("-created_at")

        # ────────────────────────────────────────────────────────
        # 🚀 第四關：打包傳輸
        # ──────────────────────────────────────────────

        # ────────────────────────────────────────────────────────
        # 🚀 新增：計算目前登入者是否有追蹤這個人 (重整頁面時的物理防線)
        # ────────────────────────────────────────────────────────
        is_following = False
        # 必須確保有登入，且不是看自己的頁面，才去資料庫觸發 O(log N) 查詢
        if request.user.is_authenticated and not is_me:
            # 🎯 物理修正：使用畫面上方已經定義好的 profile_owner，然後加上 .profile 跨表
            is_following = profile_owner.profile.followers.filter(
                id=request.user.id
            ).exists()
        # 左邊是給前端的 右邊是我這裡在用的
        context = {
            "target_user": profile_owner,
            "user": request.user,
            "posts": user_posts,
            "items": user_aquatics,  # 變數名稱物理鎖死，完美對接
            "pets": user_pets,
            "is_me": is_me,  # 順手塞一個布林值給前端，讓你方便隱藏「編輯個人資料」的按鈕
            # 🎯 物理接軌：補上前端模板正在呼叫的 profile 變數！
            "is_following": is_following,  # 🎯 關鍵：把算好的布林值丟給前端
        }
        return render(request, "profile.html", context)


# POST 類別：專門負責接收彈窗數據，寫入 R2 並刷新前台
class UpdateProfileView(FisshPageBase):
    def post(self, request, username, *args, **kwargs):

        # 🎯 第一步：去 User 表裡，把網址指定的那個「頁面擁有者」找出來
        profile_owner = get_object_or_404(User, username=username)

        # 🎯 第二步：嚴格卡死權限（現在按按鈕的人 request.user，必須跟頁面擁有者 profile_owner 是一模一樣的人）
        if request.user != profile_owner:
            return HttpResponseForbidden("錯誤 非本人")

        # 🎯 第三步：既然確定是你本人，我們用這個擁有者的帳號去撈他的 Profile 卡片
        profile = get_object_or_404(Profile, user=profile_owner)
        # 如果你沒有profile 卻想改profile 那就噴錯

        # ────────────────────────────────────────────────────────
        # 後面老老實實填空塞資料，物理搬運
        # ────────────────────────────────────────────────────────

        profile.nickname = request.POST.get("nickname", "").strip()
        profile.bio = request.POST.get("bio", "").strip()
        profile.city_region = request.POST.get("city_region", "").strip()
        profile.address_detail = request.POST.get("address_detail", "").strip()
        profile.line_link = request.POST.get("contact_link", "").strip()

        # 因為前端送回來的post只會是文字 但是檔file理面
        if "avatar" in request.FILES:
            profile.avatar = request.FILES["avatar"]
        if "background_image" in request.FILES:
            profile.background_image = request.FILES["background_image"]

        profile.save()
        # 🔄 關鍵修正：不再回傳局部 HTML，直接下達命令讓前端全自動 Reload
        # 這裡宣告他是一個HttpResponse()物件
        # python他創造新的物件不需要new
        response = HttpResponse()
        # 這個可以叫前端重整
        response["HX-Refresh"] = "true"
        return response


# respone的頭檔就是一對鍵值對
# content是html檔案
# response["HX-Refresh"] = "true" 在頭檔塞入設定


# 這裡的 username 其實就是網站的擁有者
# 把使用者先前的資訊拆解 然後丟回去前端給他編輯
# 所以上面那個update是用來可以接收他塞回來的訊息的
class EditProfileView(FisshPageBase):
    # 🎯 物理關鍵：參數列加上 username 去接收 urls.py 射進來的動態網址變數
    def get(self, request, username, *args, **kwargs):

        # 🎯 第一步：去 User 表裡，把網址指定的那個「頁面擁有者」找出來
        profile_owner = get_object_or_404(User, username=username)

        # 🛡️ 鋼鐵因果防線：如果網址上的名字不是你本人，立刻物理阻斷、彈飛！
        if request.user != profile_owner:
            return HttpResponseForbidden("沒有權限做此操作")

        # 如果沒有就創造 如果有就是修改 create會表示是新的還是修改
        profile, created = Profile.objects.get_or_create(user=profile_owner)

        # 🎯 第二步：把字串丟給專屬工廠去拆解，View 只要拿結果就好
        current_city, current_zone = split_taiwan_city_zone(profile.city_region)

        # 我函數裡面可能會有多格 但我不一定會全部且出來
        # 這就是我false前面要且變數的原因是因為我要寫我要輸入的格子
        # json.dump會把非英文的所有字元都轉換成ascll碼
        # ensure_ascii=False但是我後面叫他不要轉
        context = {
            "target_user": profile_owner,  # 變數名稱與全站因果鎖死對齊
            "profile": profile,  # 我已經把整包profile都塞進去了
            # 這是台灣全部的區域
            "taiwan_regions": TAIWAN_REGIONS,
            "taiwan_regions_json": json.dumps(TAIWAN_REGIONS, ensure_ascii=False),
            # 這個是他現在所在的區域 跟城市
            "current_city": current_city,
            "current_zone": current_zone,
        }
        return render(request, "component/profile_edit_form.html", context)


# 🚀 專職處理追蹤開關的 API (必須登入才能按)
# 因為他會塞整個登入頁面回去 所以我不能讓他繼承基類
class ToggleFollowView(View):
    def post(self, request, username, *args, **kwargs):

        # 🚀 0. 物理防線第一關：未登入者強制整頁轉向
        if not request.user.is_authenticated:
            # 建立一個空的 HttpResponse
            response = HttpResponse()
            # 塞入 HTMX 專用的轉向標頭，告訴它「不要替換 HTML，直接幫我跳轉網頁」
            response["HX-Redirect"] = reverse("account_login")
            return response

        # 1. 抓出目標使用者與他的 profile
        target_user = get_object_or_404(User, username=username)
        target_profile = target_user.profile

        # 🎯 物理防線：不能追蹤自己
        if request.user == target_user:
            return HttpResponseForbidden("不能追蹤自己")

        # 2. 物理判定：現在這個人，到底在不在追蹤名單裡？
        if target_profile.followers.filter(id=request.user.id).exists():
            # 因：已經在名單裡。果：執行退追邏輯
            target_profile.followers.remove(request.user)
            target_profile.follower_count -= 1
            is_following = False
        else:
            # 因：不在名單裡。果：執行追蹤邏輯
            target_profile.followers.add(request.user)
            target_profile.follower_count += 1
            is_following = True

        target_profile.save()

        # ────────────────────────────────────────────────────────
        # 3. 準備發送給前端的局部 HTML
        # ────────────────────────────────────────────────────────

        # A. 主目標：抽換原本按鈕 (會被丟進 hx-target="this" 裡面)
        if is_following:
            btn_html = f"""
            <button type="button" 
                    class="action-btn followed-btn" 
                    hx-post="/profile/{username}/toggle_follow/" 
                    hx-target="this" 
                    hx-swap="outerHTML">已追蹤</button>
            """
        else:
            btn_html = f"""
            <button type="button" 
                    class="action-btn follow-btn" 
                    hx-post="/profile/{username}/toggle_follow/" 
                    hx-target="this" 
                    hx-swap="outerHTML">追蹤</button>
            """

        # 🚀 B. 隔山打牛 (OOB) 目標：精準更新右上角的粉絲數字
        # 物理因果：只要標籤有 hx-swap-oob="true"，且 ID 對得上，HTMX 就會自動飛過去把它換掉
        count_html = f"""
        <span class="follower-count" id="follower-count-{username}" hx-swap-oob="true">
            <strong>{target_profile.follower_count}</strong> 粉絲
        </span>
        """

        # 🎯 將兩個 HTML 零件黏在一起，一次回傳給前端
        return HttpResponse(btn_html + count_html)
