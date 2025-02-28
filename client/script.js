document.addEventListener('DOMContentLoaded', function() {
    // Initialize Lucide icons
    lucide.createIcons();

    // Chat state
    let currentChatId = null;
    let chatHistory = {}; // Cache for loaded chats
    let chatMessages = [];

    // DOM Elements
    const chatBox = document.getElementById('chatBox');
    const userInput = document.getElementById('userInput');
    const newChatBtn = document.getElementById('newChatBtn');
    const chatsList = document.getElementById('chatsList');
    const terminalContainer = document.getElementById('terminalContainer');
    const terminalOutput = document.getElementById('terminalOutput');

    // Initialize - create a new chat on load
    createNewChat();
    
    // Event Listeners
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    newChatBtn.addEventListener('click', createNewChat);

    // Functions
    async function createNewChat() {
        try {
            const response = await apiService.createNewChat();
            
            // Save current chat before switching if it exists
            if (currentChatId) {
                chatHistory[currentChatId] = chatMessages.slice();
            }
            
            currentChatId = response.chat_id;
            chatMessages = [];
            chatBox.innerHTML = '';
            
            // Add to chat history
            chatHistory[currentChatId] = [];
            
            // Add to chat list
            const chatItem = createChatItem('New Chat', currentChatId);
            chatsList.prepend(chatItem);
            setActiveChat(currentChatId);
            
            userInput.focus();
        } catch (error) {
            console.error('Error creating new chat:', error);
        }
    }

    async function loadChat(chatId) {
        try {
            console.log(`Attempting to load chat: ${chatId}`);
            
            // Save current chat state before switching
            if (currentChatId) {
                chatHistory[currentChatId] = chatMessages.slice();
            }

            // Check if we already have this chat in history
            if (chatHistory[chatId]) {
                console.log('Loading chat from cache');
                currentChatId = chatId;
                setActiveChat(chatId);
                chatMessages = chatHistory[chatId];
                displayMessages();
                return;
            }

            // Otherwise load from API
            const response = await apiService.getChat(chatId);
            if (!response) {
                console.error('No response received when loading chat');
                return;
            }

            console.log('Chat loaded successfully:', response);
            currentChatId = chatId;
            setActiveChat(chatId);

            // Clear chat box
            chatBox.innerHTML = '';

            // Load messages
            if (response.messages && response.messages.length > 0) {
                chatMessages = response.messages;
                // Save to chat history
                chatHistory[chatId] = chatMessages.slice();
                displayMessages();
            } else {
                console.log('No messages found for this chat');
                chatMessages = [];
                chatHistory[chatId] = [];
            }
        } catch (error) {
            console.error('Error loading chat:', error);
            alert('Failed to load chat. See console for details.');
        }
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        // Add user message to UI
        addMessageToUI(message, true);
        
        // Add to chat history
        const userMessage = {
            user: 'user',
            message: message
        };
        chatMessages.push(userMessage);
        chatHistory[currentChatId] = chatMessages.slice();
        
        // Save to API
        await apiService.addMessage(currentChatId, 'user', message);
        
        // Clear input
        userInput.value = '';
        
        // Get AI response
        await getAIResponse(message);
    }

    async function getAIResponse(userMessage) {
        try {
            // Show typing indicator
            const typingIndicator = document.createElement('div');
            typingIndicator.className = 'message bot-message typing';
            typingIndicator.textContent = '...';
            chatBox.appendChild(typingIndicator);
            scrollToBottom();
            
            // Prepare messages array for Ollama API
            const ollameMessages = chatMessages.map(msg => ({
                role: msg.user === 'user' ? 'user' : 'assistant',
                content: msg.message
            }));
            
            // Make API request to Ollama
            const response = await fetch('http://localhost:11434/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: 'llama3.2', // Default model, could be made configurable
                    messages: ollameMessages,
                    stream: false // For simplicity, we'll use non-streaming
                })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            typingIndicator.remove();
            
            // Get the AI response
            const aiMessage = data.message.content;
            
            // Add AI response to UI
            addMessageToUI(aiMessage, false);
            
            // Add to chat history
            const assistantMessage = {
                user: 'assistant',
                message: aiMessage
            };
            chatMessages.push(assistantMessage);
            
            // Save to API
            await apiService.addMessage(currentChatId, 'assistant', aiMessage);
            
            // Update chat title if it's a new chat
            const chatItem = document.querySelector(`.chat-item[data-chat-id="${currentChatId}"]`);
            if (chatItem && chatItem.querySelector('.chat-item-text').textContent === 'New Chat') {
                // Use the first few words of user message as title
                const title = userMessage.length > 20 ? userMessage.substring(0, 20) + '...' : userMessage;
                chatItem.querySelector('.chat-item-text').textContent = title;
            }
        } catch (error) {
            console.error('Error getting AI response:', error);
            // Remove typing indicator
            document.querySelector('.typing')?.remove();
            // Show error message
            addMessageToUI('Sorry, I had trouble connecting to the AI service. Please try again.', false);
        }
    }

    // Terminal functions
    function showTerminal(output) {
        terminalOutput.textContent = output || '';
        terminalContainer.style.display = 'flex';
    }

    function closeTerminal() {
        terminalContainer.style.display = 'none';
    }

    function playTerminal() {
        // Execute command in terminal
        console.log('Play terminal command');
    }

    function pauseTerminal() {
        // Pause terminal execution
        console.log('Pause terminal command');
    }

    function stopTerminal() {
        // Stop terminal execution
        console.log('Stop terminal command');
    }

    function restartTerminal() {
        // Restart terminal execution
        console.log('Restart terminal command');
    }

    // Load initial chat list
    async function loadChatList() {
        try {
            const chats = await apiService.getAllChats();
            
            if (chats && chats.length > 0) {
                // Clear the list first
                chatsList.innerHTML = '';
                
                // Add each chat to the list
                chats.forEach(async (chatId) => {
                    try {
                        const chatData = await apiService.getChat(chatId);
                        let title = 'Chat';
                        
                        // Use first user message as title if available
                        if (chatData.messages && chatData.messages.length > 0) {
                            const firstUserMsg = chatData.messages.find(m => m.user === 'user');
                            if (firstUserMsg) {
                                title = firstUserMsg.message.length > 20 
                                    ? firstUserMsg.message.substring(0, 20) + '...' 
                                    : firstUserMsg.message;
                            }
                        }
                        
                        const chatItem = createChatItem(title, chatId);
                        chatsList.appendChild(chatItem);
                    } catch (error) {
                        console.error('Error fetching chat details:', error);
                    }
                });
            }
        } catch (error) {
            console.error('Error loading chat list:', error);
        }
    }

    // Initial setup
    loadChatList();

    // Expose functions to window for HTML access
    window.closeTerminal = closeTerminal;
    window.playTerminal = playTerminal;
    window.pauseTerminal = pauseTerminal;
    window.stopTerminal = stopTerminal;
    window.restartTerminal = restartTerminal;
    // Initial setup
    loadChatList();

    // Expose functions to window for HTML access
    window.closeTerminal = closeTerminal;
    window.playTerminal = playTerminal;
    window.pauseTerminal = pauseTerminal;
    window.stopTerminal = stopTerminal;
    window.restartTerminal = restartTerminal;
    window.loadChat = loadChat;
    window.showTerminal = showTerminal;
});