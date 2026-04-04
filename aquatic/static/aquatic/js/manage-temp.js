function toggleAccordion(header) {
    // 1. 找到這一組手風琴的父容器 (.accordion-item)
    const item = header.closest('.accordion-item');
    
    // 2. 切換 active 類別 (原本有就刪掉，原本沒有就加上)
    item.classList.toggle('active');
    
    // 💡 進階建議：如果你希望一次只能開一個，可以加上這行：
    document.querySelectorAll('.accordion-item').forEach(i => { if(i !== item) i.classList.remove('active'); });
}

// manage-temp.js
document.getElementById('saveNoticeBtn').addEventListener('click', async function(e) {
    e.preventDefault(); // 🚀 防止任何預設的跳轉行為

    const btn = this;
    const titleInput = document.getElementById('newNoticeTitle');
    const contentInput = document.getElementById('newNoticeContent');
    const container = document.getElementById('template-list-container');

    const title = titleInput.value.trim();
    const content = contentInput.value.trim();

    // 1. 驗證
    if (!title || !content) {
        alert("標題跟內容都要寫喔！");
        return;
    }

    // 2. 防止重複點擊
    btn.disabled = true;
    btn.innerText = "儲存中...";

    try {
        // 3. 發送請求
        const response = await fetch('/api/save-template/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'), 
            },
            body: JSON.stringify({ title, content })
        });

        const data = await response.json();

        if (data.status === 'success') {
            // 🚀 關鍵：因果邏輯 - 不要 reload，直接把新範本貼到列表最前面
            const newTemplateHtml = `
                <div class="accordion-item">
                    <div class="accordion-header" onclick="toggleAccordion(this)">
                        <div class="split-tool">
                            <div class="split-left">
                                <h3 class="temp-title">${title}</h3>
                            </div>
                            <div class="split-right">
                                <span class="temp-arrow">
                                <svg
  xmlns="http://www.w3.org/2000/svg"
  width="24"
  height="24"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
  class="lucide lucide-chevron-right-icon lucide-chevron-right"
>
  <path d="m9 18 6-6-6-6" />
</svg>
</span>
                            </div>
                        </div>
                    </div>
                    <div class="accordion-body">
                        <div class="accordion-inner">
                        
                            <div class="temp-content-text">${content.replace(/\n/g, '<br>')}</div>
                        <div class="temp-actions">
                            <div class="split-tool">
                                <div class="split-left">
                                    <button class="template-btn  delete-template" onclick="toggleAddForm()">取消</button>
                                </div>
                                <div class="split-right">
                                    <button id="saveNoticeBtn" class="template-btn edit-template">儲存</button>
                                </div>
                            </div>
                        </div>
                        </div>
                    </div>
                </div>
            `;
            
            // 插入到列表容器的最上方 (跳過新增框)
            container.insertAdjacentHTML('afterbegin', newTemplateHtml);

            // 4. 重置 UI (關閉新增框、清空文字)
            titleInput.value = '';
            contentInput.value = '';
            if (typeof toggleAddForm === "function") toggleAddForm(); // 假設你有這個開關函式

            alert("範本儲存成功！");
        } else {
            alert("失敗了：" + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert("連線發生問題，請稍後再試");
    } finally {
        // 5. 恢復按鈕狀態
        btn.disabled = false;
        btn.innerText = "儲存";
    }
});

/**
 * 🚀 抓取 CSRF Token
 */
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