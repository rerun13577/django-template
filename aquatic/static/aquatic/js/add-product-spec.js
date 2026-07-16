// 1. 定義白名單 (哪些格子可以填文字)
const textOnlyFields = ["性情", "食性", "光照需求", "水流強度"];

// 2. 數值即時過濾 (整合版：只留這一個)
document.addEventListener("input", function (e) {
  const el = e.target;
  const label = el.name;

  // 🚀 核心修正：同時檢查兩種 Class 名稱
  const isSpecField = el.classList.contains("spec-input-field") || el.classList.contains("e-spec-input-field");

  if (!isSpecField || el.tagName === "SELECT") return;

  if (textOnlyFields.some((key) => label.includes(key))) {
    console.log(`✅ ${label} 命中白名單，允許文字`);
    return;
  }

  el.value = el.value.replace(/[^0-9.]/g, "");
});

// ==========================================
// 3. 邏輯檢查 (離開焦點後觸發) —— 修正完全體
// ==========================================
document.addEventListener("focusout", function (e) {
  const el = e.target;

  const isSpecField = el.classList.contains("spec-input-field") || el.classList.contains("e-spec-input-field");
  if (!isSpecField || el.tagName === "SELECT") return;

  const label = el.name;
  if (textOnlyFields.some((key) => label.includes(key))) return;

  const num = parseFloat(el.value);
  if (isNaN(num)) return;

  // 數值合理性檢查
  if (label.includes("pH")) {
    if (num > 14) {
      window.showCustomToast("pH 值不能超過 14！"); // 🚀 修正：改用自訂紅框
      el.value = 14;
    } else if (num < 0) el.value = 0;
  } else if (label.includes("溫度") && num > 100) {
    window.showCustomToast("這溫度會煮熟魚！"); // 🚀 修正：改用自訂紅框
    el.value = "";
  } else if (label.includes("比重")) {
    if (num > 1.1) {
      window.showCustomToast("比重異常！請確認數值"); // 🚀 修正：改用自訂紅框
      el.value = "";
    } else if (num < 1.0) el.value = 1.0;
  } else if (label.includes("GH") && num > 30) {
    window.showCustomToast("GH 硬度超過 30 建議確認數值！"); // 🚀 修正：改用自訂紅框
    el.value = 30;
  }

  // 區間檢查 (Min < Max)
  const rangeFields = ["pH", "溫度", "比重", "硬度"];
  if (rangeFields.some((key) => label.includes(key))) {
    const container = el.closest(".range-inputs");
    if (container) {
      const base = label.split("_")[0];
      const minEl = container.querySelector(`[name="${base}_min"]`);
      const maxEl = container.querySelector(`[name="${base}_max"]`);

      if (minEl?.value && maxEl?.value) {
        const minV = parseFloat(minEl.value);
        const maxV = parseFloat(maxEl.value);
        if (minV >= maxV) {
          window.showCustomToast(`${base} 的最小值必須小於最大值！`); // 🚀 修正：改用自訂紅框
          el.value = "";
          el.focus();
        }
      }
    }
  }
});

htmx.logAll();
