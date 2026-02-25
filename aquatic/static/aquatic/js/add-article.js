// 抓取元素
const addBtn = document.querySelector('.add-article-btn'); // 你的綠色加號
const closeBtn = document.getElementById('closeBtn');      // 你的返回按鈕
const modal = document.getElementById('add-article-overlay');

// 點擊「+」：打開
addBtn.addEventListener('click', () => {
    modal.classList.add('is-active');
    // 🚀 雙重鎖死：html 跟 body 都不要動
    document.documentElement.style.overflow = 'hidden';
    document.body.style.overflow = 'hidden'; 
    // 禁止底層頁面捲動，也就是說只有add-article-page可以滾動
});

// 點擊「返回」：關閉
closeBtn.addEventListener('click', () => {
    modal.classList.remove('is-active');
    document.body.style.overflow = 'auto'; // 恢復捲動
    document.documentElement.style.overflow = ''; // 恢復html的overflow
});