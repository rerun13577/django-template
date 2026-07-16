// ────────────────────────────────────────────────────────
// 🚀 模組 A：分頁滑動動畫與地點初始化
// ────────────────────────────────────────────────────────
// ────────────────────────────────────────────────────────
// 模組 A：動態分頁滑動動畫與地點初始化
// ────────────────────────────────────────────────────────

function initTabs(container) {
  const elements = getTabElements(container);

  if (!elements) {
    return;
  }

  const { tabsWindow, tabs, contents } = elements;

  // 自動建立索引，不用手動寫 data-index
  tabs.forEach((tab, index) => {
    tab.dataset.index = String(index);
  });

  // 防止 HTMX 重複初始化監聽器
  if (tabsWindow.dataset.tabsInitialized !== "true") {
    tabsWindow.dataset.tabsInitialized = "true";

    let scrollFrame = null;
    let heightTimer = null;

    tabsWindow.addEventListener(
      "scroll",
      () => {
        // 更新上方 active
        if (scrollFrame) {
          cancelAnimationFrame(scrollFrame);
        }

        scrollFrame = requestAnimationFrame(() => {
          const currentElements = getTabElements(container);

          if (!currentElements) {
            return;
          }

          const currentContents = currentElements.contents;

          let nearestIndex = 0;
          let nearestDistance = Infinity;

          currentContents.forEach((content, index) => {
            const distance = Math.abs(content.offsetLeft - tabsWindow.scrollLeft);

            if (distance < nearestDistance) {
              nearestDistance = distance;
              nearestIndex = index;
            }
          });

          currentElements.tabs.forEach((tab, index) => {
            tab.classList.toggle("active", index === nearestIndex);
          });

          // 等滑動暫停後再更新高度
          window.clearTimeout(heightTimer);

          heightTimer = window.setTimeout(() => {
            updateActiveTab(container, nearestIndex);
          }, 80);
        });
      },
      {
        passive: true,
      },
    );
  }

  let activeIndex = tabs.findIndex((tab) => tab.classList.contains("active"));

  if (activeIndex < 0) {
    activeIndex = 0;
  }

  // 初始位置不要播放動畫
  syncTab(container, activeIndex, false);

  // 內容因 HTMX 或圖片載入而改變時更新高度
  if (container._profileTabsObserver) {
    container._profileTabsObserver.disconnect();
  }

  if ("ResizeObserver" in window) {
    const observer = new ResizeObserver(() => {
      const currentTab = container.querySelector(".profile-tabs .tab-item.active");

      const currentIndex = Number.parseInt(currentTab?.dataset.index ?? "0", 10) || 0;

      updateActiveTab(container, currentIndex);
    });

    contents.forEach((content) => {
      observer.observe(content);
    });

    container._profileTabsObserver = observer;
  }
}

function getTabElements(container) {
  if (!container) {
    return null;
  }

  const tabsWindow = container.querySelector(".tabs-window");

  const tabs = Array.from(container.querySelectorAll(".profile-tabs .tab-item"));

  const contents = Array.from(container.querySelectorAll(".tabs-slider > .tab-content"));

  if (!tabsWindow || tabs.length === 0 || contents.length === 0) {
    return null;
  }

  return {
    tabsWindow,
    tabs,
    contents,
  };
}

function updateActiveTab(container, index) {
  const elements = getTabElements(container);

  if (!elements) {
    return;
  }

  const { tabs, contents, tabsWindow } = elements;

  const safeIndex = Math.max(0, Math.min(Number(index) || 0, contents.length - 1));

  tabs.forEach((tab, tabIndex) => {
    tab.classList.toggle("active", tabIndex === safeIndex);
  });

  const targetContent = contents[safeIndex];

  if (!targetContent) {
    return;
  }

  // 讓外框高度跟著目前頁面內容變動
  requestAnimationFrame(() => {
    tabsWindow.style.height = `${targetContent.scrollHeight}px`;
  });
}

function syncTab(container, index, animate = true) {
  const elements = getTabElements(container);

  if (!elements) {
    return;
  }

  const { tabsWindow, contents } = elements;

  const safeIndex = Math.max(0, Math.min(Number.parseInt(index, 10) || 0, contents.length - 1));

  const targetContent = contents[safeIndex];

  if (!targetContent) {
    return;
  }

  updateActiveTab(container, safeIndex);

  // 點擊和手指滑動統一控制 scrollLeft
  tabsWindow.scrollTo({
    left: targetContent.offsetLeft,
    behavior: animate ? "smooth" : "auto",
  });
}
function updateTabsWindowHeight(container, index) {
  const tabsWindow = container.querySelector(".tabs-window");
  const contents = container.querySelectorAll(".tabs-slider > .tab-content");

  const targetContent = contents[index];

  if (!tabsWindow || !targetContent) return;

  requestAnimationFrame(() => {
    tabsWindow.style.height = `${targetContent.scrollHeight}px`;
  });
}

// ────────────────────────────────────────────────────────
// 初始化主頁分頁
// ────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  const profileContainer = document.getElementById("profile-info-section");

  initTabs(profileContainer);
});

// ────────────────────────────────────────────────────────
// HTMX 動態更新後重新初始化
// ────────────────────────────────────────────────────────

document.addEventListener("htmx:afterSwap", () => {
  const profileContainer = document.getElementById("profile-info-section");

  initTabs(profileContainer);

  const modal = document.getElementById("profile-edit-modal");

  if (modal) {
    initTabs(modal);
    initLocationCircuit(modal);
  }
});

// ────────────────────────────────────────────────────────
// 分頁按鈕事件代理
// ────────────────────────────────────────────────────────

document.addEventListener("click", (event) => {
  const tab = event.target.closest(".profile-tabs .tab-item");

  if (!tab) {
    return;
  }

  const container = tab.closest("#profile-info-section") || tab.closest("#profile-edit-modal");

  if (!container) {
    return;
  }

  const tabs = Array.from(container.querySelectorAll(".profile-tabs .tab-item"));

  const index = tabs.indexOf(tab);

  if (index === -1) {
    return;
  }

  syncTab(container, index, true);
});

// ────────────────────────────────────────────────────────
// 視窗縮放時重新對齊
// ────────────────────────────────────────────────────────

let profileTabResizeTimer = null;

window.addEventListener("resize", () => {
  window.clearTimeout(profileTabResizeTimer);

  profileTabResizeTimer = window.setTimeout(() => {
    const containers = document.querySelectorAll("#profile-info-section, #profile-edit-modal");

    containers.forEach((container) => {
      const activeTab = container.querySelector(".profile-tabs .tab-item.active");

      const index = Number.parseInt(activeTab?.dataset.index ?? "0", 10) || 0;

      syncTab(container, index, false);
    });
  }, 100);
});

// ────────────────────────────────────────────────────────
// 🚀 模組 B：主頁「三個點」下拉選單切換（安全防禦版）
// ────────────────────────────────────────────────────────
document.addEventListener("click", (e) => {
  const editBtn = document.getElementById("edit-menu-btn");
  const dropdown = document.getElementById("edit-dropdown");

  if (!editBtn || !dropdown) return;

  if (editBtn.contains(e.target)) {
    e.stopPropagation();
    dropdown.classList.toggle("show");
    return;
  }

  if (dropdown.contains(e.target)) {
    dropdown.classList.remove("show");
    return;
  }

  dropdown.classList.remove("show");
});
