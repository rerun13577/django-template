# 🎯 終極防線：直接用 method_decorator 確保不管前端丟什麼 Method
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Exists, OuterRef
from django.http import (
    JsonResponse,  # 🚀 回傳成功或失敗的訊息給 JS
)
from django.views import View

from aquatic.constants import (
    CORE_SPECS_CONFIG,
    EXTRA_SPECS,
    FISH_SPECS_LABELS,
    REVERSE_AQUATIC_CATEGORIES,
    TAIWAN_REGIONS,
)
from aquatic.models import AquaticImage, AquaticLife, Post, ShopNotice, SpecTemplate
from aquatic.utils import compress_image


# 如果你從網址直接輸入需要登入的地方他就會把你踢回去
# 所以大多數都是繼承這個
# 當我作為多重繼承 我就是從左找到右 看誰會我就給誰
class FisshPageBase(LoginRequiredMixin, View):
    login_url = "/accounts/login/"
    redirect_field_name = "next"


# 如果你沒有登入但是按讚用的是這個
# 我沒有繼承是因為這個是要顯示給人家看的
# 我上面那個不用顯示給人家看所以他直接繼承官方
# 但我要客製化所以我沒有繼承
# 但他就是不會導向
class FisshAPIBase(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # 🚀 關鍵：不回傳 redirect，而是回傳 JsonResponse
            # 我傳回去js會用data函數去call
            # window.location.href = data.login_url;之類的
            return JsonResponse(
                {
                    "status": "unauthorized",
                    "message": "請先登入才能操作喔！",
                    "login_url": f"/accounts/login/?next={request.path}",
                },
                status=401,
            )  # 401 代表「未經授權」
        # 如果走到這裡代表他經過授權了，
        # 我就會會帶他去dispatch裡面去判斷他要用的是啥方法post 或者get
        return super().dispatch(request, *args, **kwargs)


# view裡面有包含dispatch函數
# super代表的是super class 代表我呼叫我老爸裡面的函數
# 然後把老爸裡面的dispatch函數拿出來用，所以我還要用view來搞
# 因為dispatch他是view裡面的東西所以我不可以直接import view然後就可以拿裡面的東西
# 我要先繼承再拿他裡面的函數


# 這是抓多種小魚的瀏覽資訊(所有人的小魚 包含自己)
def get_active_product():
    """因為我使用者是外鍵 所以他不會主動去查詢我需要叫他順便查詢"""
    # select_related("owner")他可以順便抓其他東西
    # 這裡的意思就是順便抓使用者的名子

    products = (
        AquaticLife.objects.filter(is_active=True)
        .select_related("owner")
        .order_by("-created_at")
    )
    # 鍵值對必須裝在大擴號裡面
    return {
        "items": products,
    }


# 抓單一小魚的各種詳細資料
def get_product_detail(product_id):
    """
    專門獲取單一產品詳細資訊的工具。
    """
    # 直接用 get_object_or_404 的邏輯拆分出來
    return AquaticLife.objects.select_related("owner").filter(id=product_id).first()


# 這是抓管理頁面的小魚資訊
def get_bothtype_product(user):
    # 我把回傳小魚的資料統一管理因為小魚的配件太多了一個個寫會很麻煩

    # 先把這個user資料都抓出來
    products = AquaticLife.objects.filter(owner=user).order_by("-created_at")

    # 然後在把他的資料做過濾
    active_products = products.filter(is_active=True)
    inactive_products = products.filter(is_active=False)

    # 3. 整合並回傳 Context 字典
    return {
        "items": products,
        "active_items": active_products,
        "inactive_items": inactive_products,
        "notices": ShopNotice.objects.filter(user=user).order_by("-created_at"),
        "spec_templates": SpecTemplate.objects.filter(user=user).order_by("-id"),
        "core_config": CORE_SPECS_CONFIG,
        "extra_labels": EXTRA_SPECS,
        "master_labels": FISH_SPECS_LABELS,
        "target_user": user,
    }


# 下面顯示非同步的範本scrpit的邏輯
# 為什麼不能後面全部抓起來丟前面要用加的是因為我不能讓客人已經選好的東西改變
# 這樣我刪除的邏輯就必定是把原本的抽出來刪掉
# 然後新增的是把多的丟出去
def get_delete_script(item_id, global_var, selector):
    """產出刪除選項的 JavaScript (附帶高強度雷達與引號防禦)"""
    return f"""
    <script>
        (function() {{
            console.log("⚡ [刪除電路通電] 開始執行！準備拔除 ID:", "{item_id}");
            const deletedId = "{item_id}";
            
            // 檢查全域變數
            if (typeof {global_var} !== 'undefined') {{
                const regex = new RegExp('<option value="' + deletedId + '">.*?</option>', 'g');
                {global_var} = {global_var}.replace(regex, '');
                console.log("🧹 [1/2] 全域變數", '{global_var}', "清理完成。");
            }} else {{
                console.log("ℹ️ [1/2] 沒找到全域變數", '{global_var}', "，跳過。");
            }}

            // 檢查畫面上的下拉選單
            const selects = document.querySelectorAll('{selector}');
            
            // 🚀 修正：用逗號分隔，避免 selector 裡的雙引號把 console.log 炸斷！
            console.log("🔍 [2/2] 雷達掃描 CSS 選擇器:", '{selector}', "，找到:", selects.length, "個選單");
            
            selects.forEach(select => {{
                // 🚀 順便幫你換成反引號，尋找精準度更高，不怕單雙引號衝突
                const opt = select.querySelector(`option[value="${{deletedId}}"]`);
                
                if (opt) {{
                    opt.remove();
                    console.log("✅ 成功從畫面上拔除該選項！");
                }} else {{
                    console.log("⚠️ 警告：選單找到了，但裡面沒有 value 是", deletedId, "的選項。");
                }}
            }});
        }})();
    </script>
    """


def get_update_script(item_id, item_name, global_var, selector):
    """產出新增/修改選項的 JavaScript (引號防衝突安全版)"""
    return f"""
    <script>
        (function() {{
            const newId = "{item_id}";
            const newName = "{item_name}";
            
            // 🚀 修正 1：用逗號分隔參數，不把變數硬塞進雙引號字串裡
            console.log("⚡ [更新電路通電] ID:", newId, "名稱:", newName);
            
            const newOptHtml = `<option value="${{newId}}">${{newName}}</option>`;

            if (typeof {global_var} !== 'undefined') {{
                const regex = new RegExp('<option value="' + newId + '">.*?</option>', 'g');
                
                if (regex.test({global_var})) {{
                    {global_var} = {global_var}.replace(regex, newOptHtml);
                    console.log("🔄 [1/2] 全域變數已覆寫更新舊選項。");
                }} else {{
                    {global_var} += newOptHtml;
                    console.log("➕ [1/2] 全域變數已新增全新選項。");
                }}
            }} else {{
                console.log("ℹ️ [1/2] 沒找到全域變數", '{global_var}', "，跳過。");
            }}

            const selects = document.querySelectorAll('{selector}');
            
            // 🚀 修正 2：用逗號分隔，徹底避免 selector 裡面的雙引號把 console.log 炸斷！
            console.log("🔍 [2/2] 雷達掃描 CSS 選擇器:", '{selector}', "，找到:", selects.length, "個選單");

            selects.forEach(select => {{
                const existingOpt = select.querySelector(`option[value="${{newId}}"]`);
                
                if (!existingOpt) {{
                    const opt = document.createElement('option');
                    opt.value = newId; 
                    opt.textContent = newName;
                    select.appendChild(opt);
                    console.log("✅ 成功在畫面上新增一筆選項！");
                }} else {{
                    existingOpt.textContent = newName;
                    console.log("🔄 成功在畫面上更新舊有選項名稱！");
                }}
            }});
        }})();
    </script>
    """


def get_user_profile_posts(profile_owner, viewer_user):
    """
    因：區分「遊客」與「會員」的點讚資料庫優化防線
    果：回傳加工完成、帶有 is_liked 屬性的貼文清單，完全防止 SQL 崩潰
    """
    # 基礎查詢：先撈出這個人的所有貼文並依照時間倒序排好
    posts_queryset = (
        Post.objects.filter(author=profile_owner)
        .select_related("author")
        .order_by("-created_at")
    )

    # 身分分流物理邏輯
    if not viewer_user.is_authenticated:
        # 沒登入的人看別人：物理上「不可能有點讚紀錄」，直接硬編碼為 False，不查點讚表
        for post in posts_queryset:
            post.is_liked = False
    else:
        # 有登入（看自己或看別人）：啟動 Exists 點讚雷達
        posts_queryset = posts_queryset.annotate(
            # 後面的exists函數如果有就是true他不會看裡面內容
            is_liked=Exists(
                # 我這裡個按讚表過濾條件要是找這篇文章的id
                # 找這個要求用戶的id 有兩個都存在那就是這個人有按讚
                # 不管你是誰這裡個過濾邏輯都會一樣因為你也可以按讚妳自己
                Post.likes.through.objects.filter(
                    # 我的outerref 他是去看外面的post的id是什麼
                    post_id=OuterRef("pk"),
                    user_id=viewer_user.id,
                )
            )
        )

    return posts_queryset


def split_taiwan_city_zone(city_region_str):
    """
    🎯 物理抽離：專門把 "新北市中和區" 拆解成 ("新北市", "中和區") 的純文字加工廠
    """
    current_city = ""
    current_zone = ""

    if city_region_str:
        for city in TAIWAN_REGIONS.keys():
            if city_region_str.startswith(city):
                current_city = city
                current_zone = city_region_str.replace(city, "")
                break

    return current_city, current_zone


# 外面資料處理完對進去
# 這樣我就不用在裡面還在分辨兩個的差別
# 外面view處理一下就好


# post_data是資料庫回傳的response
def update_fish_product_data(fish, post_data, files_data):
    """
    物理因果：接收櫃台傳來的原始包裹，進行清洗、防呆、去重，最後鎖死進資料庫。
    """
    """1. 名子"""
    fish.name = post_data.get("fish_name[]")

    """2. 價格"""
    try:
        fish.price = int(post_data.get("fish_price[]", 0))
    except (ValueError, TypeError):
        # 這裡用 raise 觸發警報，讓外面的 View 去接住
        raise ValueError("價格必須填寫整數純數字")

    # 字典是單項的
    # 因為我可能核心的資料庫會變所以我不可以寫死
    # 但是因為我不可以用類似FOR I 然後裡面塞FISH.I
    # 所以我要透過setattr 全名就是 Set Attribute 去尋找標籤 且輸入數值
    # setattr(物件名稱,屬性名稱,要輸入屬性名稱的數值)

    """3. 規格"""
    # 🔄 啟動全自動對接迴圈：完全看著 CONFIG 陣列辦事！
    for config in CORE_SPECS_CONFIG:
        field_key = config["key"]  # 資料庫的欄位名 (例：'ph', 'temp', 'adult_length')
        field_label = config[
            "label"
        ]  # 前端的表單中文 (例：'pH值', '適宜溫度', '體長(cm)')
        field_type = config.get("type")

        # 1. 生物種類（特例處理）：因為它需要過「中翻英」翻譯機
        if field_key == "category":
            raw_cat = post_data.get(field_label, "其他")
            fish.category = REVERSE_AQUATIC_CATEGORIES.get(raw_cat, "OTHER")

        # 2. 雙通道範圍型 (range)：自動掛載 _min 與 _max
        elif field_type == "range":
            # 去 POST 裡面抓 "pH值_min"
            val_min = post_data.get(f"{field_label}_min")
            val_max = post_data.get(f"{field_label}_max")

            # 等同於 fish.ph_min = val_min
            setattr(fish, f"{field_key}_min", val_min)
            setattr(fish, f"{field_key}_max", val_max)

        # 3. 單一數值型 (single)：直線對接
        elif field_type == "single":
            val = post_data.get(field_label)

            # 物理通電：等同於 fish.adult_length = val
            setattr(fish, field_key, val)

    new_specs = {}
    for label in EXTRA_SPECS:
        val = post_data.get(label)
        if val:
            new_specs[label] = val
    fish.specs_json = new_specs

    """4. 提醒"""
    template_notice_id = post_data.get("global_notice")
    if template_notice_id:
        fish.notice_template_id = template_notice_id
        fish.description = ""
    else:
        fish.notice_template = None
        fish.description = post_data.get("content", "")

    """5. 圖片處理"""
    if "fish_image[]" in files_data:
        current_fish_images = files_data.getlist("fish_image[]")
        seen_files = set()
        unique_fish_images = []

        for f in current_fish_images:
            file_key = (f.name, f.size)
            if file_key not in seen_files:
                seen_files.add(file_key)
                unique_fish_images.append(f)

        if unique_fish_images:
            fish.image = unique_fish_images[0]
            AquaticImage.objects.filter(product=fish).delete()

            if len(unique_fish_images) > 1:
                for extra_img in unique_fish_images[1:]:
                    AquaticImage.objects.create(product=fish, image=extra_img)

    # 6. 敲下存檔大鐵鎚！
    fish.save()


# 處理名子 價格
def extract_fish_name_price(post_data):
    """
    物理因果：全面回歸單筆上傳，直接抓取唯一值。
    徹底捨棄 [] 與陣列的複雜迴圈判斷。
    """
    # 1. 直接抓唯一的名字 (加上 .strip() 順手物理消滅前後的空白符號)
    name = post_data.get("fish_name", "").strip()

    # 2. 抓價格並執行防呆
    price_str = post_data.get("fish_price", "").strip()
    try:
        # 如果有填就轉整數，沒填就預設 0
        price = int(price_str) if price_str else 0
    except (ValueError, TypeError):
        # 保持你原本的警報線路：如果填了 "三十" 或 "abc"，立刻中斷並拋給外層 View 接住
        raise ValueError("價格必須填寫整數純數字")

    return {
        "name": name,
        "price": price,
    }


# 處理圖片
# fish_instance這隻小魚在哪裡
# unique_images這檔案傳進來的
def process_fish_video(the_fish, video_file):
    """
    物理因果：處理單一影片上傳，並架設後端絕對防線。
    只要格式不對、太大，直接拋出 ValueError 讓外面的 View 攔截報錯。
    """
    if not video_file:
        return

    # 🛡️ 防線 1：檢查檔案大小 (物理極限：20MB)
    MAX_SIZE = 20 * 1024 * 1024  # 20MB 轉 Bytes
    if video_file.size > MAX_SIZE:
        raise ValueError("影片大小超過 20MB 限制，請重新壓縮後上傳！")

    # 🛡️ 防線 2：檢查檔案 MimeType 類型 (防止惡意偽裝檔案)
    # 這裡加入 video/quicktime 是為了相容 iPhone 拍出來的 .mov 檔案
    allowed_types = ["video/mp4", "video/webm", "video/quicktime"]
    if video_file.content_type not in allowed_types:
        raise ValueError("只支援 MP4、WebM 或 MOV 格式的影片喔！")

    # ⚡ 驗證通過，放行寫入
    the_fish.video = video_file
    the_fish.save()


def apply_fish_notice(the_fish, notice_template_id):
    """
    物理因果：純 ID 綁定模式。
    前端已經把自定義閹割，這裡只負責把選單的 ID 寫入魚隻。
    """
    notice_template_id = str(notice_template_id).strip() if notice_template_id else None

    # 大閘門：沒選範本直接報錯擋下
    if not notice_template_id:
        raise ValueError("必須選擇一個提醒範本！")

    # 綁定 ID，並保險清空舊版的自定義欄位
    the_fish.notice_template_id = notice_template_id
    the_fish.description = ""


def apply_fish_specs(the_fish, spec_template_id):
    """
    物理因果：利用範本 ID，把資料庫裡的規格解壓縮，
    精準填入魚隻的實體欄位，以利後續的資料庫標籤搜尋。
    """
    if not spec_template_id:
        raise ValueError("必須選擇一個規格範本！")

    # 1. 直接去資料庫提領這包範本
    spec_template = SpecTemplate.objects.filter(id=spec_template_id).first()
    if not spec_template:
        raise ValueError("找不到指定的規格範本，可能已被刪除！")

    # 2. 唯一的資料源：範本內的乾淨 JSON 字典
    source_data = spec_template.data

    # 3. 🔄 啟動全自動對接迴圈 (因為資料絕對乾淨，直線賦值即可)
    for config in CORE_SPECS_CONFIG:
        field_key = config["key"]  # 例：'ph'
        field_label = config["label"]  # 例：'pH值'
        field_type = config.get("type")

        # 種類轉換
        if field_key == "category":
            raw_cat = source_data.get(field_label, "其他")
            the_fish.category = REVERSE_AQUATIC_CATEGORIES.get(raw_cat, "OTHER")

        # 雙通道範圍型：直接抓 _min 跟 _max (範本裡早存好了)
        elif field_type == "range":
            setattr(the_fish, f"{field_key}_min", source_data.get(f"{field_label}_min"))
            setattr(the_fish, f"{field_key}_max", source_data.get(f"{field_label}_max"))

        # 單一數值型
        elif field_type == "single":
            setattr(the_fish, field_key, source_data.get(field_label))

    # 4. EXTRA_SPECS 額外自定義標籤
    new_specs = {}
    for label in EXTRA_SPECS:
        val = source_data.get(label)
        if val and str(val).strip():
            new_specs[label] = str(val).strip()

    the_fish.specs_json = new_specs


def process_fish_cover(the_fish, cover_file):
    """
    物理因果：攔截封面圖 -> 送入轉檔機壓縮、改 UUID -> 將最終包裹綁定到模型上。
    """
    # 1. 大閘門防線：沒有新檔案就直接斷電退場
    if not cover_file:
        return

    # 2. 🚀 核心因果：把使用者傳來的原始圖片，丟進轉檔機
    # 出來的 compressed_file 會是一個全新的、WEBP 格式、且檔名是 UUID 的記憶體包裹
    try:
        compressed_file = compress_image(cover_file, threshold_kb=500)
    except Exception as e:
        print(f"❌ [封面處理] 轉檔機發生物理故障：{e}")
        # 如果轉檔失敗，為了不讓爛檔案上傳，可以直接拋出錯誤或 return
        raise ValueError("封面圖片處理失敗，請檢查檔案格式！")

    # 3. 綁定實體檔案
    # Django 接到這個包裹後，在執行外層的 the_fish.save() 時，
    # 會自動去 models.py 讀取 upload_to 的路徑，然後發射到 Cloudflare R2。
    the_fish.image = compressed_file


# 組裝上面是個副函式
def main_process_fish_data(the_fish, post_data, files_data):
    """
    物理因果：一條龍大總管函數。
    完全捨棄批量陣列邏輯，直線處理單筆生物的 名稱/價格/提醒/規格/影片/封面圖。
    """
    # 1. 名字與價格 (呼叫剛改好的單筆提取函數)
    basic_info = extract_fish_name_price(post_data)
    the_fish.name = basic_info["name"]
    the_fish.price = basic_info["price"]

    # 2. 提醒範本 (直接抓單一 ID，呼叫純 ID 綁定函數)
    notice_id = post_data.get("fish_notice")
    apply_fish_notice(the_fish, notice_id)

    # 3. 規格自動對接 (直接抓單一 ID，呼叫純 ID 解壓縮函數)
    spec_id = post_data.get("fish_spec")
    apply_fish_specs(the_fish, spec_id)

    # 4. 影片防線處理
    # (如果檔案太大或格式錯誤，這裡會直接砸出 ValueError，中斷外層的 save 交易)
    video_file = files_data.get("video")
    process_fish_video(the_fish, video_file)

    # 🚀 5. 封面圖防線處理 (新增這兩行，物理對接前端傳來的圖片)
    cover_file = files_data.get("fish-cover")
    process_fish_cover(the_fish, cover_file)

    # 6. 終極存檔
    # 因果防線：就算 process_fish_video 或 process_fish_cover 遇到「編輯模式沒換新檔案」
    # 而直接 return，這裡的 save() 依然能確保名字、價格和範本的修改被確實寫入資料庫。
    the_fish.save()

    return the_fish
