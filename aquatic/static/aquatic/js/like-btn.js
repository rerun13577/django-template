// 🚀 FisshShop 萬用點讚總機 (文章、留言共用)
document.querySelectorAll(".like-btn, .comment-like-btn").forEach((button) => {
  // 監聽器
  button.addEventListener("click", async function (e) {
    // 攔截瀏覽器的預設動作（例如跳轉頁面），讓訊號只跑我們寫的邏輯
    e.preventDefault();

    // 🛡️ 第一道防線：前端攔截
    // getAttribute 去讀取前端data-authenticated的狀態
    const isAuthenticated = this.getAttribute('data-authenticated') === 'true';
    if (!isAuthenticated) {
        window.location.href = `/accounts/login/?next=${window.location.pathname}`;
        return;
    }

    // 📡 訊號定址：判斷是文章還是留言
    // this.dataset：讀取按鈕身上的資料位址（ID）
    //  前端寫data-comment-id="{{ comment.id }}" 後端用this.dataset抓
    // 不管是文章還是留言，只要是有編號的零件，通通把那個數字拿過來存進 id 這個暫存器裡。
    // classList.contains 檢查零件的 「特徵（Class）」
    // 如果 isComment 是 True $\rightarrow$ 執行 : 左邊的網址。
    // 如果 isComment 是 False $\rightarrow$ 執行 : 右邊的網址。
    const id = this.dataset.postId || this.dataset.commentId;
    const isComment = this.classList.contains('comment-like-btn');
    const apiUrl = isComment ? `/comment/like/${id}/` : `/blog/like/${id}/`;
    
    const actionNum = this.querySelector(".action-num");

    try {
      // 把apiurl送出去
      // post(寫入/改變)：就像是按下「寫入暫存器」的按鈕。
      // X-CSRFToken讓這次的點擊產生唯一性 後台會對照密碼密碼正確才會照做
      // 用json 解讀
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Content-Type": "application/json",
        },
      });

      // 🛡️ 第二道防線：後端 401 攔截 (雙重保險)
      // 這是在檢查 「狀態暫存器」。401 在 HTTP 協議中代表「Unauthorized（未授權）」。
      if (response.status === 401) {
        window.location.href = `/accounts/login/?next=${window.location.pathname}`;
        return;
      }

      if (response.ok) {
        const data = await response.json();
        // 🎨 UI 更新：變色與改數字
        // 這行很聰明！它會看 data.is_liked 是 true 還是 false。
        // 如果是 true（按讚成功），它就把 liked 這個 CSS 類別焊上去（變紅）。
        // 如果是 false（取消按讚），它就把 liked 拔掉（變回灰色）。
        this.classList.toggle("liked", data.is_liked);
        // innerText：把解碼出來的最新數字 new_count 直接寫入畫面的數字元件。
        if (actionNum) actionNum.innerText = data.new_count;
      }
    } catch (error) {
      console.error("訊號傳輸失敗：", error);
    }
      //catch：這就是你的 「安全機制」。
      //守什麼？ 如果剛好你點下去的瞬間 Wi-Fi 斷了，或是伺服器突然當機，fetch 就會報錯。
      //功能：如果沒有這層 catch，你的網頁 JS 可能會直接卡死。有了它，它只會把錯誤印在控制台（Console），保證主程式（網頁其他功能）不會壞掉。
  });
});

// 使用者點一下讚，你的 fisshshop.com 就會當機 0.5 秒。
// 這就是「非同步」存在的意義：讓網路傳輸在背景跑，不影響主畫面的流暢。

// .forEach((button) => { ... })：這是一個「批次作業」。
// 它會一個一個拿起清單裡的按鈕（暫時叫它 button），對每一個按鈕執行大括號 {} 裡面的動作。
// () 裡面放的是對象，{} 裡面放的是動作

// 小括號 ()：這叫「傳輸口」。
// 用來放「參數」或是「條件」。像 if (條件)，或是 function(收進來的訊號)。

// 大括號 {}：這叫「處理區塊（Scope）」。
// 這對括號中間夾住的程式碼，就是一個「完整的動作包」。當條件達成時，系統會執行這一整包。

// 點點 .：這叫「接腳（Access）」。
// 例如 this.dataset，代表我要去 this 這個零件裡面找名為 dataset 的接腳。

// const / let：定義一個「變數」或是「常數」。這就像是在 PCB 上定義一個有名字的 測試點 (Test Point)。
// addEventListener：這就是 「中斷（Interrupt）」。
// 告訴瀏覽器：「平時不用動，但只要這個按鈕被按到（電位變化），就立刻跳進來執行程式。」

// fetch：就像發出一個 UART 封包。
// await：就像在寫 delay()，但它是高等級的「等訊號回來才繼續」。

// 如果你的標籤是 <a> (超連結)：
// 它會直接跳轉到 href 屬性寫的那個網址。

// 如果你的標籤是 <form> 裡的 <button>：
// 它會觸發「提交（Submit）」，這會導致整張網頁重新載入（Reload）。