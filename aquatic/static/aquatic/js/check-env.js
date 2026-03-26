// `function checkLoginEnvironment() {
//     const ua = navigator.userAgent || navigator.vendor || window.opera;
//     const isInApp = /Threads|Line|FBAN|FBAV|Instagram|TikTok/i.test(ua);
//     const isAndroid = /Android/i.test(ua);
//     const isiOS = /iPhone|iPad|iPod/i.test(ua);

//     if (isInApp) {
//         // 顯示彈窗
//         document.getElementById('login-guide-overlay').style.display = 'block';

//         if (isAndroid) {
//             // Android 處理：設定 Intent 跳轉連結
//             const rawUrl = window.location.href.replace(/^https?:\/\//, '');
//             const intentUrl = `intent://${rawUrl}#Intent;scheme=https;package=com.android.chrome;end`;
//             const btn = document.getElementById('android-jump-link');
//             btn.href = intentUrl;
//             btn.style.display = 'block';
//         } else if (isiOS) {
//             // iOS 處理：顯示手動指示
//             document.getElementById('ios-instruction').style.display = 'block';
//         }
//         return false; // 阻斷原本的登入流程
//     }
//     return true; // 環境安全，允許執行登入
// }`

function checkLoginEnvironment() {
    const ua = navigator.userAgent || navigator.vendor || window.opera;
    
    // 🚀 核心：包含 Barcelona (Threads iOS) 與 IABMV (Meta 新版標籤)
    const isInApp = /Threads|Barcelona|Line|FBAN|FBAV|Instagram|TikTok|FB_IAB|FBSS|IABMV/i.test(ua);
    
    const isAndroid = /Android/i.test(ua);
    const isiOS = /iPhone|iPad|iPod/i.test(ua);

    if (isInApp) {
        // 1. 顯示遮罩並鎖定背景滾動
        const overlay = document.getElementById('login-guide-overlay');
        if (overlay) {
            overlay.style.display = 'flex'; // 使用 flex 確保內容居中
            document.body.classList.add("no-scroll");
        }

        // 2. 針對平台顯示跳轉指令
        if (isAndroid) {
            const rawUrl = window.location.href.replace(/^https?:\/\//, '');
            // 產生 Intent 連結強制喚醒 Chrome
            const intentUrl = `intent://${rawUrl}#Intent;scheme=https;package=com.android.chrome;end`;
            const btn = document.getElementById('android-jump-link');
            if (btn) {
                btn.href = intentUrl;
                btn.style.display = 'block';
            }
        } else if (isiOS) {
            // iOS 無法強制跳轉，顯示「右上角開啟」指示
            const iosInstr = document.getElementById('ios-instruction');
            if (iosInstr) iosInstr.style.display = 'block';
        }
        return false; // 阻斷點擊流程
    }
    return true; // 環境安全
}

// 🚀 自動執行：頁面載入完成後立即檢查一次環境
window.addEventListener('DOMContentLoaded', () => {
    // 如果偵測到在 App 內，直接顯示引導（不必等按按鈕）
    const ua = navigator.userAgent || navigator.vendor || window.opera;
    const isInApp = /Threads|Barcelona|Line|FBAN|FBAV|Instagram|TikTok|FB_IAB|FBSS|IABMV/i.test(ua);
    
    if (isInApp) {
        checkLoginEnvironment();
    }
});