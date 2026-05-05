// manage.js - 通用 UI 總管
let currentEditingItem = null;

// 通用的「開表單」動畫邏輯
window.uiShowForm = function (item, form) {
  if (currentEditingItem) uiReset(); // 如果有人在改，先復原
  currentEditingItem = item;

  item.style.opacity = "0";
  item.style.transform = "scale(0.95)";

  setTimeout(() => {
    item.style.display = "none";
    item.insertAdjacentElement("afterend", form);
    form.style.display = "block";
    requestAnimationFrame(() => {
      form.style.opacity = "1";
      form.style.transform = "translateY(0)";
    });
  }, 300);
};

// manage.js

// 通用的「收表單」歸位邏輯 (修正版)
// manage.js

// 🚀 1. 編輯：表單與卡片同步切換
window.uiShowForm = function (item, form) {
  if (currentEditingItem) uiReset();
  currentEditingItem = item;

  // 同步開始：卡片淡出，同時讓表單「佔位」
  item.style.opacity = "0";
  item.style.transform = "scale(0.98)";

  // 縮短等待時間到 150ms (人類視覺無感的極限)
  setTimeout(() => {
    item.style.display = "none";
    item.insertAdjacentElement("afterend", form);

    form.style.display = "block";
    form.style.opacity = "0";
    form.style.transform = "translateY(5px)";

    // 🚀 立即觸發淡入，不要再等
    requestAnimationFrame(() => {
      form.style.transition = "all 0.25s var(--transition)";
      form.style.opacity = "1";
      form.style.transform = "translateY(0)";
    });
  }, 150);
};

// 🚀 2. 取消：表單淡出，卡片立刻補位
// manage.js

// manage.js

window.uiReset = function () {
  const activeForms = document.querySelectorAll(".create-mode");

  activeForms.forEach((formWrapper) => {
    if (getComputedStyle(formWrapper).display !== "none") {
      formWrapper.style.opacity = "0";
      formWrapper.style.transform = "translateY(10px)";

      setTimeout(() => {
        formWrapper.style.display = "none";

        // 🚀 關鍵修正：同時抓取 input 和 textarea
        formWrapper.querySelectorAll('input:not([type="hidden"]), textarea').forEach((i) => {
          i.value = "";
        });

        // 清空隱藏的 ID
        const hiddenId = formWrapper.querySelector("#edit-spec-id, #editTempId");
        if (hiddenId) hiddenId.value = "";

        if (currentEditingItem) {
          currentEditingItem.style.display = "block";
          setTimeout(() => {
            currentEditingItem.style.opacity = "1";
            currentEditingItem.style.transform = "scale(1)";
            currentEditingItem = null;
          }, 10);
        }
      }, 150);
    }
  });
};

// manage.js

// 🚀 1. 全域手風琴監聽：不管「購物須知」還是「規格」，點了就展開
document.addEventListener("click", function (e) {
  const header = e.target.closest(".accordion-header");
  // 如果點的是標題，且不是處於「不可點擊(no-cursor)」狀態
  if (!header || header.classList.contains("no-cursor")) return;

  const item = header.closest(".accordion-item");
  const body = item.querySelector(".accordion-body");
  if (!body) return;

  const isOpen = item.classList.toggle("is-open");
  if (isOpen) {
    body.style.display = "block";
    setTimeout(() => {
      body.style.maxHeight = body.scrollHeight + "px";
      body.style.opacity = "1";
    }, 10);
  } else {
    body.style.maxHeight = "0";
    body.style.opacity = "0";
    setTimeout(() => {
      if (!item.classList.contains("is-open")) body.style.display = "none";
    }, 300);
  }
});

// 🚀 2. 通用表單切換：傳入 ID，它就幫你開或關
// manage.js

function toggleForm(formId) {
  const form = document.getElementById(formId);
  if (!form) return;

  // 使用 getComputedStyle 判斷，比 style.display 更準
  const isHidden = getComputedStyle(form).display === "none";

  if (isHidden) {
    // 🚀 1. 顯示前先確保它是透明的，準備淡入
    form.style.display = "block";
    form.style.opacity = "0";
    form.style.transform = "translateY(10px)";

    // 🚀 2. 觸發強制的「重繪」並開始動畫
    requestAnimationFrame(() => {
      form.style.transition = "all 0.25s var(--transition)";
      form.style.opacity = "1";
      form.style.transform = "translateY(0)";
    });

    form.scrollIntoView({ behavior: "smooth", block: "center" });
  } else {
    // 如果是開著的，就呼叫 uiReset 執行縮回動畫
    uiReset();
  }
}

// ==========================================
// 1. 分頁切換 (Tab Switching)
// ==========================================
function switchTab(btn, tabId) {
  // A. 隱藏所有分頁區塊 (.tab-section)
  document.querySelectorAll(".tab-section").forEach((section) => {
    section.style.display = "none";
  });

  // B. 顯示目標分頁 (ID 組合規律：tab-notices, tab-specs, tab-products)
  const target = document.getElementById("tab-" + tabId);
  if (target) {
    target.style.display = "block";
    console.log(`📌 已切換至分頁: ${tabId}`);
  } else {
    console.error(`❌ 找不到對應分頁: tab-${tabId}`);
  }

  // C. 更新按鈕的 active 樣式
  document.querySelectorAll(".tab-item").forEach((item) => {
    item.classList.remove("active");
  });
  btn.classList.add("active");

  // D. 額外保險：換頁時自動收起所有開啟的表單
  if (typeof uiReset === "function") uiReset();
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // 檢查這塊餅乾的名字是不是我們要的 (通常是 csrftoken)
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// 🚀 自動幫所有的 HTMX 請求帶上餅乾
document.addEventListener("htmx:configRequest", (event) => {
  event.detail.headers["X-CSRFToken"] = getCookie("csrftoken");
});
