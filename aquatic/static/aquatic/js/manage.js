// manage.js - 通用 UI 總管
let currentEditingItem = null;

// 通用的「開表單」動畫邏輯
// 🚀 穩定派：永遠把資料「送上去」給最上方的表單，絕不搬移表單本體！

// 🚀 穩定派：收合與清空表單

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

window.uiReset = function () {
  console.log("⚡ 啟動表單歸位與卡片還原程序！");

  // 🚀 核心因果修正：無條件優先還原卡片！不准包在表單迴圈裡！
  if (currentEditingItem) {
    currentEditingItem.style.display = "block";
    // 逼迫瀏覽器瞬間計算體積，避免動畫卡頓
    void currentEditingItem.offsetHeight;
    currentEditingItem.style.opacity = "1";
    currentEditingItem.style.transform = "scale(1)";

    // 釋放記憶體，把插頭拔掉，避免下次錯亂
    currentEditingItem = null;
  }

  // 📦 下面的邏輯負責把表單收好、清空
  const activeForms = document.querySelectorAll(".create-mode, .edit-mode"); // 多加幾個保險
  activeForms.forEach((formWrapper) => {
    if (getComputedStyle(formWrapper).display !== "none") {
      formWrapper.style.opacity = "0";
      formWrapper.style.transform = "translateY(10px)";

      setTimeout(() => {
        formWrapper.style.display = "none";

        // 物理清空輸入框
        formWrapper.querySelectorAll('input:not([type="hidden"]), textarea').forEach((i) => {
          i.value = "";
        });

        // 物理清空隱藏 ID
        const hiddenId = formWrapper.querySelector("#edit-spec-id, #editTempId");
        if (hiddenId) hiddenId.value = "";
      }, 150);
    }
  });
};

document.addEventListener("click", async function (e) {
  const header = e.target.closest(".accordion-header");
  if (!header || header.classList.contains("no-cursor")) return;

  const item = header.closest(".accordion-item");
  const body = item.querySelector(".accordion-body");
  if (!body) return;

  // ====================================================
  // 🔍 階段一：排他性掃描 (強制關閉其他正在打開的盒子)
  // ====================================================
  const allOpenItems = document.querySelectorAll(".accordion-item.is-open");

  allOpenItems.forEach((openItem) => {
    // 只要不是你現在點的這個，就通通關起來
    if (openItem !== item) {
      openItem.classList.remove("is-open");
      const openBody = openItem.querySelector(".accordion-body");

      if (openBody) {
        // 執行標準關門物理學
        openBody.style.maxHeight = openBody.scrollHeight + "px";
        void openBody.offsetHeight; // 強制重繪
        openBody.style.maxHeight = "0";
        openBody.style.opacity = "0";

        setTimeout(() => {
          if (!openItem.classList.contains("is-open")) {
            openBody.style.display = "none";
          }
        }, 300); // 配合 CSS 動畫時間
      }
    }
  });

  // ====================================================
  // ⚙️ 階段二：處理你剛剛點擊的這個盒子的開與關
  // ====================================================
  const isOpen = item.classList.toggle("is-open");

  if (isOpen) {
    // 【階段 1：顯示空殼】
    body.style.display = "block";
    body.style.maxHeight = "0"; // 先設 0，保證不會閃爍
    body.style.opacity = "0";

    // 🚀 階段 2：排程等待 (這讓幾千字的排版能先完成)
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        // 現在計算高度，瀏覽器已經完成文字渲染了
        body.style.transition = "max-height 0.4s cubic-bezier(0.25, 1, 0.5, 1), opacity 0.3s ease";
        body.style.maxHeight = body.scrollHeight + 60 + "px";
        body.style.opacity = "1";
      });
    });

    // 階段 3：動畫結束後釋放高度，避免幾千字溢出
    setTimeout(() => {
      if (item.classList.contains("is-open")) {
        body.style.maxHeight = "none";
      }
    }, 500);
  } else {
    // 【關門物理學】(自己點擊自己來關閉)
    body.style.maxHeight = body.scrollHeight + "px";
    void body.offsetHeight; // 鎖定當下高度

    // 瞬間壓扁
    body.style.maxHeight = "0";
    body.style.opacity = "0";

    setTimeout(() => {
      if (!item.classList.contains("is-open")) {
        body.style.display = "none";
      }
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

  // 1. 視覺對齊藥丸背景
  if (defaultTab) moveActiveTab(defaultTab);

  // 2. 初始化所有區塊的顯示狀態與 Input 活性
  if (defaultTab) {
    const currentMode = defaultTab.innerText.includes("批量") ? "batch" : defaultTab.innerText.includes("單獨") ? "single" : "off";

    // 🚀 直接呼叫你寫好的 switchMode，讓它去處理所有的顯示/隱藏與 disabled
    switchMode(defaultTab, currentMode);
  }

  // 3. 監聽 Hover (維持原樣)
  tabs.forEach((tab) => {
    tab.addEventListener("mouseenter", (e) => moveActiveTab(e.target));
  });
  if (wrapper) {
    wrapper.addEventListener("mouseleave", () => {
      const currentActive = document.querySelector(".mode-tab.active");
      if (currentActive) moveActiveTab(currentActive);
    });
  }
});
// 🚀 3. 正式點擊切換功能 (對應你 HTML 裡的 onclick)
// manage.js 中的 switchMode 整合版

function switchMode(element, mode) {
  // A. 樣式與藥丸框框移動
  document.querySelectorAll(".mode-tab").forEach((tab) => tab.classList.remove("active"));
  element.classList.add("active");
  if (typeof moveActiveTab === "function") moveActiveTab(element);

  // B. 抓取唯一的單獨表單區塊（批量的 id 全部物理拔除，省空間）
  const singleForm = document.getElementById("singleUploadForm");

  // C. 核心因果：精準切換開與關
  if (mode === "off") {
    // 模式：關閉 -> 隱藏單獨表單
    if (singleForm) singleForm.style.display = "none";
  } else if (mode === "single") {
    // 模式：單獨 -> 顯示單獨表單
    if (singleForm) singleForm.style.display = "block";
  }
}
