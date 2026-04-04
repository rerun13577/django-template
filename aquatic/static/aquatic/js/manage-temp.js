function toggleAccordion(header) {
    // 1. 找到這一組手風琴的父容器 (.accordion-item)
    const item = header.closest('.accordion-item');
    
    // 2. 切換 active 類別 (原本有就刪掉，原本沒有就加上)
    item.classList.toggle('active');
    
    // 💡 進階建議：如果你希望一次只能開一個，可以加上這行：
    document.querySelectorAll('.accordion-item').forEach(i => { if(i !== item) i.classList.remove('active'); });
}

document.getElementById('saveNoticeBtn').addEventListener('click', async function(e) {
    e.preventDefault();

    const btn = this;
    const titleInput = document.getElementById('newNoticeTitle');
    const contentInput = document.getElementById('newNoticeContent');
    const editIdInput = document.getElementById('editTempId');
    const container = document.getElementById('template-list-container');

    const title = titleInput.value.trim();
    const content = contentInput.value.trim();
    const editId = editIdInput.value;

    if (!title || !content) {
        alert("標題跟內容都要寫喔！");
        return;
    }

    const url = '/api/manage-template/';
    const bodyData = { title, content };
    if (editId) bodyData.id = editId;

    btn.disabled = true;
    btn.innerText = "處理中...";

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'), 
            },
            body: JSON.stringify(bodyData)
        });

        const data = await response.json();
        const emptyHint = container.querySelector('.empty-hint');
        if (emptyHint) emptyHint.remove();
        
        if (data.status === 'success') {
            if (editId && currentEditingItem) {
                // 🚀 修改邏輯：原地更新文字
                const titleElement = currentEditingItem.querySelector('.temp-title');
                if (titleElement) titleElement.innerText = title;

                const contentElement = currentEditingItem.querySelector('.temp-content-text');
                if (contentElement) contentElement.innerHTML = content.replace(/\n/g, '<br>');

                const editBtn = currentEditingItem.querySelector('.edit-template');
                if (editBtn) {
                    const escapedTitle = title.replace(/'/g, "\\'");
                    const escapedContent = content.replace(/'/g, "\\'");
                    editBtn.setAttribute('onclick', `openEditForm('${editId}', '${escapedTitle}', '${escapedContent}', this)`);
                }

                currentEditingItem.style.display = 'block';
                toggleAddForm(); 
                alert("修改成功！");
                currentEditingItem = null;
            } else {
                // 🚀 新增邏輯：動態插入 HTML，取代 location.reload()
                const escapedTitle = title.replace(/'/g, "\\'");
                const escapedContent = content.replace(/'/g, "\\'");
                
                const newTemplateHtml = `
                    <div class="accordion-item">
                        <div class="accordion-header" onclick="toggleAccordion(this)">
                            <div class="split-tool">
                                <div class="split-left">
                                    <h3 class="temp-title">${title}</h3>
                                </div>
                                <div class="split-right">
                                    <span class="temp-arrow">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-right"><path d="m9 18 6-6-6-6" /></svg>
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
                                            <button class="template-btn delete-template" onclick="deleteTemplate('${data.id}', this)">刪除</button>
                                        </div>
                                        <div class="split-right">
                                            <button class="template-btn edit-template" onclick="openEditForm('${data.id}', '${escapedTitle}', '${escapedContent}', this)">編輯</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                // 塞到列表最前方 (在新增表單的後面)
                const addForm = document.getElementById('add-template-form');
                addForm.insertAdjacentHTML('afterend', newTemplateHtml);
                
                // 重置表單並隱藏
                titleInput.value = '';
                contentInput.value = '';
                editIdInput.value = '';
                toggleAddForm(); 
                alert("新增成功！");
            }
        } else {
            alert("錯誤：" + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert("網路連線發生問題");
    } finally {
        btn.disabled = false;
        btn.innerText = "儲存";
    }
});

// 🚀 1. 監聽右上角的「新增」按鈕
// 🚀 修改原本的「新增」按鈕監聽器
document.getElementById('addNewTempBtn').addEventListener('click', function() {
    // 也要先跑一遍歸位邏輯
    if (currentEditingItem) {
        currentEditingItem.style.display = 'block';
        currentEditingItem = null;
    }
    
    const form = document.getElementById('add-template-form');
    document.getElementById('template-list-container').prepend(form); // 移回最上面
    
    // 清空資料
    document.getElementById('editTempId').value = "";
    document.getElementById('newNoticeTitle').value = "";
    document.getElementById('newNoticeContent').value = "";
    document.getElementById('saveNoticeBtn').innerText = "儲存";

    form.style.display = 'block';
    form.scrollIntoView({ behavior: 'smooth' });
});

// 修改原本的「取消/切換」函式
function toggleAddForm() {
    const form = document.getElementById('add-template-form');
    const listContainer = document.getElementById('template-list-container');

    // 如果是取消編輯，讓原本隱藏的框框顯現
    if (currentEditingItem) {
        currentEditingItem.style.display = 'block';
        currentEditingItem = null;
    }

    // 🚀 歸位：把 FORM 移回列表的最上方
    listContainer.prepend(form);
    form.style.display = 'none';
}

/**
 * 🚀 1. 開啟編輯模式
 * 因果解釋：點擊編輯時，把該筆資料的 ID 與內容填入最上方的 Form，並讓畫面捲動過去。
 */
let currentEditingItem = null; // 🚀 用來記錄現在正在改哪一個

function openEditForm(id, title, content, btn) {
    const form = document.getElementById('add-template-form');
    
    // 1. 如果剛才已經有在編輯別的，先讓舊的顯示回來
    if (currentEditingItem) {
        currentEditingItem.style.display = 'block';
    }

    // 2. 找到目前點擊的這一個框框
    const item = btn.closest('.accordion-item');
    currentEditingItem = item;

    // 3. 填入資料
    document.getElementById('editTempId').value = id;
    document.getElementById('newNoticeTitle').value = title;
    document.getElementById('newNoticeContent').value = content;
    document.getElementById('saveNoticeBtn').innerText = "確認修改";

    // 4. 🚀 瞬間移動：把 FORM 移到這個框框的後面，並隱藏原本的框框
    item.style.display = 'none'; // 隱藏原本的框框
    item.insertAdjacentElement('afterend', form); // 把 FORM 塞到它後面
    
    form.style.display = 'block';
    form.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * 🚀 2. 刪除範本
 * 因果解釋：發送 ID 給後端，後端執行刪除後，前端直接把該 DOM 元素移除（或重新整理）。
 */
// 🚀 把參數從 (id) 改成 (id, btn)
async function deleteTemplate(id, btn) {
    if (!confirm("老闆，確定要刪除這條範本嗎？")) return;

    try {
        const response = await fetch('/api/manage-template/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ id: id, action: 'delete' }) 
        });

        const data = await response.json();

        if (data.status === 'success') {
            const item = btn.closest('.accordion-item');
            if (item) {
                item.style.opacity = '0';
                item.style.transform = 'translateX(20px)';
                item.style.transition = '0.3s ease';
                
                // 🚀 等動畫跑完才移除
                setTimeout(() => {
                    item.remove();
                    
                    // --- 🧩 這裡新增：檢查是否刪光了 ---
                    const container = document.getElementById('template-list-container');
                    
                    // 找到所有範本，但排除掉那個「新增表單」
                    const remainingItems = container.querySelectorAll('.accordion-item:not(#add-template-form)');
                    
                    // 如果一條都不剩，且畫面上還沒出現過提示，就補上去
                    if (remainingItems.length === 0 && !container.querySelector('.empty-hint')) {
                        const emptyHtml = '<p class="empty-hint">目前沒有範本，點擊右上方新增一個吧！</p>';
                        container.insertAdjacentHTML('beforeend', emptyHtml);
                    }
                    // --------------------------------
                }, 300);
            }
        } else {
            alert("刪除失敗：" + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert("程式執行出錯：" + error.message);
    }
}

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