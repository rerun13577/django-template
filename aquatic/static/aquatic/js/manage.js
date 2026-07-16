// manage.js
// 商品管理頁共用功能：上架表單切換、切換背景、HTMX CSRF。

"use strict";

/**
 * 取得指定 Cookie。
 *
 * HTMX 發送 POST 請求時，需要使用 Django 的 csrftoken。
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
 * 自動替所有 HTMX 請求加入 Django CSRF Token。
 */
document.addEventListener("htmx:configRequest", (event) => {
  const csrfToken = getCookie("csrftoken");

  if (csrfToken) {
    event.detail.headers["X-CSRFToken"] = csrfToken;
  }
});

/**
 * 將切換器的活動背景移動到指定按鈕。
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
 * 切換上架表單的顯示狀態。
 *
 * mode:
 * - off：隱藏表單
 * - single：顯示表單
 */
window.switchMode = function (button, mode) {
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
 * 視窗寬度改變時，重新計算活動背景位置。
 */
function realignModeIndicator() {
  const currentActive = document.querySelector(".mode-tab.active");

  if (currentActive) {
    moveModeIndicator(currentActive);
  }
}

document.addEventListener("DOMContentLoaded", initializeModeToggle);
window.addEventListener("resize", realignModeIndicator);
