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
// -------------------------------------------------------------------------------------------------------------
// 🚀 初始化：網頁一開，背景自動對準「關閉」
// 🚀 1. 核心搬移函數：負責計算位置並讓方塊滑過去
function moveActiveTab(target) {
  const activeBg = document.querySelector(".mode-tab-active");
  if (!target || !activeBg) return;

  const { clientHeight, clientWidth, offsetLeft, offsetTop } = target;

  activeBg.style.left = `${offsetLeft}px`;
  activeBg.style.top = `${offsetTop}px`;
  activeBg.style.width = `${clientWidth}px`;
  activeBg.style.height = `${clientHeight}px`;
}

// 🚀 2. 初始化與事件監聽
// 🚀 2. 初始化：網頁載入完成後的「對齊」與「隱藏」
window.addEventListener("DOMContentLoaded", () => {
  const wrapper = document.querySelector(".mode-toggle-wrapper");
  const tabs = document.querySelectorAll(".mode-tab");
  const defaultTab = document.querySelector(".mode-tab.active");

  // 視覺對齊
  if (defaultTab) moveActiveTab(defaultTab);

  // 抓取所有區塊
  const setupSection = document.getElementById("setupSection");
  const batchContainer = document.getElementById("batchSlotsContainer");
  const singleContainer = document.getElementById("singleUploadContainer"); // 🚀 補上這行

  if (defaultTab) {
    const isBatch = defaultTab.innerText.includes("批量");
    const isSingle = defaultTab.innerText.includes("單獨"); // 🚀 增加單獨的判斷

    // 🚀 因果邏輯：不是批量就藏批量
    if (!isBatch) {
      if (setupSection) setupSection.style.display = "none";
      if (batchContainer) batchContainer.style.display = "none";
    }

    // 🚀 因果邏輯：不是單獨就藏單獨（解決你的問題）
    if (!isSingle) {
      if (singleContainer) singleContainer.style.display = "none";
    }
  }

  // 監聽 Hover 與 歸位 (維持不變)
  tabs.forEach((tab) => {
    tab.addEventListener("mouseenter", (e) => moveActiveTab(e.target));
  });
  wrapper.addEventListener("mouseleave", () => {
    const currentActive = document.querySelector(".mode-tab.active");
    if (currentActive) moveActiveTab(currentActive);
  });
});

// 🚀 3. 正式點擊切換功能 (對應你 HTML 裡的 onclick)
function switchMode(element, mode) {
  // 1. 樣式與框框移動 (維持你原本的)
  document.querySelectorAll(".mode-tab").forEach((tab) => tab.classList.remove("active"));
  element.classList.add("active");
  moveActiveTab(element);

  // 2. 抓取所有區塊
  const setupSection = document.getElementById("setupSection"); // 批量設定條
  const batchContainer = document.getElementById("batchSlotsContainer"); // 批量格子區
  const singleContainer = document.getElementById("singleUploadContainer"); // 單獨大卡片

  // 🚀 核心因果：根據 mode 決定誰消失、誰出現
  if (mode === "off") {
    // 模式：關閉 -> 全部藏起來
    setupSection.style.display = "none";
    batchContainer.style.display = "none";
    singleContainer.style.display = "none";
  } else if (mode === "single") {
    // 模式：單獨 -> 藏批量，開單獨
    setupSection.style.display = "none";
    batchContainer.style.display = "none";
    singleContainer.style.display = "block"; // 💡 顯示大卡片
  } else if (mode === "batch") {
    // 模式：批量 -> 藏單獨，開批量
    singleContainer.style.display = "none";
    setupSection.style.display = "grid"; // 💡 顯示批量設定條
    batchContainer.style.display = "grid"; // 💡 顯示批量格子
  }
}
