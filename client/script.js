(() => {
    const userInput = document.getElementById("userInput");
    const chatBox = document.getElementById("chatBox");
    const terminalContainer = document.getElementById("terminalContainer");
    const terminalOutput = document.getElementById("terminalOutput");

    userInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            const inputText = userInput.value.trim();
            if (!inputText) return;

            appendMessage("user", inputText);
            userInput.value = "";

            setTimeout(() => {
                const botHTML = `${inputText} <button class="control-btn" onclick="openTerminal()">Exécuter</button>`;
                appendMessage("bot", botHTML, true);
                scrollChatToBottom();
            }, 500);
        }
    });

    function appendMessage(type, content, useHTML = false) {
        const message = document.createElement("div");
        message.className = `message ${type}-message`;
        if (useHTML) {
            message.innerHTML = content;
        } else {
            message.textContent = content;
        }
        chatBox.appendChild(message);
    }

    function scrollChatToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    window.openTerminal = () => {
        terminalContainer.style.display = "flex";
    };

    window.closeTerminal = () => {
        terminalContainer.style.display = "none";
    };

    window.playTerminal = () => {
        terminalOutput.innerText = "Play...";
    };

    window.pauseTerminal = () => {
        terminalOutput.innerText = "Pause...";
    };

    window.stopTerminal = () => {
        terminalOutput.innerText = "Stop...";
    };

    window.restartTerminal = () => {
        terminalOutput.innerText = "Restart...";
    };

    lucide.createIcons();
})();
