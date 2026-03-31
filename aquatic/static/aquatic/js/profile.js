document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab-item');
    const slider = document.getElementById('tabs-slider');
    const tabsWindow = document.querySelector('.tabs-window');
    const contents = document.querySelectorAll('.tab-content');

    if (!slider || !tabsWindow || contents.length === 0) return;

    // 🚀 核心：同步更新位置與高度
    function syncTab(index) {
        console.log(`切換分頁: ${index}`);
        
        // 1. 處理位移 (300% 寬度，每格 33.33%)
        const movePercentage = index * (100 / 3);
        slider.style.transform = `translateX(-${movePercentage}%)`;

        // 2. 處理高度
        const targetContent = contents[index];
        const targetHeight = targetContent.offsetHeight;
        
        // 🚀 因：有些圖片可能還在載入中，offsetHeight 抓不到最終高度。
        // 🚀 果：我們設定高度，並針對內容中的圖片掛載監聽器。
        tabsWindow.style.height = (targetHeight) + 'px'; 

        // 監聽該分頁內的圖片是否載入完成，載入完就重算一次高度
        const imgs = targetContent.querySelectorAll('img');
        imgs.forEach(img => {
            if (!img.complete) {
                img.addEventListener('load', () => {
                    // 圖片跑出來後，重新校正一次高度
                    const updatedHeight = targetContent.offsetHeight;
                    tabsWindow.style.height = (updatedHeight) + 'px';
                }, { once: true }); // 確保只觸發一次
            }
        });
    }

    // 🚀 初始化修正
    // 因：DOMContentLoaded 只保證 HTML 標籤排好，不保證圖片抓完。
    // 果：我們用 window.onload 做二次校正，這才是圖片全出來的時間點。
    window.addEventListener('load', () => {
        syncTab(0);
    });

    // 🚀 點擊事件
    tabs.forEach((tab, index) => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            syncTab(index);
        });
    });

    // 🚀 額外加強：視窗縮放時也要重算，不然 RWD 會跑掉
    window.addEventListener('resize', () => {
        const activeTab = document.querySelector('.tab-item.active');
        const activeIndex = activeTab ? activeTab.getAttribute('data-index') : 0;
        syncTab(activeIndex);
    });
});