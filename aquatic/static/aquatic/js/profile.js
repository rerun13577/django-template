// ────────────────────────────────────────────────────────
// 🚀 模組 A：分頁滑動動畫與地點初始化
// ────────────────────────────────────────────────────────
function syncTab(modal, index) {
  if (!modal) return;
  const slider = modal.querySelector("#tabs-slider");
  const tabsWindow = modal.querySelector(".tabs-window");
  const contents = modal.querySelectorAll(".tab-content");

  const tabIndex = parseInt(index, 10) || 0;
  const movePercentage = tabIndex * (100 / 3);
  if (slider) slider.style.transform = `translateX(-${movePercentage}%)`;

  const targetContent = contents[tabIndex];
  if (targetContent && tabsWindow) {
    tabsWindow.style.height = targetContent.offsetHeight + "px";
  }
}

// 🎯 監聽 HTMX 載入事件：當 Modal 被動態塞入網頁時，立刻初始化功能
document.addEventListener("htmx:afterSwap", (e) => {
  const modal = document.getElementById("profile-edit-modal");
  if (!modal) return;

  // 1. 初始化分頁標籤
  const tabs = modal.querySelectorAll(".tab-item");
  tabs.forEach((tab, index) => tab.setAttribute("data-index", index));
  setTimeout(() => syncTab(modal, 0), 60);

  // 2. 🗺️ 接管全台面交地點連動電路
  initLocationCircuit(modal);
});

// 🗺️ 地點連動核心電路（從 HTML 探針動態撈資料）
function initLocationCircuit(modal) {
  const citySelect = modal.querySelector("#city-select");
  const zoneSelect = modal.querySelector("#zone-select");
  const hiddenInput = modal.querySelector("#hidden-city-region");
  const dataProbe = modal.querySelector("#js-taiwan-regions-data");

  // 防禦中斷線路：少一個組件直接收工，確保不噴錯誤卡死
  if (!citySelect || !zoneSelect || !hiddenInput || !dataProbe) return;

  // 📥 核心：解碼 HTML 探針吐出來的 Django JSON 變數
  let taiwanRegions = {};
  try {
    taiwanRegions = JSON.parse(dataProbe.dataset.json);
  } catch (err) {
    return;
  }

  // 解析目前資料庫儲存的「新北市中和區」
  const savedCityRegion = hiddenInput.value || "";
  let savedCity = "";
  let savedZone = "";

  if (savedCityRegion) {
    for (const city in taiwanRegions) {
      if (savedCityRegion.startsWith(city)) {
        savedCity = city;
        savedZone = savedCityRegion.replace(city, "");
        break;
      }
    }
  }

  // 更新行政區域選項
  function updateZoneOptions(skipCombine = false) {
    const selectedCity = citySelect.value;
    zoneSelect.innerHTML = '<option value="">-- 區域 --</option>';

    if (selectedCity && taiwanRegions[selectedCity]) {
      taiwanRegions[selectedCity].forEach((zone) => {
        const option = document.createElement("option");
        option.value = zone;
        option.textContent = zone;
        if (zone === savedZone && selectedCity === savedCity) {
          option.selected = true;
        }
        zoneSelect.appendChild(option);
      });
    }
    if (!skipCombine) combineFullAddress();
  }

  function combineFullAddress() {
    hiddenInput.value = citySelect.value + zoneSelect.value;
  }

  // 物理綁定下拉選單事件
  citySelect.addEventListener("change", () => updateZoneOptions(false));
  zoneSelect.addEventListener("change", combineFullAddress);

  // 導通電路：如果原本就有選過縣市，開彈窗自動點亮對應區域
  if (savedCity) {
    citySelect.value = savedCity;
    updateZoneOptions(true);
  }
}

// 全域監聽分頁標籤點擊
document.addEventListener("click", (e) => {
  const tab = e.target.closest(".profile-tabs .tab-item");
  if (!tab) return;

  const container = tab.closest("#profile-info-section") || tab.closest("#profile-edit-modal");
  if (!container) return;

  const tabs = container.querySelectorAll(".tab-item");
  const index = tab.getAttribute("data-index");

  tabs.forEach((t) => t.classList.remove("active"));
  tab.classList.add("active");
  syncTab(container, index);
});

// 視窗縮放防線
window.addEventListener("resize", () => {
  const modal = document.getElementById("profile-edit-modal") || document.getElementById("profile-info-section");
  if (!modal) return;
  const activeTab = modal.querySelector(".tab-item.active");
  const activeIndex = activeTab ? activeTab.getAttribute("data-index") : 0;
  syncTab(modal, activeIndex);
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

// ────────────────────────────────────────────────────────
// 🚀 模組 C：照片即時預覽與移除（舊圖相容＋叉叉按鈕安全隔離版）
// ────────────────────────────────────────────────────────
document.addEventListener("change", (e) => {
  const input = e.target.closest("#profile-edit-modal .profile-image-input");
  if (!input) return;

  const file = e.target.files[0];
  const previewSelector = input.dataset.preview; // 🎯 對接 HTML 的 "#avatar-preview" 或 "#background-preview"
  const fieldGroup = input.closest(".input-field-group");
  const previewContainer = fieldGroup ? fieldGroup.querySelector(previewSelector) : null;

  if (!previewContainer) return;

  if (file) {
    const reader = new FileReader();
    reader.onload = (readerEvent) => {
      const imageUrl = readerEvent.target.result;

      // ⚡ 關鍵修正：清空容器內部（無論原本是舊圖還是空白），重新灌入新電路
      previewContainer.innerHTML = "";

      const imgWrapper = document.createElement("div");
      imgWrapper.classList.add("image-preview-wrapper");

      const img = document.createElement("img");
      img.src = imageUrl;
      img.classList.add("image-preview");

      const removeBtn = document.createElement("button");
      removeBtn.type = "button";
      removeBtn.classList.add("remove-image-btn");
      removeBtn.innerHTML = "&times;";

      // 物理退火防線：按叉叉時不只清空網頁，也要把實體 input.value 拔掉，後端才不會誤吞
      removeBtn.addEventListener("click", () => {
        previewContainer.innerHTML = "";
        input.value = "";
      });

      imgWrapper.appendChild(img);
      imgWrapper.appendChild(removeBtn);
      previewContainer.appendChild(imgWrapper);
    };
    reader.readAsDataURL(file);
  } else {
    previewContainer.innerHTML = "";
    input.value = "";
  }
});
