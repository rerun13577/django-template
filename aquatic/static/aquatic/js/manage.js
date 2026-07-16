// manage.js
// 商品管理頁共用功能：表單切換、HTMX CSRF、商品編輯 Modal。

"use strict";

(() => {
  // 防止 manage.js 被重複初始化
  if (window.__fisshManageReady) {
    return;
  }

  window.__fisshManageReady = true;

  let modalPageScrollY = 0;
  let isPageScrollLocked = false;
  let wasMobileHeaderHiddenBeforeModal = false;

  /**
   * 取得指定 Cookie。
   */
  function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(";") : [];

    for (const cookieItem of cookies) {
      const cookie = cookieItem.trim();
      const prefix = `${name}=`;

      if (cookie.startsWith(prefix)) {
        return decodeURIComponent(cookie.slice(prefix.length));
      }
    }

    return null;
  }

  /**
   * HTMX 請求自動加入 Django CSRF Token。
   */
  document.addEventListener("htmx:configRequest", (event) => {
    const csrfToken = getCookie("csrftoken");

    if (csrfToken) {
      event.detail.headers["X-CSRFToken"] = csrfToken;
    }
  });

  /**
   * 將切換器的活動背景移到指定按鈕。
   */
  function moveModeIndicator(target) {
    const indicator = document.querySelector(".mode-tab-active");

    if (!target || !indicator) {
      return;
    }

    indicator.style.left = `${target.offsetLeft}px`;
    indicator.style.top = `${target.offsetTop}px`;
    indicator.style.width = `${target.offsetWidth}px`;
    indicator.style.height = `${target.offsetHeight}px`;
  }

  /**
   * 切換商品新增表單。
   *
   * mode:
   * - off：隱藏表單
   * - single：顯示表單
   */
  window.switchMode = function switchMode(button, mode) {
    const uploadForm = document.getElementById("singleUploadForm");

    document.querySelectorAll(".mode-tab").forEach((tab) => {
      tab.classList.toggle("active", tab === button);
    });

    moveModeIndicator(button);

    if (!uploadForm) {
      return;
    }

    uploadForm.style.display = mode === "single" ? "block" : "none";
  };

  /**
   * 初始化管理頁切換器。
   */
  function initializeModeToggle() {
    const wrapper = document.querySelector(".mode-toggle-wrapper");

    const tabs = document.querySelectorAll(".mode-tab");

    const activeTab = document.querySelector(".mode-tab.active");

    if (!activeTab) {
      return;
    }

    const initialMode = activeTab.dataset.mode || "off";

    window.switchMode(activeTab, initialMode);

    tabs.forEach((tab) => {
      tab.addEventListener("mouseenter", () => {
        moveModeIndicator(tab);
      });
    });

    wrapper?.addEventListener("mouseleave", () => {
      const currentActive = document.querySelector(".mode-tab.active");

      if (currentActive) {
        moveModeIndicator(currentActive);
      }
    });
  }

  /**
   * 視窗尺寸改變時重新校正切換器。
   */
  function realignModeIndicator() {
    const currentActive = document.querySelector(".mode-tab.active");

    if (currentActive) {
      moveModeIndicator(currentActive);
    }
  }

  /**
   * 鎖定 Modal 背後的管理頁面。
   */
  function lockPageScroll() {
    if (isPageScrollLocked) {
      return;
    }

    modalPageScrollY = window.scrollY;
    isPageScrollLocked = true;

    document.documentElement.classList.add("modal-open");

    document.body.classList.add("modal-open");

    document.body.style.position = "fixed";
    document.body.style.top = `-${modalPageScrollY}px`;
    document.body.style.left = "0";
    document.body.style.right = "0";
    document.body.style.width = "100%";
    document.body.style.overflow = "hidden";
  }

  /**
   * 解鎖管理頁面並回到原本位置。
   */
  function unlockPageScroll(restorePosition = true) {
    const restoreScrollY = modalPageScrollY;

    document.documentElement.classList.remove("modal-open");
    document.body.classList.remove("modal-open");

    document.body.style.removeProperty("position");
    document.body.style.removeProperty("top");
    document.body.style.removeProperty("left");
    document.body.style.removeProperty("right");
    document.body.style.removeProperty("width");
    document.body.style.removeProperty("overflow");

    isPageScrollLocked = false;

    if (!restorePosition) {
      return;
    }

    window.requestAnimationFrame(() => {
      window.scrollTo({
        top: restoreScrollY,
        left: 0,
        behavior: "auto",
      });

      // 通知 Header：目前捲動位置已經被程式恢復
      window.dispatchEvent(
        new CustomEvent("fissh:scroll-restored", {
          detail: {
            scrollY: restoreScrollY,
          },
        }),
      );
    });
  }

  /**
   * 開啟編輯商品 Modal。
   */
  window.openEditModal = function openEditModal() {
    const modal = document.getElementById("edit-modal-container");

    const mobileHeader = document.querySelector(".mobile-header");

    if (!modal) {
      return;
    }

    if (modal.classList.contains("show")) {
      return;
    }

    // 記住 Modal 開啟前頁首的狀態
    wasMobileHeaderHiddenBeforeModal = Boolean(mobileHeader?.classList.contains("is-hidden"));

    lockPageScroll();

    // 只隱藏頁首，不改變原本的 is-hidden 狀態
    mobileHeader?.classList.add("modal-is-open");

    modal.setAttribute("aria-hidden", "false");
    modal.classList.add("show");

    const video = modal.querySelector(".preview-video");

    if (video?.src) {
      video.muted = true;

      video.play().catch(() => {
        // 瀏覽器拒絕自動播放時不處理
      });
    }

    const closeButton = modal.querySelector(".modal-close-btn, [data-modal-close]");

    closeButton?.focus();
  };

  /**
   * 關閉編輯商品 Modal。
   */
  window.closeEditModal = function closeEditModal() {
    const modal = document.getElementById("edit-modal-container");

    const mobileHeader = document.querySelector(".mobile-header");

    if (!modal) {
      unlockPageScroll(false);
      return;
    }

    modal.querySelectorAll("video").forEach((video) => {
      video.pause();

      if (video.src && video.src.startsWith("blob:")) {
        URL.revokeObjectURL(video.src);
      }
    });

    modal.classList.remove("show");
    modal.setAttribute("aria-hidden", "true");

    if (mobileHeader) {
      mobileHeader.classList.remove("modal-is-open");

      // 恢復開啟 Modal 前的頁首狀態
      mobileHeader.classList.toggle("is-hidden", wasMobileHeaderHiddenBeforeModal);
    }

    unlockPageScroll(true);

    window.setTimeout(() => {
      if (!modal.classList.contains("show")) {
        modal.innerHTML = "";
      }
    }, 220);
  };

  /**
   * 修復舊程式留下的 body 鎖定狀態。
   */
  function resetClosedModalState() {
    const modal = document.getElementById("edit-modal-container");

    if (modal?.classList.contains("show")) {
      return;
    }

    document.documentElement.classList.remove("modal-open");

    document.body.classList.remove("modal-open");

    document.body.style.removeProperty("position");
    document.body.style.removeProperty("top");
    document.body.style.removeProperty("left");
    document.body.style.removeProperty("right");
    document.body.style.removeProperty("width");
    document.body.style.removeProperty("overflow");

    document.querySelector(".mobile-header")?.classList.remove("modal-is-open");

    isPageScrollLocked = false;
  }

  /**
   * 點擊叉叉或具有 data-modal-close 的元素。
   */
  document.body.addEventListener("click", (event) => {
    const closeButton = event.target.closest(".modal-close-btn, [data-modal-close]");

    if (closeButton) {
      event.preventDefault();
      event.stopPropagation();

      window.closeEditModal();
      return;
    }

    const modal = document.getElementById("edit-modal-container");

    // 直接點擊黑色遮罩時關閉
    if (modal && event.target === modal && modal.classList.contains("show")) {
      window.closeEditModal();
    }
  });

  /**
   * 按下 ESC 關閉 Modal。
   */
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") {
      return;
    }

    const modal = document.getElementById("edit-modal-container");

    if (modal?.classList.contains("show")) {
      window.closeEditModal();
    }
  });

  /**
   * HTMX 可以觸發此事件來關閉 Modal。
   */
  document.body.addEventListener("closeEditModal", () => {
    window.closeEditModal();
  });

  /**
   * 初始化。
   */
  function initializeManagePage() {
    resetClosedModalState();
    initializeModeToggle();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeManagePage, {
      once: true,
    });
  } else {
    initializeManagePage();
  }

  // 瀏覽器上一頁返回時，也清除殘留鎖定
  window.addEventListener("pageshow", resetClosedModalState);

  window.addEventListener("resize", realignModeIndicator);
})();
