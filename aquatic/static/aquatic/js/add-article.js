// 抓取元素
const addBtn = document.querySelector('.add-article-btn'); // 你的綠色加號
const closeBtn = document.getElementById('closeBtn');      // 你的返回按鈕
const modal = document.getElementById('add-article-overlay'); //背後的遮罩


// 2. 🚀 0 秒攔截邏輯（不發 Fetch，絕對不閃現）
// e 是包含所有「現場資訊」的封包
if (addBtn) {
    addBtn.addEventListener('click', (e) => {
        // 直接從 HTML 讀門票，不用等網路
        // 原理：Django 在「出廠渲染（Render）」HTML 的時候，就已經把使用者的登入狀態「燒錄」在按鈕的屬性裡了。
        // 優點：JS 不用發出 fetch 去問伺服器「我登入了沒？」。它直接讀取按鈕上的 「物理跳線狀態」。
        // 讀取暫存器的速度是奈秒級，所以使用者完全感覺不到延遲。
        const isAuthenticated = addBtn.getAttribute('data-authenticated') === 'true';

        if (!isAuthenticated) {
            e.preventDefault(); // 強力攔截所有動作
            e.stopImmediatePropagation(); // 阻止任何其他 JS 執行
            
// 注意 accounts 有加 s
        window.location.href = `/accounts/login/?next=${window.location.pathname}`;
            return;
        }

        // 有登入才開門
        // model 是之前遮罩變數
        // classlist 現有的class上
        // add is-active class的項目
        modal.classList.add('is-active');
        document.documentElement.style.overflow = 'hidden';
        document.body.style.overflow = 'hidden';
    });
}

// 點擊「返回」：關閉
closeBtn.addEventListener('click', () => {
    modal.classList.remove('is-active');
    document.body.style.overflow = 'auto'; // 恢復捲動
    document.documentElement.style.overflow = ''; // 恢復html的overflow
});



// --------------------------------------------------------------------------------------------------------------------------
// --- add-article.js ---

// 1. 照片輪播邏輯

function moveSlide(direction, btn) {
    const viewport = btn.closest(".photo-viewport");
    const track = viewport.querySelector(".photo-item-s");
    const slides = track.querySelectorAll(".photo-item");
    const total = slides.length;

    let currentIndex = parseInt(viewport.getAttribute("data-index")) || 0;
    currentIndex += direction;

    if (currentIndex >= total) currentIndex = 0;
    if (currentIndex < 0) currentIndex = total - 1;

    viewport.setAttribute("data-index", currentIndex);
    track.style.transform = `translateX(-${currentIndex * 100}%)`;
}

// 2. 照片上傳與即時顯示邏輯

function handleFileUpload(input) {
    const file = input.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
        // 建立新車廂
        const newItem = document.createElement("div");
        newItem.className = "photo-item";
        newItem.innerHTML = `<img src="${e.target.result}" class="photo-preview" />`;

        // 🚀 關鍵定位：只找這一組框框內的 upload-item
        const uploadItem = input.closest(".upload-item");
        const track = input.closest(".photo-item-s");
        const viewport = input.closest(".photo-viewport");

        // 把新照片插在「點擊的這個上傳鈕」前面
        if (track && uploadItem) {
            track.insertBefore(newItem, uploadItem);
            
            // 跳回第一張預覽剛傳好的圖
            viewport.setAttribute("data-index", 0);
            track.style.transform = `translateX(0%)`;
        }
        
        input.value = ""; // 清空值，讓同一張圖可以重複選
    };
    reader.readAsDataURL(file);
}

// 3. 頁面初始化與動態區塊新增

document.addEventListener("DOMContentLoaded", () => {
    const contentContainer = document.querySelector(".input-article-content");
    const overlay = document.getElementById("add-article-overlay");

    // // 模態框開關
    // document.getElementById("openModal")?.addEventListener("click", () => {
    //     overlay.style.display = "flex";
    // });
    // document.getElementById("closeBtn")?.addEventListener("click", () => {
    //     overlay.style.display = "none";
    // });

    // 通用新增 Template 函式
    window.appendTemplate = function(templateId) {
        const template = document.getElementById(templateId);
        const clone = template.content.cloneNode(true);
        const hint = contentContainer.querySelector(".input-hint");
        contentContainer.insertBefore(clone, hint);
    };

    document.getElementById("add-text-block")?.addEventListener("click", () => appendTemplate("text-block-template"));
    document.getElementById("add-image-block")?.addEventListener("click", () => appendTemplate("photo-block-template"));

    // 刪除邏輯 (事件委託)
    contentContainer.addEventListener("click", (e) => {
        const deleteBtn = e.target.closest(".delete-btn");
        if (deleteBtn) {
            const card = deleteBtn.closest(".input-area-card");
            if (card && confirm("確定要刪除嗎？")) card.remove();
        }
    });
});

// 圖片邏輯---------------------------------------------------------------------------------------------


// 上傳邏輯
// add-article.js

// 取得通行證的工具
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 建立一個全域變數，用來存放「暫時還沒上傳的照片檔案」
let fileMap = {}; 

// 3. 🚀 修改後的上傳處理：改用 Template 複製
function handleFileUpload(input) {
    const file = input.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
        // --- 關鍵改動：從模板複製 HTML ---
        const template = document.getElementById('photo-item-template');
        const clone = template.content.cloneNode(true);
        const newItem = clone.querySelector('.photo-item');

        // 🚀 給這個車廂一個唯一的 ID (時間戳記)
        const photoId = "photo_" + Date.now();
        newItem.setAttribute("data-photo-id", photoId);
        
        // 把檔案存進地圖
        fileMap[photoId] = file;

        // 設定預覽圖
        newItem.querySelector('.photo-preview').src = e.target.result;

        // 🚀 優化：點擊叉叉時，除了移除畫面，也從 memory 刪除檔案 (選用)
        newItem.querySelector('.remove-photo').onclick = function() {
            delete fileMap[photoId]; // 釋放記憶體
            this.parentElement.remove();
        };

        const uploadItem = input.closest(".upload-item");
        const track = input.closest(".photo-item-s");
        track.insertBefore(clone, uploadItem);

        input.value = ""; 
    };
    reader.readAsDataURL(file);
}

document.getElementById('postBtn').addEventListener('click', async function() {
    const postBtn = this; // 取得按鈕本人
    const allCards = document.querySelectorAll('.input-article-content .input-area-card');
    
    // --- 🚀 第一步：前置檢查 (防止空發) ---
    
    // 1. 檢查標題 (假設在第二個卡片)
    const titleTextarea = allCards[1] ? allCards[1].querySelector('textarea') : null;
    const titleValue = titleTextarea ? titleTextarea.value.trim() : "";

    if (!titleValue) {
        alert("魚魚提醒：請輸入標題再發佈喔！");
        if (titleTextarea) titleTextarea.focus();
        return; // 攔截，不往下跑
    }

    // 2. 檢查封面圖
    const coverPhotoItem = allCards[0].querySelector('.photo-item[data-photo-id]');
    if (!coverPhotoItem) {
        alert("請上傳一張漂亮的封面圖！");
        return;
    }

    // --- 🚀 第二步：變更按鈕狀態 (防止重複點擊) ---
    postBtn.disabled = true;
    postBtn.innerText = "上傳中..."; // 讓使用者知道後台在忙
    postBtn.style.opacity = "0.6";
    postBtn.style.cursor = "not-allowed";

    try {
        const formData = new FormData();
        const contentStructure = [];

        // --- 處理大圖 (Cover) ---
        const id = coverPhotoItem.getAttribute('data-photo-id');
        formData.append('cover_image', fileMap[id]);

        // --- 處理標題 ---
        formData.append('title', titleValue);

        // --- 處理動態區塊 ---
        for (let i = 2; i < allCards.length; i++) {
            const card = allCards[i];
            const textarea = card.querySelector('textarea');
            const photos = card.querySelectorAll('.photo-item[data-photo-id]');

            if (textarea && textarea.value.trim() !== "") {
                contentStructure.push({
                    type: 'text',
                    value: textarea.value
                });
            } else if (photos.length > 0) {
                const photoKeys = [];
                photos.forEach((p, pIdx) => {
                    const photoId = p.getAttribute('data-photo-id');
                    const file = fileMap[photoId];
                    const secretKey = `block${i}_img${pIdx}`;
                    formData.append(secretKey, file);
                    photoKeys.push(secretKey);
                });
                contentStructure.push({
                    type: 'image_group',
                    value: photoKeys
                });
            }
        }

        formData.append('content_json', JSON.stringify(contentStructure));

        // --- 寄出到後端 ---
        const response = await fetch('/blog/api/create/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });

        if (response.ok) {
            alert("發佈成功！");
            window.location.reload();
        } else {
            const errorData = await response.json();
            alert("發佈失敗：" + (errorData.message || "未知錯誤"));
            // 失敗了要解鎖按鈕，讓使用者可以修正後重傳
            resetBtn(postBtn);
        }

    } catch (error) {
        console.error(error);
        alert("網路連線似乎有問題，請稍後再試。");
        resetBtn(postBtn);
    }
});

// 重置按鈕的工具函式
function resetBtn(btn) {
    btn.disabled = false;
    btn.innerText = "發佈";
    btn.style.opacity = "1";
    btn.style.cursor = "pointer";
}
