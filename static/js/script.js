window.toggleMenu = function() {
    var menu = document.getElementById("avatar-menu");
    console.log("Toggle menu called. Current display:", menu.style.display);
    if (menu.style.display === "none" || menu.style.display === "") {
        menu.style.display = "block";
        console.log("Menu should now be visible");
    } else {
        menu.style.display = "none";
        console.log("Menu should now be hidden");
    }
};

function logClickEvent(element, details) {
    fetch('/log_click', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            element: element,
            details: details
        }),
    });
}

(function() {
    let chatDiv, questionInput, submitButton, newChatButton, clearAllHistoryButton, fileUpload, historyList;
    let allConversations = [];
    let currentConversation = { id: null, title: '', messages: [] };
    let isViewingHistory = false;

    document.addEventListener('DOMContentLoaded', function() {
        chatDiv = document.getElementById('chat');
        questionInput = document.getElementById('question');
        submitButton = document.getElementById('submit');
        newChatButton = document.getElementById('newChat');
        clearAllHistoryButton = document.getElementById('clearAllHistory');
        fileUpload = document.getElementById('fileUpload');
        historyList = document.getElementById('historyList');

        submitButton.addEventListener('click', function() {
            logClickEvent('提交问题按钮');
            console.log('Submit button clicked');
            askQuestion();
        });
        questionInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                logClickEvent('提交问题按钮');
                console.log('Enter key pressed');
                askQuestion();
            }
        });

        newChatButton.addEventListener('click', function() {
            logClickEvent('新建对话按钮');
            startNewChat();
        });
        clearAllHistoryButton.addEventListener('click', function() {
            logClickEvent('清空历史记录按钮');
            confirmClearAllHistory();
        });
        fileUpload.addEventListener('change', handleFileUpload);

        appendMessage('system', '你好，很高兴认识你');
        loadHistoryFromServer();

        document.addEventListener('click', hideMenu);
        
        document.getElementById("avatar-menu").addEventListener('click', function(event) {
            event.stopPropagation();
        });
    });

    function startNewChat() {
        if (!isViewingHistory && currentConversation.messages.length > 0) {
            saveCurrentConversation();
        }
        chatDiv.innerHTML = '';
        currentConversation = { id: null, title: '', messages: [] };
        appendMessage('system', '你好，很高兴认识你');
        isViewingHistory = false;
        updateHistoryList();
    }

    function saveCurrentConversation() {
        if (currentConversation.title && currentConversation.messages.length > 0) {
            const existingIndex = allConversations.findIndex(conv => conv.title === currentConversation.title);
            if (existingIndex !== -1) {
                allConversations[existingIndex] = {...currentConversation};
            } else {
                allConversations.push({...currentConversation});
            }
        }
    }

    function updateHistoryList() {
        historyList.innerHTML = '';
        allConversations.forEach((conv, index) => {
            const historyItem = document.createElement('div');
            historyItem.classList.add('history-item');
            
            const titleSpan = document.createElement('div');
            titleSpan.classList.add('history-item-text');
            const title = conv.title || `对话 ${index + 1}`;
            titleSpan.textContent = title;
            titleSpan.setAttribute('data-full-text', title);
            titleSpan.title = title;
            titleSpan.addEventListener('click', () => loadConversation(conv.id));
            
            const deleteIcon = document.createElement('div');
            deleteIcon.classList.add('history-item-delete');
            const iconImg = document.createElement('img');
            iconImg.src = '/static/svg/delete.svg';
            iconImg.alt = '删除';
            iconImg.classList.add('svg-icon');
            deleteIcon.appendChild(iconImg);
            deleteIcon.addEventListener('click', (e) => {
                e.stopPropagation();
                confirmDeleteConversation(conv.id);
            });
            
            historyItem.appendChild(titleSpan);
            historyItem.appendChild(deleteIcon);
            historyList.appendChild(historyItem);
        });
    }

    function loadConversation(conversationId) {
        logClickEvent('历史记录项', `历史记录ID: ${conversationId}`);
        fetch(`/get_conversation/${conversationId}`)
            .then(response => response.json())
            .then(data => {
                currentConversation = {
                    id: conversationId,
                    title: data.messages[0]?.content || '空对话',
                    messages: data.messages
                };
                chatDiv.innerHTML = '';
                currentConversation.messages.forEach(msg => {
                    appendMessage(msg.sender, msg.content);
                });
                isViewingHistory = true;
                updateHistoryList();
            })
            .catch(error => console.error('Error:', error));
    }

    function confirmDeleteConversation(conversationId) {
        if (confirm("是否删除当前对话记录？")) {
            logClickEvent('删除历史记录', `历史记录ID: ${conversationId}`);
            fetch(deleteHistoryUrl + conversationId, {
                method: 'DELETE',
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    allConversations = allConversations.filter(conv => conv.id !== conversationId);
                    updateHistoryList();
                    if (isViewingHistory && conversationId === currentConversation.id) {
                        startNewChat();
                    }
                } else {
                    console.error('Failed to delete conversation');
                }
            })
            .catch(error => console.error('Error:', error));
        }
    }

    function confirmClearAllHistory() {
        if (confirm("是否删除所有对话记录？")) {
            logClickEvent('清空历史记录按钮');
            Promise.all(allConversations.map(conv => 
                fetch(deleteHistoryUrl + conv.id, { method: 'DELETE' })
            ))
            .then(() => {
                allConversations = [];
                updateHistoryList();
                startNewChat();
            })
            .catch(error => console.error('Error:', error));
        }
    }

    function askQuestion() {
        console.log('askQuestion function called');
        const question = questionInput.value.trim();
        console.log('Question:', question);
        if (question) {
            console.log('Question is not empty, proceeding...');
            if (isViewingHistory) {
                console.log('Viewing history, starting new chat');
                startNewChat();
            }
            
            if (!currentConversation.title) {
                console.log('Setting conversation title');
                currentConversation.title = question;
            }
            console.log('Appending user message');
            appendMessage('user', question);
            console.log('Sending request to /ask');
            fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question,
                    conversation_id: currentConversation.id,
                    is_new_conversation: !currentConversation.id
                }),
            })
            .then(response => {
                console.log('Response status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Response received:', data);
                appendMessage('system', data.answer);
                currentConversation.id = data.conversation_id;
                currentConversation.messages.push(
                    { sender: 'user', content: question },
                    { sender: 'system', content: data.answer }
                );
                isViewingHistory = false;
                loadHistoryFromServer();
            })
            .catch((error) => {
                console.error('Error:', error);
                appendMessage('system', '抱歉,出现了错误。');
            });
            questionInput.value = '';
        } else {
            console.log('Question is empty, not sending request');
        }
    }

    function appendMessage(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender + '-message');

        const avatarDiv = document.createElement('div');
        avatarDiv.classList.add('message-avatar');
        avatarDiv.style.backgroundImage = sender === 'user' 
            ? `url("${userAvatar}")` 
            : 'url("/static/uploads/system.jpg")';

        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        contentDiv.textContent = message;

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        chatDiv.appendChild(messageDiv);
        chatDiv.scrollTop = chatDiv.scrollHeight;
    }

    function handleFileUpload(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const content = e.target.result;
                questionInput.value = `文件内容: ${content.substring(0, 100)}...`;
            };
            reader.readAsText(file);
        }
    }

    function toggleMenu() {
        var menu = document.getElementById("avatar-menu");
        if (menu.style.display === "none" || menu.style.display === "") {
            menu.style.display = "block";
        } else {
            menu.style.display = "none";
        }
    }

    function confirmDelete() {
        if (confirm("确定要注销账户吗？此操作将删除所有相关数据且不可恢复。")) {
            window.location.href = deleteAccountUrl;
        }
    }

    function hideMenu(event) {
        var menu = document.getElementById("avatar-menu");
        var avatar = document.querySelector(".user-avatar");
        if (!avatar.contains(event.target) && !menu.contains(event.target) && menu.style.display === "block") {
            menu.style.display = "none";
        }
    }

    function loadHistoryFromServer() {
        fetch('/get_history')
            .then(response => response.json())
            .then(data => {
                allConversations = data;
                updateHistoryList();
            })
            .catch(error => console.error('Error:', error));
    }
})();