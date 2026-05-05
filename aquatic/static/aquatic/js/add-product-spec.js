// 2. 數值即時過濾 (排除選單)
document.addEventListener("input", function (e) {
  const el = e.target;
  if (el.classList.contains("spec-input-field") && el.tagName !== "SELECT") {
    el.value = el.value.replace(/[^0-9.]/g, "");
  }
});

// 3. 邏輯檢查 (離開焦點後觸發)
document.addEventListener("focusout", function (e) {
  const el = e.target;
  if (!el.classList.contains("spec-input-field") || el.tagName === "SELECT") return;

  const num = parseFloat(el.value);
  const label = el.name;
  if (isNaN(num)) return;

  // 數值合理性 (pH & 溫度)
  if (label.includes("pH")) {
    if (num > 14) {
      alert("pH 值不能超過 14！");
      el.value = 14;
    } else if (num < 0) {
      el.value = 0;
    }
  }
  if (label.includes("溫度") && num > 100) {
    alert("這溫度會煮熟魚！");
    el.value = "";
  }

  // 區間檢查 (Min < Max)
  if (label.includes("pH") || label.includes("溫度")) {
    const container = el.closest(".range-inputs");
    if (container) {
      const base = label.split("_")[0]; // 取得 pH 或 適宜溫度
      const minEl = container.querySelector(`[name="${base}_min"]`);
      const maxEl = container.querySelector(`[name="${base}_max"]`);

      if (minEl?.value && maxEl?.value) {
        const minV = parseFloat(minEl.value);
        const maxV = parseFloat(maxEl.value);
        if (minV >= maxV) {
          alert("最小值必須小於最大值！");
          el.value = "";
          el.focus();
        }
      }
    }
  }
});

// add-product-spec.js

window.openEditSpec = function (id, name, data, btn) {
  const item = btn.closest(".accordion-item");
  const form = document.getElementById("add-spec-form");
  if (!form) return;

  // 1. 填寫基礎資料
  document.getElementById("edit-spec-id").value = id;
  document.getElementById("new-spec-name").value = name;

  // 2. 清空舊資料並回填新資料
  form.querySelectorAll(".spec-input-field").forEach((el) => (el.value = ""));
  for (const [key, value] of Object.entries(data)) {
    const input = form.querySelector(`[name="${key}"]`);
    if (input) input.value = value;
  }

  // 3. 對稱點：呼叫 manage.js 裡的動畫邏輯
  uiShowForm(item, form);
};

htmx.logAll();
