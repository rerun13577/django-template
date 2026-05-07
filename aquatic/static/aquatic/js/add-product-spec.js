// 1. 定義白名單 (哪些格子可以填文字)
const textOnlyFields = ["性情", "食性", "光照需求", "水流強度"];

// 2. 數值即時過濾 (整合版：只留這一個)
document.addEventListener("input", function (e) {
  const el = e.target;
  const label = el.name;

  if (!el.classList.contains("spec-input-field") || el.tagName === "SELECT") return;

  // 🚀 因：在白名單內。果：直接放行，不執行數字過濾。
  if (textOnlyFields.some((key) => label.includes(key))) {
    console.log(`✅ ${label} 命中白名單，允許文字`);
    return;
  }

  // 🚀 因：不在白名單。果：只允許數字和小數點。
  el.value = el.value.replace(/[^0-9.]/g, "");
});

// 3. 邏輯檢查 (離開焦點後觸發)
document.addEventListener("focusout", function (e) {
  const el = e.target;
  if (!el.classList.contains("spec-input-field") || el.tagName === "SELECT") return;

  const label = el.name;
  if (textOnlyFields.some((key) => label.includes(key))) return;

  const num = parseFloat(el.value);
  if (isNaN(num)) return;

  // 數值合理性檢查
  if (label.includes("pH")) {
    if (num > 14) {
      alert("pH 值不能超過 14！");
      el.value = 14;
    } else if (num < 0) el.value = 0;
  } else if (label.includes("溫度") && num > 100) {
    alert("這溫度會煮熟魚！");
    el.value = "";
  } else if (label.includes("比重")) {
    if (num > 1.1) {
      alert("比重異常！請確認數值");
      el.value = "";
    } else if (num < 1.0) el.value = 1.0;
  } else if (label.includes("GH") && num > 30) {
    alert("GH 硬度超過 30 建議確認數值！");
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
          alert(`${base} 的最小值必須小於最大值！`);
          el.value = "";
          el.focus();
        }
      }
    }
  }
});

// 4. 編輯開窗邏輯
window.openEditSpec = function (id, name, data, btn) {
  const item = btn.closest(".accordion-item");
  const form = document.getElementById("add-spec-form");
  if (!form) return;

  document.getElementById("edit-spec-id").value = id;
  document.getElementById("new-spec-name").value = name;

  form.querySelectorAll(".spec-input-field").forEach((el) => (el.value = ""));
  for (const [key, value] of Object.entries(data)) {
    const input = form.querySelector(`[name="${key}"]`);
    if (input) input.value = value;
  }
  uiShowForm(item, form);
};

htmx.logAll();
