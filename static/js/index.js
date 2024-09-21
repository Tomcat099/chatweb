document.addEventListener('DOMContentLoaded', function() {
    console.log('首页加载完成');
    
    // 示例：为按钮添加点击效果
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.target.style.transform = 'scale(0.95)';
            setTimeout(() => {
                e.target.style.transform = 'scale(1)';
            }, 100);
        });
    });
});