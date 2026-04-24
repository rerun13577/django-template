// 1. 分頁切換邏輯
function switchTab(btn, tabId) {
  // 隱藏所有區塊
  document.querySelectorAll(".tab-section").forEach((section) => {
    section.style.display = "none";
  });
  // 顯示目標區塊
  const target = document.getElementById("tab-" + tabId);
  if (target) {
    target.style.display = "block";
  }

  // 切換按鈕樣式
  document.querySelectorAll(".tab-item").forEach((item) => {
    item.classList.remove("active");
  });
  btn.classList.add("active");
}

// 2. 獲取 CSRF Token 的輔助函式 (因為外部 JS 抓不到 Django 標籤)
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// 3. HTMX 配置：自動蓋印章
document.addEventListener("DOMContentLoaded", () => {
  document.body.addEventListener("htmx:configRequest", (event) => {
    // 從 Cookie 抓取 csrftoken
    event.detail.headers["X-CSRFToken"] = getCookie("csrftoken");
  });
});

function toggleNotice(cardId) {
  const card = document.getElementById(cardId);
  if (card) {
    // 因：點擊標籤。果：切換類別。
    // CSS 會根據這個類別自動處理內容顯示與箭頭旋轉。
    card.classList.toggle("expanded");
  }
}

// 控制手風琴開關
function toggleAccordion(header) {
  const item = header.closest(".accordion-item");
  item.classList.toggle("active");
}

// 切換新增表單顯示/隱藏
function toggleAddForm() {
  const form = document.getElementById("add-template-form");
  if (form.style.display === "none") {
    form.style.display = "block";
  } else {
    form.style.display = "none";
    // 關閉時清空 ID，防止編輯狀態殘留
    document.getElementById("editTempId").value = "";
    document.getElementById("newNoticeTitle").value = "";
    document.getElementById("newNoticeContent").value = "";
  }
}
// 🚀 1. 在函式外面定義一個變數，用來記錄「誰正在被改」
let currentEditingItem = null;

// 🚀 2. 修改函式，增加第四個參數 btn
function openEditForm(id, title, content, btn) {
  const form = document.getElementById("add-template-form");
  const saveBtn = document.getElementById("saveNoticeBtn");

  // 💡 因果：如果之前有別張卡片在編輯，先讓它顯示回來（恢復原狀）
  if (currentEditingItem) {
    currentEditingItem.style.display = "block";
  }

  // 💡 找到「現在」點擊的這一張卡片
  const item = btn.closest(".accordion-item");
  currentEditingItem = item;

  // 填寫資料
  document.getElementById("editTempId").value = id;
  document.getElementById("newNoticeTitle").value = title;
  document.getElementById("newNoticeContent").value = content;

  // 修改按鈕文字讓老闆知道是在「修改」
  if (saveBtn) saveBtn.innerText = "確認修改";

  // 🚀 關鍵動作：把 Form 搬到這張卡片後面，然後隱藏卡片
  item.insertAdjacentElement("afterend", form);
  item.style.display = "none"; // 👈 這行沒寫，舊卡片就不會消失
  form.style.display = "block";

  // 捲動到位置
  form.scrollIntoView({ behavior: "smooth", block: "center" });
}
