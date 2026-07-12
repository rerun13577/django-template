# 這是最後渲染的工具
import json

# 🎯 終極防線：直接用 method_decorator 確保不管前端丟什麼 Method
from django.db import transaction
from django.http import (
    Http404,  # 這是用來拋出 404 的
    HttpResponse,  # 🚀 回傳成功或失敗的訊息給 JS
    HttpResponseForbidden,
)
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string  # 🚀 補上這行，紅燈當場熄滅
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

# 🎯 終極防線：直接用 method_decorator 確保不管前端丟什麼 Method
from aquatic.constants import (
    AQUATIC_CATEGORIES,
    CORE_SPECS_CONFIG,
    EXTRA_SPECS,  # 🚀 物理引入你的常數庫
)

# 2. 工具從 utils 檔案抓 🚀
# 我設定他的絕對路徑就不會抓錯了錯了
# 🚀 既然 CORE_SPECS 已經不存在了，就不要 import 它
# 1. Model 從 models 資料夾抓
from aquatic.models import (  # 🚀 核心修正：手動補上副圖模型  # 記得引入模型
    AquaticLife,
    Post,
    Profile,
    SpecTemplate,
)
from aquatic.models.shop_notice import ShopNotice

# 🚀 既然 CORE_SPECS 已經不存在了，就不要 import 它
# 1. Model 從 models 資料夾抓
# 🚀 因：從 utility 引入剛剛寫好的共用函式
from .utility import (
    FisshPageBase,
    get_active_product,
    get_bothtype_product,
    get_product_detail,
    main_process_fish_data,
)

# 2. 工具從 utils 檔案抓 🚀
# 我們分類不是分功能
# 從展示 上架 下架全部都寫一起


class ShopView(View):
    """賣場頁面展示小魚"""

    def get(self, request):
        # 1. 🚀 因：呼叫共用工具。果：拿到完美優化過的 QuerySet (包含所有的魚)
        context = get_active_product()

        # 2. 🚀 新增防線：準備「我的追蹤名單」彈藥包
        followed_user_ids = []
        if request.user.is_authenticated:
            # 去資料庫查出「我」有在哪些 Profile 的 followers 名單裡，並把他們的老闆 ID 抽出來
            followed_user_ids = list(
                Profile.objects.filter(followers=request.user).values_list(
                    "user_id", flat=True
                )
            )

        # 3. 🚀 物理接軌：把這包清單塞進 context 裡面，一起送給前端
        context["followed_user_ids"] = followed_user_ids

        return render(request, "shop.html", context)


# 因為我需要文章跟小魚
class IndexView(View):
    """首頁展示小魚與熱門文章"""

    def get(self, request):
        # 1. 先接住工具打包好的小魚包裹
        context = get_active_product()

        # 2. 把裡面的 "items" 拿出來切片 (LIMIT 10)
        context["items"] = context["items"][:10]

        # 🚀 3. 新增：抓取前 10 篇文章塞進 context
        # 因：這是 "熱門文章" (hot-article)
        # 果：所以我用 order_by('-like_count') 按點讚數由高到低排，再切片 [:10] 拿前十名
        # (如果你想拿最新文章，可以改成 order_by('-id') 或 '-created_at')
        context["hot_posts"] = Post.objects.order_by("-like_count")[:10]

        return render(request, "index.html", context)


# 後面兩個變數是接受來自網址的多餘變數
# *args所有「沒有名字」的多餘參數，打包成陣列（Tuple）
# kwargs集所有「有名字」的多餘參數，打包成字典（Dictionary）
# 例如/product/edit/<int:pk>/
@method_decorator(never_cache, name="dispatch")
class DashboardView(FisshPageBase):
    """商品管理頁面展示小魚"""

    def get(self, request, *args, **kwargs):
        # 🚀 果：View 的職責回歸純粹的「收發室」
        # 把 user 丟給共用函式，拿到整理好的包裹，直接轉發給 HTML
        context = get_bothtype_product(request.user)

        return render(request, "manage.html", context)


# 小魚的細節頁面 大家都可以看
class ProductDetailView(View):
    def get(self, request, product_id, *args, **kwargs):
        product = get_product_detail(product_id)

        # 加個防呆：如果魚不見了，直接回傳 404
        if not product:
            # 這裡特別用raise是因為要跳出頁面
            raise Http404("找不到這條魚")

        context = {
            "product": product,
        }
        return render(request, "component/product-detail.html", context)


# 繼承的底層邏就是如果我不會就找我老爸 fisshpagebase
# 我在所有的view裡面都沒有處理登入 但我有一個總老爸可以幫我處理登入
# 所以我需要做的只是問他就好
# 我這裡本來有繼承兩個FisshPageBase view 但因為我的FisshPageBase本身又繼承view
# 所以我往上找兩層就會有 所以我在這裡不用call view這個 class
class ToggleProductActiveView(FisshPageBase):
    """搞定商品 上架 / 下架 / 刪除"""

    def post(self, request, pk, action, *args, **kwargs):
        # 因：透過網址拿到商品 ID，並經由 FisshPageBase 安全鎖定 owner
        product = get_object_or_404(AquaticLife, pk=pk, owner=request.user)

        # 過：根據行為變數進行因果分流
        if action == "delist":
            product.is_active = False
            # 我只更新這個欄位，減少不必要的資源浪費
            product.save(update_fields=["is_active"])
        elif action == "relist":
            product.is_active = True
            # 我只更新這個欄位
            product.save(update_fields=["is_active"])

        # 💥 全新追加：物理刪除防線
        elif action == "delete":
            # 因果效應：呼叫 .delete() 會引發級聯反應（Cascade）
            # 資料庫會連帶把綁定這隻魚的副圖藝廊（AquaticImage）紀錄一併抹除
            product.delete()

        else:
            return HttpResponse("非法操作", status=400)

        # 果：統一回傳真空字串，告訴前端 JS 電流可以放行了
        return HttpResponse("")


# 把你的東西都打包成一個字典 然後用跟修改一樣的格式送進去我們的共用裡面
class EditProductView(FisshPageBase):  # 完美繼承你的基類
    def get(self, request, pk, *args, **kwargs):
        """
        GET 開啟彈窗電路：負責把舊資料（含 JSON 規格與多圖）還原並塞回格子
        """
        # 抓出這個小魚的id 如果抓不到就直接404
        # 驗證現在逛網頁的人（request.user）有沒有權限開啟這張編輯卡片
        fish = get_object_or_404(AquaticLife, pk=pk)
        if request.user != fish.owner:
            return HttpResponseForbidden("沒有權限做此操作")

        # 將 JSON 字串逆向解析為 Python 字典
        fish_specs = fish.specs_json
        # 先判斷他是不是字串
        if isinstance(fish_specs, str):
            # 是字串 我就把他變成字典
            # 裡面的文字出錯我就跳出 然後給這個小魚資訊一個空字典
            try:
                fish_specs = json.loads(fish_specs)
            except ValueError:
                fish_specs = {}

        # 打包傳輸給前端表單，鍵值（Key）物理鎖死，完美還原前端變數
        context = {
            "target_user": fish.owner,  # 🎯 鍵值還原：前端只認 target_user
            "item": fish,
            "fish_specs": fish_specs,
            "category_display": AQUATIC_CATEGORIES.get(fish.category, "其他"),
            "spec_templates": SpecTemplate.objects.filter(user=fish.owner),
            "notices": ShopNotice.objects.filter(user=fish.owner),
            "core_config": CORE_SPECS_CONFIG,
            "extra_labels": EXTRA_SPECS,
        }
        return render(request, "component/edit-product-form.html", context)

    def post(self, request, pk, *args, **kwargs):
        """
        🟢 POST 存檔電路：只負責攔截權限、外包處理、以及回傳畫面
        """
        # 1. 櫃台身分查驗
        fish = get_object_or_404(AquaticLife, pk=pk)
        if request.user != fish.owner:
            return HttpResponseForbidden("你不准修改別人的格子！")

        try:
            # 2. 🎯 核心解耦：調用大總管函數！
            # 傳入舊的 fish 物件、request.POST、request.FILES
            # 物理因果：因為沒有傳入 index，內部會自動採用單筆處理邏輯
            main_process_fish_data(
                the_fish=fish, post_data=request.POST, files_data=request.FILES
            )

            # 3. 廚房處理完畢，櫃台負責把最新鮮的卡片端給客人 (HTMX 回傳)
            response = render(
                request, "component/new-creature-card.html", {"item": fish}
            )

            # 🚀 物理通電：在封包貼上 HTMX 專屬指令，命令前端「關閉編輯彈窗」
            response["HX-Trigger"] = "closeEditModal"

            return response

        except ValueError as ve:
            # 這裡專門接住大總管內部四個零件（如價格非數字、提醒不可為空）丟出來的警報
            return HttpResponse(str(ve), status=400)

        except Exception as e:
            # 終極防護網
            return HttpResponse(f"儲存失敗！後端原因: {str(e)}", status=400)


# get 是專門你有key來找value的 所以你有 你的字典名子.get(key)這樣就可以拿到名子
# 下面是批量上架跟單獨上架的組合view
class AddProductView(FisshPageBase, View):
    def post(self, request, *args, **kwargs):
        # 🚀 1. 單筆上傳，直接用單一的 get 抓取名字
        fish_name = request.POST.get("fish_name", "").strip()

        # 第一道防線
        if not fish_name:
            return HttpResponse("商品名稱不可為空", status=400)

        try:
            # 大閘門防線：有錯就物理回滾
            with transaction.atomic():
                # 1. 建立生物主體與城市綁定
                new_fish = AquaticLife(owner=request.user)
                if hasattr(request.user, "city") and request.user.city:
                    new_fish.city = request.user.city

                # 2. 🎯 核心解耦：直接呼叫大總管，不需要任何 index 參數了
                main_process_fish_data(new_fish, request.POST, request.FILES)

            # 3. 廚房處理完畢，利用 HTMX 渲染最新鮮的卡片
            card_html = render_to_string(
                "component/new-creature-card.html", {"item": new_fish}, request=request
            )

            # 🚀 4. 回傳成功訊息與影片清理腳本
            success_html = f"""
                <div class="alert alert-success" style="padding: 1rem; background-color: oklch(0.85 0.05 140); border-radius: 0.5rem; margin-bottom: 1rem;">
                    🎉 商品上架成功！
                </div>
                
                <script>
                    (function() {{
                        // 把新卡片推入畫面上方的 Grid
                        const activeGrid = document.getElementById("active-grid");
                        if (activeGrid) {{
                            const emptyHint = activeGrid.querySelector('.empty-hint');
                            if (emptyHint) emptyHint.remove();
                            activeGrid.insertAdjacentHTML("afterbegin", `{card_html}`);
                        }}

                        // 📹 影片預覽清空重置 (對齊影片 UI)
                        const bigVideo = document.querySelector(".viewport-video");
                        const bigPlaceholder = document.querySelector(".viewport-placeholder");
                        const deleteBtn = document.querySelector(".delete-prod-pic-btn");

                        if (bigVideo) {{
                            bigVideo.pause();
                            bigVideo.removeAttribute('src');
                            bigVideo.load();
                            bigVideo.style.display = "none";
                        }}
                        if (bigPlaceholder) {{
                            bigPlaceholder.style.setProperty('display', 'flex', 'important');
                        }}
                        if (deleteBtn) {{
                            deleteBtn.style.setProperty('display', 'none', 'important');
                        }}

                        // 清空表單的所有文字與數字輸入
                        const form = document.getElementById("singleUploadForm");
                        if (form) form.reset();
                    }})();
                </script>
            """
            return HttpResponse(success_html)

        except ValueError as ve:
            # 接住大總管拋出的防呆警報
            return HttpResponse(f"上架失敗：{str(ve)}", status=400)

        except Exception as e:
            # 終極防護網
            return HttpResponse(f"儲存失敗：{str(e)}", status=400)
