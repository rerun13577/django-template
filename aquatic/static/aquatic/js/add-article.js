// 抓取元素
const addBtn = document.querySelector('.add-article-btn'); // 你的綠色加號
const closeBtn = document.getElementById('closeBtn');      // 你的返回按鈕
const modal = document.getElementById('add-article-overlay');

// 點擊「+」：打開
addBtn.addEventListener('click', () => {
    modal.classList.add('is-active');
    // 🚀 雙重鎖死：html 跟 body 都不要動
    document.documentElement.style.overflow = 'hidden';
    document.body.style.overflow = 'hidden'; 
    // 禁止底層頁面捲動，也就是說只有add-article-page可以滾動
});

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

    // 模態框開關
    document.getElementById("openModal")?.addEventListener("click", () => {
        overlay.style.display = "flex";
    });
    document.getElementById("closeBtn")?.addEventListener("click", () => {
        overlay.style.display = "none";
    });

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
    // 1. 準備一個「大信封」 (FormData)
    const formData = new FormData();
    
    // 2. 準備一份「內容清單」 (JSON 結構)
    const contentStructure = [];

    // 3. 抓取固定的大圖與標題
    // 我們假設第一個卡片是大圖，第二個是標題 (按你的 HTML 順序)
    const allCards = document.querySelectorAll('.input-article-content .input-area-card');
    
    // --- 處理大圖 (Cover) ---
    // 大圖通常不放在 JSON 裡，直接放在文章主欄位
    const coverInput = allCards[0].querySelector('input[type="file"]');
    // 如果你有用 handleFileUpload，大圖的檔案會存在 fileMap 或是 input 裡
    // 這裡我們假設你直接抓大圖框裡最後產生的那張圖
    const coverPhotoItem = allCards[0].querySelector('.photo-item[data-photo-id]');
    if (coverPhotoItem) {
        const id = coverPhotoItem.getAttribute('data-photo-id');
        formData.append('cover_image', fileMap[id]);
    }

    // --- 處理標題 ---
    const title = allCards[1].querySelector('textarea').value;
    formData.append('title', title);

    // 4. 掃描「動態新增」的區塊 (從第 3 個卡片開始)
    for (let i = 2; i < allCards.length; i++) {
        const card = allCards[i];
        const textarea = card.querySelector('textarea');
        const photos = card.querySelectorAll('.photo-item[data-photo-id]');

        if (textarea) {
            // 如果是文字框
            contentStructure.push({
                type: 'text',
                value: textarea.value
            });
        } else if (photos.length > 0) {
            // 如果是照片輪播框
            const photoKeys = [];
            photos.forEach((p, pIdx) => {
                const photoId = p.getAttribute('data-photo-id');
                const file = fileMap[photoId];
                
                // 給每張照片一個暗號，例如：block2_img0
                const secretKey = `block${i}_img${pIdx}`;
                formData.append(secretKey, file); // 把檔案塞進大信封
                photoKeys.push(secretKey); // 在清單寫下暗號
            });

            contentStructure.push({
                type: 'image_group',
                value: photoKeys
            });
        }
    }

    // 5. 把「內容清單」轉成字串，也塞進大信封
    formData.append('content_json', JSON.stringify(contentStructure));

    // 6. 寄出信封到後端 Django
    const response = await fetch('/blog/api/create/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken') // Django 的安全檢查
        },
        body: formData
    });

    if (response.ok) {
        alert("發佈成功！");
        window.location.reload();
    }
});