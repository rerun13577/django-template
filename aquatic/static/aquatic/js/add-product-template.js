/**
 * 🚀 FisshShop 範本管理邏輯 (同步發文模式)
 */
console.log("泰森已上線，範本管理載入成功！");

(function() {
    // 1. 抓取元素
    const modal = document.getElementById('manage-notice-overlay');
    const saveBtn = document.getElementById('saveNoticeBtn');

    // 2. 打開彈窗 (掛到 window 讓 HTML 的 onclick 抓得到)
    window.openManageTempModal = function() {
        console.log("嘗試打開範本彈窗...");
        if (modal) {
            modal.classList.add('is-active'); // 🚀 因：改用 class 控制。果：觸發 CSS 的淡入動畫。
            document.documentElement.style.overflow = 'hidden';
            document.body.style.overflow = 'hidden';
        } else {
            console.error("找不到 ID: manage-notice-overlay");
        }
    };

    // 3. 關閉彈窗
    window.closeNoticeModal = function() {
        if (modal) {
            modal.classList.remove('is-active');
            document.documentElement.style.overflow = '';
            document.body.style.overflow = 'auto';
        }
    };

    // 4. 儲存邏輯 (AJAX)
    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            const title = document.getElementById('notice-title').value.trim();
            const defaultName = document.getElementById('notice-default-name').value.trim();
            const content = document.getElementById('notice-content').value.trim();

            if (!title || !content) {
                alert("標題跟內容都要填喔，這是優雅的基礎。");
                return;
            }

            // 變更按鈕狀態
            saveBtn.disabled = true;
            saveBtn.innerText = "儲存中...";

            try {
                const response = await fetch('/aquatic/api/template/save/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({
                        title: title,
                        default_item_name: defaultName,
                        content: content
                    })
                });

                if (response.ok) {
                    alert("範本儲存成功！");
                    window.location.reload();
                } else {
                    alert("儲存失敗，後端可能在鬧脾氣。");
                    saveBtn.disabled = false;
                    saveBtn.innerText = "儲存";
                }
            } catch (error) {
                console.error(error);
                alert("網路怪怪的，檢查一下？");
                saveBtn.disabled = false;
                saveBtn.innerText = "儲存";
            }
        });
    }
    // 輔助函式：拿 CSRF Token
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
})();

// 🚀 掛在 window 下讓 HTML 的 onclick 抓得到
window.toggleAccordion = function(headerElement) {
    const item = headerElement.parentElement;
    
    // 💡 如果你想要「點開一個、自動關閉另一個」，可以加上這兩行：
    // document.querySelectorAll('.accordion-item').forEach(el => el !== item && el.classList.remove('is-open'));

    item.classList.toggle('is-open');
    console.log("切換範本展開狀態");
};