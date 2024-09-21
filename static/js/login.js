document.addEventListener('DOMContentLoaded', function() {
    // 检查是否登录成功
    if (document.body.classList.contains('logged-in')) {
        // 清除历史记录
        window.history.pushState(null, "", window.location.href);
        window.onpopstate = function () {
            window.history.pushState(null, "", window.location.href);
        };
    }
});