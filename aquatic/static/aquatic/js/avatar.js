window.addEventListener('error', function(e) {
    if (e.target.tagName === 'IMG') {
        // 根據你提供的實體路徑，網址應該是這一個：
        const defaultSrc = '/static/image/no-avatar.jpg';
        
        if (e.target.src.includes(defaultSrc)) {
            return;
        }

        console.log('偵測到破圖，更換為預設頭像');
        e.target.src = defaultSrc;
    }
}, true);