function toggleAccordion(header) {
    // 1. 找到這一組手風琴的父容器 (.accordion-item)
    const item = header.closest('.accordion-item');
    
    // 2. 切換 active 類別 (原本有就刪掉，原本沒有就加上)
    item.classList.toggle('active');
    
    // 💡 進階建議：如果你希望一次只能開一個，可以加上這行：
    document.querySelectorAll('.accordion-item').forEach(i => { if(i !== item) i.classList.remove('active'); });
}

// manage-temp.js

document.getElementById('saveNoticeBtn').addEventListener('click', function() {
    const title = document.getElementById('newNoticeTitle').value;
    const content = document.getElementById('newNoticeContent').value;

    // 1. 簡單防呆
    if (!title.trim() || !content.trim()) {
        alert("老闆，標題跟內容都要寫喔！");
        return;
    }

    // 2. 準備發送 (因果：傳 JSON 到後端 View)
    fetch('/api/save-template/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'), 
        },
        body: JSON.stringify({
            'title': title,
            'content': content
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // 🚀 儲存成功後的因果：清空輸入框並重新整理
            alert("範本儲存成功！");
            location.reload(); 
        } else {
            alert("失敗了：" + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("系統噴錯了，去看看 Console");
    });
});

// 🚀 抓取 CSRF Token 的標準寫法
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