document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab-item');
    const slider = document.getElementById('tabs-slider');
    const tabsWindow = document.querySelector('.tabs-window');
    const contents = document.querySelectorAll('.tab-content');

    // 🚀 因：統一更新畫面的函式。果：讓代碼更容易維護，初始化跟點擊都能共用。
    function updateProfileTab(index) {
        // 1. 處理位移 (火車滑動)
        slider.style.transform = `translateX(-${index * (100 / 3)}%)`;

        // 2. 處理高度 (視窗伸縮)
        // 抓取目標內容的 offsetHeight，並強制設定給觀景窗
        const targetHeight = contents[index].offsetHeight;
        tabsWindow.style.height = `${targetHeight + 100}px`;
    }

    // 初始化：進入頁面時，先根據第一個分頁（貼文）設定高度
    if (contents.length > 0) {
        updateProfileTab(0);
    }

    tabs.forEach((tab, index) => {
        tab.addEventListener('click', () => {
            // 3. 處理標籤發亮 (Active 狀態)
            // 先拔掉所有人，再幫自己戴上
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // 執行滑動與高度更新
            updateProfileTab(index);
        });
    });
});