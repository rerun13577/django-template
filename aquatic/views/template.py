# 🚀 核心刪除同步補丁：利用正則表達式物理清除字串記憶體，並拔除畫面 option
# IIFE 例如：(function() { ... })();是一個用完就丟的函式
# 我就可以避免我按兩次 導致內部變數重複宣告
# 我就是挑出我要的刪除的數字出來 deletedId]
# const regex = new RegExp('<option value="' + deletedId + '">.*?</option>', 'g');
# ：. 代表「任何字元」
# * 代表「不管有幾個字」
# ?代表遇到第一個標籤結尾就要收手
# g代表的是全域掃描 有這個id的範本都給我丟給regex
# GLOBAL_NOTICE_OPTIONS = GLOBAL_NOTICE_OPTIONS.replace(regex, '');
# 我把regex換成空字串
# ('select[name="fish_notice[]"], select[name="global_notice"], #global_notice')
# 因為我網頁上可以很多卡片同時輸入 所以我叫所有選單都來給我刪掉
# const opt = select.querySelector('option[value="' + deletedId + '"]');
# 因為擴號裡面只能塞一包純字串 但我已經是字串的所以只能用 (前面的)+deletedId+(後面的)

# 這是最後渲染的工具
from django.http import (
    HttpResponse,  # 🚀 回傳成功或失敗的訊息給 JS
)
from django.shortcuts import render

from aquatic.constants import CORE_SPECS_CONFIG, EXTRA_SPECS
from aquatic.models import (  # 🚀 核心修正：手動補上副圖模型  # 記得引入模型
    ShopNotice,
    SpecTemplate,
)

# 我設定他的絕對路徑就不會抓錯了錯了
from .utility import FisshAPIBase, get_delete_script, get_update_script

# 🚀 因：從 utility 引入剛剛寫好的共用函式
# 你的GLOBAL_NOTICE_OPTIONS就是所有提醒範本的總清單，這會在單獨上架的引入範本裡面隨時顯示出來
# 因為要顯示正確所以要隨時更新
# RegExp他是根據你設定的「文字結構規則」去模糊比對出符合特定條件的所有片段
# 後端不可以重新loading所有選單，所以前端要寫一個可以重新loading的 然後後端負責觸發他


# 1. 範本提醒 API
# 上面是在處理我管理範本的展示邏輯
# 下面是在修改我新增小魚的下拉選單展示
# 然後我每個處理都要處理他的 刪 改 新增
class NoticeAPIView(FisshAPIBase):
    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            notice = ShopNotice.objects.get(id=pk, user=request.user)
            return render(request, "partials/notice_edit_form.html", {"n": notice})
        return HttpResponse("找不到範本", status=400)

    def post(self, request, *args, **kwargs):
        temp_id = request.POST.get("id")
        action = request.POST.get("action")

        # 定義這支 View 的座標系統
        global_var = "GLOBAL_NOTICE_OPTIONS"
        selector = (
            'select[name="fish_notice"], select[name="global_notice"], #global_notice'
        )

        # --- 1. 刪除分支 (Fast-path) ---
        if action == "delete":
            ShopNotice.objects.filter(id=temp_id, user=request.user).delete()
            # 直接返回刪除腳本，完事！
            return HttpResponse(get_delete_script(temp_id, global_var, selector))
        # --- 2. 儲存/更新分支 (Main-path) ---
        else:
            title = request.POST.get("title", "").strip()
            content = request.POST.get("content", "").strip()

            if not title or not content:
                return HttpResponse("內容不可為空", status=400)

            notice_obj, created = ShopNotice.objects.update_or_create(
                id=temp_id if temp_id else None,
                user=request.user,
                defaults={"title": title, "content": content},
            )

            # 撈清單並渲染 HTML
            notices = ShopNotice.objects.filter(user=request.user).order_by(
                "-created_at"
            )
            response = render(
                request, "component/notice_list_items.html", {"notices": notices}
            )

            # 注入同步腳本
            sync_script = get_update_script(
                notice_obj.id, notice_obj.title, global_var, selector
            )
            response.content = response.content + sync_script.encode("utf-8")
            return response


# 有這些key的資料我不要
# 然後value沒填的資料我不要
# # 下面那三行是反過來讀的
# # 1. 先準備一個空的乾淨箱子
# spec_data = {}
# 2. 把前端送來的資料，一組一組拿出來一個item是k：v加起來的
# # for k, v in request.POST.items():
#     # 3. 過兩道安檢門 你要通過not in exclude_keys還有v.strip() != ""
#      如果不等於就會是true
#     if k not in exclude_keys and v.strip() != "":
#         # 4. 安檢通過，把這組資料放進箱子裡
#         spec_data[k] = v


# 2. 規格範本 API (負責 存/改/刪)
class SpecAPIView(FisshAPIBase):
    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            # 找到該規格，並丟給一個編輯表單頁面
            spec = SpecTemplate.objects.get(id=pk, user=request.user)
            return render(request, "component/spec_edit_form.html", {"spec": spec})
        return HttpResponse("找不到範本", status=400)

    def post(self, request, *args, **kwargs):
        try:
            temp_id = request.POST.get("id")
            action = request.POST.get("action")
            name = request.POST.get("name")

            # --- 1. 刪除邏輯 ---
            if action == "delete":
                # 物理消滅資料庫紀錄
                SpecTemplate.objects.filter(id=temp_id, user=request.user).delete()

                # 定義規格選單的專屬座標
                global_var = "GLOBAL_SPEC_OPTIONS"
                selector = 'select[name="fish_spec[]"], select[name="global_spec"], #global_spec'

                # 🚀 直接呼叫工廠函數產出腳本並回傳，乾淨俐落！
                return HttpResponse(get_delete_script(temp_id, global_var, selector))

            # --- 2. 儲存/更新分支 (Main-path) ---
            else:
                if not name:
                    return HttpResponse("規格名稱不能為空", status=400)

                exclude_keys = ["id", "action", "name", "csrfmiddlewaretoken"]

                # 因為前端送過來的通常是一個很大的post字典
                spec_data = {
                    k: v
                    for k, v in request.POST.items()
                    if k not in exclude_keys and v.strip() != ""
                }

                # 如果有就修改如果沒有就創造
                spec_obj, created = SpecTemplate.objects.update_or_create(
                    id=temp_id if temp_id else None,
                    user=request.user,
                    defaults={"name": name, "data": spec_data},
                )

                # --- 3. 獲取原有的清單 HTML 回傳（呼叫下方補好的工具） ---
                response = self.render_spec_list(request)

                # 核心因果同步線：利用 JS 強行修改前端記憶體與即時選單
                global_var = "GLOBAL_SPEC_OPTIONS"
                selector = (
                    'select[name="fish_spec"], select[name="global_spec"], #global_spec'
                )

                sync_script = get_update_script(
                    spec_obj.id, spec_obj.name, global_var, selector
                )

                # 這裡就不會再噴 NoneType 錯誤了，因為 response 拿到了實體物件
                response.content = response.content + sync_script.encode("utf-8")
                return response

        except Exception as e:
            # 🚀 對齊 HTMX 標準：把原本的 JsonResponse 換成 HttpResponse
            return HttpResponse(f"系統發生錯誤：{str(e)}", status=500)

    # 🚀 實體修復線：把原本洗掉的渲染代碼刻回來
    def render_spec_list(self, request):
        # 1. 撈出該用戶的實體規格資料
        spec_templates = SpecTemplate.objects.filter(user=request.user).order_by("-id")

        # 2. 把所有必備零件打包發射給前端 HTML
        return render(
            request,
            "component/spec_list_items.html",
            {
                "spec_templates": spec_templates,
                "templates": spec_templates,
                # 直接吃常數檔裡定義好的底層協議
                "core_config": CORE_SPECS_CONFIG,
                "extra_labels": EXTRA_SPECS,
            },
        )
