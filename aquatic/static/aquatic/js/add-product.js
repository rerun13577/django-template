// ==========================================
// 1. 影片上傳核心電路 (已完美調通)
// ==========================================
function triggerActiveInput(e) {
  if (e.target.closest(".delete-prod-pic-btn")) return;
  const activeInput = e.currentTarget.querySelector("#fish-video-input");
  if (activeInput) activeInput.click();
}

function handleVideoUpload(input) {
  const file = input.files[0];
  if (!file) return;

  if (file.size > 20 * 1024 * 1024) {
    alert("影片太大囉！請限制在 20MB 以內再上傳。");
    input.value = "";
    return;
  }

  const videoUrl = URL.createObjectURL(file);
  const customUploadBox = input.closest(".custom-upload-box");
  if (!customUploadBox) return;

  const bigVideo = customUploadBox.querySelector(".viewport-video");
  const placeholder = customUploadBox.querySelector(".viewport-placeholder");
  const deleteBtn = customUploadBox.querySelector(".delete-prod-pic-btn");

  if (placeholder) placeholder.style.setProperty("display", "none", "important");

  if (bigVideo) {
    bigVideo.src = videoUrl;
    bigVideo.style.display = "block";
    bigVideo.play().catch((err) => console.log("自動播放被攔截，不影響功能"));
  }

  if (deleteBtn) {
    deleteBtn.style.setProperty("display", "flex", "important");
  }
}

function removeActivePhoto(e) {
  e.stopPropagation();
  const btn = e.currentTarget;
  const container = btn.closest(".photo-upload-container");

  const input = container.querySelector("#fish-video-input");
  if (input) input.value = "";

  const bigVideo = container.querySelector(".viewport-video");
  const bigPlaceholder = container.querySelector(".viewport-placeholder");

  if (bigVideo) {
    bigVideo.pause();
    bigVideo.removeAttribute("src");
    bigVideo.load();
    bigVideo.style.display = "none";
  }

  if (bigPlaceholder) {
    bigPlaceholder.style.setProperty("display", "flex", "important");
  }
  btn.style.setProperty("display", "none", "important");
}

// 只剩下上架下架刪除 編輯交給htmx代理
function runFisshCardAction(event, action, itemId) {
  // 因為我標籤是a所以要做這個動作
  // 我如果沒有寫後面的非同步動作還是會導致網頁重新更新
  // 因為a原生的關係
  event.preventDefault();
  event.stopPropagation(); // 物理斷電：阻止外層 a 標籤跳轉

  // 其實target也會通 currenttarget是表示你裝函數的地方
  // target表示你點的地方
  const pane = event.currentTarget.closest(".fissh-card-menu-pane");
  //如果有找到就執行
  // 如果有點到我先把表單關起來等一下要顯示其他東西
  if (pane) pane.classList.remove("fissh-show");

  // 🎯 精準定位當前點擊的這張商品卡片本體
  // 因為我同一個網頁會有很多卡片所以我必須用唯一的id去搜尋
  const card = document.getElementById(`product-card-${itemId}`);
  const csrftoken = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1];
  //  一開始會像
  // "sessionid=xyz987; theme=dark; csrftoken=abc123def456"
  // 只要看到 "; "切割刀切割
  // ["sessionid=xyz987", "theme=dark", "csrftoken=abc123def456"]
  // 我把所有元素取名叫row 然後我尋找有沒有東西開頭叫做csrftoken=
  // 因為如果第一次來我網頁他會沒有csrf ?的意思是說如果沒有就不要執行了
  // csrftoken=abc123def456 這時我在對等號切一刀 ["csrftoken", "abc123def456"]
  // 因為array裡面的第二個其實就是第1個因為從0開始 然後他[1]
  // 最後存進csrftoken這個變數裡面 鏈式語法

  if (action === "delist") {
    // 因：準備向後端發送下架 POST。果：立刻幫卡片上一道鎖，變暗且防連點
    if (card) card.classList.add("fissh-loading");

    fetch(`/product/${itemId}/delist/`, {
      method: "POST",
      headers: { "X-CSRFToken": csrftoken },
    })
      .then((res) => {
        if (res.ok) {
          // 🎯 物理移動至下架區
          // 我先找到下架區
          const inactiveGrid = document.getElementById("inactive-grid");
          // 如果下架區跟卡片我都有找到才執行
          if (card && inactiveGrid) {
            // 我先空生物提醒
            const emptyHint = inactiveGrid.querySelector(".empty-hint");
            // 如果有找到代表他現在是顯示的 然後因為我下架了 所以下面就會有東西
            // 所以空生物提醒就要刪除
            if (emptyHint) emptyHint.remove();

            // APPENDCHILD是在說把CARD移動 然後移動到inactiveGrid裡面
            inactiveGrid.appendChild(card); // 卡片自動滾至下方

            // 動態重寫按鈕線路：改為上架屬性
            // [onclick*="..."]：這是 CSS 的「屬性選擇器」。
            // onclick：代表我要找標籤身上有 onclick 這個屬性的。
            // *="delist" 代表包含delist
            const delistBtn = card.querySelector('[onclick*="delist"]');
            if (delistBtn) {
              // 把<div><div>裡面的文字改變 當然其他標籤也可以
              delistBtn.textContent = "上架商品";

              // 他可以修改HTML的屬性，因為我們如果是非同步我需要到下架區的時候
              // 她下架按鈕馬上變成上架的按鈕我這裡就是她屬性修改然後丟回去給HTML
              delistBtn.setAttribute("onclick", `runFisshCardAction(event, 'relist', '${itemId}')`);
            }
          }
        }
      })
      .finally(() => {
        // 果：不論後端成功或失敗，通訊結束物理開鎖，還原字體與亮度
        if (card) card.classList.remove("fissh-loading");
      });
  } else if (action === "relist") {
    // 卡片立刻變暗、死鎖
    if (card) card.classList.add("fissh-loading");

    fetch(`/product/${itemId}/relist/`, {
      method: "POST",
      headers: { "X-CSRFToken": csrftoken },
    })
      .then((res) => {
        if (res.ok) {
          // 先尋找上架區
          const activeGrid = document.getElementById("active-grid");
          // 如果卡片跟上架區都有找到
          if (card && activeGrid) {
            // 因為我現在要上架上架如果有空提醒就取消因為我等等要上架了不會為空
            const emptyHint = activeGrid.querySelector(".empty-hint");
            if (emptyHint) emptyHint.remove();
            // 我把卡片移動到到上方
            activeGrid.appendChild(card); // 卡片自動回彈至上方

            // 動態重寫按鈕線路：改回下架屬性
            const relistBtn = card.querySelector('[onclick*="relist"]');
            if (relistBtn) {
              relistBtn.textContent = "下架商品";
              relistBtn.setAttribute("onclick", `runFisshCardAction(event, 'delist', '${itemId}')`);
            }
          }
        }
      })
      .finally(() => {
        // 這裡都一樣 要讓卡片回亮
        if (card) card.classList.remove("fissh-loading");
      });
  } else if (action === "delete") {
    console.log(`[ACTION] 觸發物理刪除，ID: ${itemId}`);

    // confirm是網頁上預設的提醒如果點擊comfire他會回傳false 但因為你前面有加一個bar 所以他會變回true
    if (!confirm("確定要刪除這商品嗎？此操作無法復原！")) {
      return; // 使用者按取消：電流直接掐斷，什麼都不發生
    }

    // 因：確定要刪，立刻上鎖變暗，防止使用者在傳輸的 0.2 秒內瘋狂連點
    if (card) card.classList.add("fissh-loading");

    // 發射非同步電訊號 這個格式是一定的
    fetch(`/product/${itemId}/delete/`, {
      method: "POST",
      headers: { "X-CSRFToken": csrftoken },
    })
      // 我後端是用action去分類
      // 這裡不用res.text()因為沒有html 你他媽的都刪掉了
      .then((res) => {
        if (res.ok) {
          // 果：資料庫那邊已經燒毀。前端直接下達 remove() 指令
          if (card) {
            // 網頁節點（DOM）當場斷根，不留任何渣滓與排版空隙
            card.remove();
            alert("商品已徹底刪除！");
          }
        } else {
          alert("刪除失敗，請再嘗試一次");
        }
      })
      // 就算前面沒有傳瀏覽器錯誤的時候他也會自己塞
      // 這個的真實性有待考察，因為我把生物刪除再沒有python manage.py runserver的時候他沒有錯誤
      .catch((err) => {
        console.error(err);
      })
      .finally(() => {
        // 安全退場：萬一沒刪成功，至少把卡片解鎖
        if (card) card.classList.remove("fissh-loading");
      });
  }
}

// 收選單(新增編輯刪除的)
document.addEventListener("DOMContentLoaded", () => {
  // 🚀 核心因果修正：改用全域事件代理，直接監聽整個 document
  document.addEventListener("click", (e) => {
    // 🎯 1. 偵測點擊目標：不論新卡片還是舊卡片，只要點擊的對象（或其祖先）包含三個點 class
    const btn = e.target.closest(".fissh-card-menu-dots");
    // 如果btn有被找到，就執行
    if (btn) {
      // 因：使用者點擊了三個點。
      // 果：物理攔截！秒斷所有向上冒泡的電流，絕對不讓外層 <a> 標籤觸發 href="/" 的跳轉！
      e.preventDefault();
      e.stopPropagation();

      const pane = btn.nextElementSibling;
      const isOpen = pane.classList.contains("fissh-show");

      // 我先搜尋全域的fissh-card-menu-pane 然後他css裡面的fissh-show移除這樣代表他就不可以顯示了
      // 我先關掉別的再開我現在有的
      // 那個p是什麼都無所謂 我設定我找到的元素叫做p
      document.querySelectorAll(".fissh-card-menu-pane").forEach((p) => p.classList.remove("fissh-show"));

      // 選單要顯示
      if (!isOpen) {
        pane.classList.add("fissh-show"); // 面板就地顯形
      }
      return; // 阻斷後續邏輯，直接退場
    }

    // 🎯 2. 全局雷達防線：如果點擊的地方跟整個選單結構無關，代表使用者想關閉選單
    // e.target就等於是用戶點擊的那個html實體 然後往上爬找不到html的外殼就執行
    if (!e.target.closest(".fissh-card-menu-wrap")) {
      document.querySelectorAll(".fissh-card-menu-pane").forEach((pane) => {
        pane.classList.remove("fissh-show");
      });
    }
  });
});

// 🚀 核心因果：偵測到檔案改變時，把檔名物理抽出來，塞進旁邊的 span 裡面
function updateCoverFilename(input) {
  const displaySpan = document.getElementById("cover-filename-display");
  if (input.files && input.files.length > 0) {
    // 瀏覽器基於資安不會給你實體路徑(C:\...)，只會給你檔名，這剛好符合你的需求
    displaySpan.textContent = input.files[0].name;
    displaySpan.style.color = "var(--primary)"; // 選完檔案變個顏色提示成功
  } else {
    displaySpan.textContent = "尚未選擇檔案";
    displaySpan.style.color = "var(--secondary)";
  }
}

// 🚀 核心因果：監聽 HTMX 的請求完成事件 (專門用來打掃戰場)
document.body.addEventListener("htmx:afterRequest", function (event) {
  // 檢查這次請求是不是成功的 (HTTP 狀態碼 200)
  if (event.detail.successful) {
    console.log("[HTMX 廣播接收] 上架成功，開始物理清空上傳區塊...");

    // 1. 物理清空「封面圖」的檔名顯示與文字顏色
    const coverDisplay = document.getElementById("cover-filename-display");
    if (coverDisplay) {
      coverDisplay.textContent = "尚未選擇檔案";
      coverDisplay.style.color = "var(--secondary)"; // 恢復預設顏色
    }

    // 2. 物理清空隱藏的 input 檔案記錄 (封面圖 + 影片)
    const coverInput = document.querySelector('input[name="fish-cover"]');
    if (coverInput) coverInput.value = "";

    const videoInput = document.getElementById("fish-video-input");
    if (videoInput) videoInput.value = "";

    // 3. (防呆) 關閉影片預覽框，恢復原本的「上傳圖示」
    const videoPreview = document.querySelector(".preview-video");
    if (videoPreview) {
      videoPreview.style.display = "none";
      videoPreview.removeAttribute("src"); // 拔掉電源
      videoPreview.load(); // 強制釋放記憶體
    }

    // 4. 隱藏影片框右上角的叉叉按鈕
    const deleteBtn = document.querySelector(".delete-prod-pic-btn");
    if (deleteBtn) {
      deleteBtn.style.setProperty("display", "none", "important");
    }

    // 5. 恢復上傳提示文字 (點擊選取影片)
    const videoPlaceholder = document.querySelector(".viewport-placeholder");
    if (videoPlaceholder) {
      videoPlaceholder.style.setProperty("display", "flex", "important");
    }
  }
});

function autoResizeTextarea(textarea) {
  textarea.style.height = "auto";
  textarea.style.height = `${textarea.scrollHeight}px`;
}

function initializeAutoResizeTextareas() {
  document.querySelectorAll("textarea.input-content-area").forEach((textarea) => {
    autoResizeTextarea(textarea);

    textarea.addEventListener("input", () => {
      autoResizeTextarea(textarea);
    });
  });
}

document.addEventListener("DOMContentLoaded", initializeAutoResizeTextareas);
