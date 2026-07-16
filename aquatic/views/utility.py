# 🎯 終極防線：直接用 method_decorator 確保不管前端丟什麼 Method
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Exists, OuterRef
from django.http import (
    JsonResponse,  # 🚀 回傳成功或失敗的訊息給 JS
)
from django.views import View

from aquatic.constants import (
    AQUATIC_CATEGORIES,
    TAIWAN_REGIONS,
)
from aquatic.models import (
    AquaticLife,
    Post,
    Profile,
    ShopNotice,
)
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
    """取得所有有效商品，並一起取得發布者和 Profile。"""

    products = (
        AquaticLife.objects.filter(
            is_active=True,
            owner__isnull=False,
            owner__profile__isnull=False,
        )
        .select_related("owner__profile")
        .order_by("-created_at")
    )

    return {
        "items": products,
    }


def get_followed_user_ids(request):
    """取得目前登入者已追蹤的所有商家 User ID。"""

    if not request.user.is_authenticated:
        return set()

    return set(
        Profile.objects.filter(followers=request.user).values_list(
            "user_id",
            flat=True,
        )
    )


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


# 處理名子 價格
def extract_fish_name_price(post_data):
    """
    從單筆商品表單取得名稱與價格。
    """

    name = post_data.get("fish_name", "").strip()

    if not name:
        raise ValueError("商品名稱不可為空")

    price_str = post_data.get("fish_price", "").strip()

    if not price_str:
        raise ValueError("商品價格不可為空")

    try:
        price = int(price_str)
    except (ValueError, TypeError):
        raise ValueError("價格必須填寫整數純數字")

    if price < 0:
        raise ValueError("商品價格不可小於 0")

    return {
        "name": name,
        "price": price,
    }


# --------------------------------------------------------------

# --------------------------------------------------------------


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


# 處理圖片
# fish_instance這隻小魚在哪裡
# unique_images這檔案傳進來的
def process_fish_video(the_fish, video_file):
    """
    驗證影片後綁定至商品。
    實際存檔統一交給 main_process_fish_data。
    """
    if not video_file:
        return

    max_size = 20 * 1024 * 1024

    if video_file.size > max_size:
        raise ValueError("影片大小超過 20MB 限制，請重新壓縮後上傳")

    allowed_types = {
        "video/mp4",
        "video/webm",
        "video/quicktime",
    }

    if video_file.content_type not in allowed_types:
        raise ValueError("只支援 MP4、WebM 或 MOV 格式的影片")

    the_fish.video = video_file


# 下面是新的
def clean_spec_text(value):
    """
    清除前後空白，並把連續空白整理成單一空白。
    """
    if value is None:
        return ""

    return " ".join(str(value).strip().split())


def clean_temperature(value):
    """
    資料庫不儲存溫度單位。

    例如：
    24～28°C → 24～28
    24℃ → 24
    24 ～ 28 °C → 24 ～ 28
    """
    value = clean_spec_text(value)

    return value.replace("°C", "").replace("°c", "").replace("℃", "").strip()


def clean_body_length(value):
    """
    資料庫不儲存長度單位。

    例如：
    3～5 cm → 3～5
    5CM → 5
    約 5 公分 → 約 5
    """
    value = clean_spec_text(value)

    return (
        value.replace("cm", "")
        .replace("CM", "")
        .replace("Cm", "")
        .replace("cM", "")
        .replace("公分", "")
        .replace("厘米", "")
        .strip()
    )


def apply_fish_basic_specs(the_fish, post_data):
    """
    不再使用規格範本。

    前端直接傳入：
    fish_category
    fish_temp
    fish_body_length
    """

    category = post_data.get("fish_category", "").strip()

    # category 是必要欄位，並且只能是定義過的英文代碼
    if not category:
        raise ValueError("必須選擇產品種類")

    if category not in AQUATIC_CATEGORIES:
        raise ValueError("產品種類無效")

    the_fish.category = category

    # 溫度與體長均為選填，資料庫不存單位
    the_fish.temp = clean_temperature(post_data.get("fish_temp", ""))

    the_fish.body_length = clean_body_length(post_data.get("fish_body_length", ""))


# 組裝上面是個副函式
def main_process_fish_data(the_fish, post_data, files_data):
    """
    新增與編輯商品共用的資料處理函式。

    流程：
    1. 名稱與價格
    2. 種類、溫度、體長
    3. 商品備註
    4. 影片
    5. 封面圖
    6. 統一存檔
    """

    # 1. 名稱與價格
    basic_info = extract_fish_name_price(post_data)

    the_fish.name = basic_info["name"]
    the_fish.price = basic_info["price"]

    # 2. 種類、溫度、體長
    apply_fish_basic_specs(
        the_fish=the_fish,
        post_data=post_data,
    )

    # 3. 商品備註直接存入 description
    # 只清除前後空白，不可使用 clean_spec_text，
    # 否則備註裡的換行會被消除。
    the_fish.description = post_data.get(
        "fish_description",
        "",
    ).strip()

    # 新流程不再使用備註範本。
    # 編輯舊商品時，同時解除原本的範本關聯，
    # 避免詳細頁仍優先顯示舊範本內容。
    the_fish.notice_template = None

    # 不要主動清除舊的 specs_json。
    # 它目前不再顯示，但保留舊資料方便回退。
    # 新商品本來就會依 Model default 得到 {}。

    # 4. 影片
    video_file = files_data.get("video")
    process_fish_video(the_fish, video_file)

    # 5. 封面圖
    cover_file = files_data.get("fish-cover")
    process_fish_cover(the_fish, cover_file)

    # 6. 統一存檔
    the_fish.save()

    return the_fish
