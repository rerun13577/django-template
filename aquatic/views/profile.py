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
    PRICE_VISIBILITY_CHOICES,
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
        # ────────────────────────────────────────────────────────
        # 🚀 新增：計算是否要對這個瀏覽者隱藏價格
        # ────────────────────────────────────────────────────────

        # 預設公開價格

        should_hide_price = False

        price_visibility = profile_owner.profile.price_visibility

        # 商家本人永遠可以在自己的頁面看到價格
        if not is_me:

            # 只有追蹤者可以看價格
            if price_visibility == "FOLLOWERS":
                should_hide_price = not is_following

            # 完全隱藏價格，追蹤者也看不到
            elif price_visibility == "HIDDEN":
                should_hide_price = True

            # PUBLIC 或異常值都保持公開
            else:
                should_hide_price = False
        context = {
            "target_user": profile_owner,
            "user": request.user,
            "posts": user_posts,
            "items": user_aquatics,
            "pets": user_pets,
            "is_me": is_me,
            "is_following": is_following,
            # 原始設定：PUBLIC / FOLLOWERS / HIDDEN
            "price_visibility": price_visibility,
            # 針對目前瀏覽者，最後是否應隱藏
            "should_hide_price": should_hide_price,
        }
        return render(request, "profile.html", context)


# POST 類別：專門負責接收彈窗數據，寫入 R2 並刷新前台
class UpdateProfileView(FisshPageBase):
    def post(self, request, username, *args, **kwargs):
        profile_owner = get_object_or_404(User, username=username)

        if request.user != profile_owner:
            return HttpResponseForbidden("錯誤，非本人")

        profile = get_object_or_404(Profile, user=profile_owner)

        profile.nickname = request.POST.get("nickname", "").strip()
        profile.bio = request.POST.get("bio", "").strip()
        profile.city_region = request.POST.get("city_region", "").strip()
        profile.address_detail = request.POST.get("address_detail", "").strip()

        # 修正：模型欄位叫 contact_link
        profile.contact_link = request.POST.get("contact_link", "").strip()

        # 接收價格顯示方式
        price_visibility = request.POST.get(
            "price_visibility",
            "PUBLIC",
        )

        # 防止有人自行修改 POST，傳入不存在的值
        if price_visibility not in dict(PRICE_VISIBILITY_CHOICES):
            price_visibility = "PUBLIC"

        profile.price_visibility = price_visibility

        if "avatar" in request.FILES:
            profile.avatar = request.FILES["avatar"]

        if "background_image" in request.FILES:
            profile.background_image = request.FILES["background_image"]

        profile.save()

        response = HttpResponse()
        response["HX-Refresh"] = "true"
        return response


# respone的頭檔就是一對鍵值對
# content是html檔案
# response["HX-Refresh"] = "true" 在頭檔塞入設定


# 這裡的 username 其實就是網站的擁有者
# 把使用者先前的資訊拆解 然後丟回去前端給他編輯
# 所以上面那個update是用來可以接收他塞回來的訊息的
class EditProfileView(FisshPageBase):
    def get(self, request, username, *args, **kwargs):
        profile_owner = get_object_or_404(User, username=username)

        if request.user != profile_owner:
            return HttpResponseForbidden("沒有權限做此操作")

        profile, created = Profile.objects.get_or_create(user=profile_owner)

        current_city, current_zone = split_taiwan_city_zone(profile.city_region)

        context = {
            "target_user": profile_owner,
            "profile": profile,
            "taiwan_regions": TAIWAN_REGIONS,
            "taiwan_regions_json": json.dumps(
                TAIWAN_REGIONS,
                ensure_ascii=False,
            ),
            "current_city": current_city,
            "current_zone": current_zone,
            # 提供給前端 select 使用
            "price_visibility_choices": PRICE_VISIBILITY_CHOICES,
        }

        return render(
            request,
            "component/profile_edit_form.html",
            context,
        )


# 🚀 專職處理追蹤開關的 API (必須登入才能按)
# 因為他會塞整個登入頁面回去 所以我不能讓他繼承基類
class ToggleFollowView(View):
    def post(self, request, username, *args, **kwargs):

        # 未登入時，交給 HTMX 進行整頁跳轉
        if not request.user.is_authenticated:
            response = HttpResponse()
            response["HX-Redirect"] = reverse("account_login")
            return response

        # 取得目標使用者與 Profile
        target_user = get_object_or_404(
            User.objects.select_related("profile"),
            username=username,
        )

        target_profile = target_user.profile

        # 不能追蹤自己
        if request.user == target_user:
            return HttpResponseForbidden("不能追蹤自己")

        # 切換追蹤狀態
        if target_profile.followers.filter(id=request.user.id).exists():
            target_profile.followers.remove(request.user)
            is_following = False
        else:
            target_profile.followers.add(request.user)
            is_following = True

        # 依照實際追蹤名單重新計算，避免 follower_count 發生誤差
        target_profile.follower_count = target_profile.followers.count()
        target_profile.save(update_fields=["follower_count"])

        # 使用 Django URL name 產生網址
        toggle_follow_url = reverse(
            "toggle_follow",
            kwargs={"username": username},
        )

        # 更新追蹤按鈕
        if is_following:
            btn_html = f"""
                <button type="button"
                        class="action-btn followed-btn"
                        hx-post="{toggle_follow_url}"
                        hx-target="this"
                        hx-swap="outerHTML">
                    已追蹤
                </button>
            """
        else:
            btn_html = f"""
                <button type="button"
                        class="action-btn follow-btn"
                        hx-post="{toggle_follow_url}"
                        hx-target="this"
                        hx-swap="outerHTML">
                    追蹤
                </button>
            """

        # 使用 OOB 同時更新粉絲數
        count_html = f"""
            <span class="follower-count"
                  id="follower-count-{username}"
                  hx-swap-oob="true">
                <strong>{target_profile.follower_count}</strong> 粉絲
            </span>
        """

        response = HttpResponse(btn_html + count_html)

        # 按鈕替換完成後，通知商品區重新取得內容
        response["HX-Trigger-After-Swap"] = "refreshProducts"

        return response
