const vscode = acquireVsCodeApi();
const chatContainer = document.getElementById('chat-container');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const modelSelect = document.getElementById('model-select');
const temperatureInput = document.getElementById('temperature-input');
const maxTokensInput = document.getElementById('max-tokens-input');
const newChatButton = document.getElementById('new-chat-button');
const attachmentButton = document.getElementById('attachment-button');

let currentAttachment = null;

// Config management
function updateConfig() {
    vscode.postMessage({
        type: 'updateConfig',
        value: {
            model: modelSelect.value,
            temperature: parseFloat(temperatureInput.value),
            max_completion_tokens: parseInt(maxTokensInput.value)
        }
    });
}

// Message handling
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    // Create a container for the message content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Set the HTML content (markdown is already parsed on the server side)
    contentDiv.innerHTML = text;
    
    // Add apply buttons to code blocks
    contentDiv.querySelectorAll('pre code').forEach(codeBlock => {
        const pre = codeBlock.parentElement;
        const codeContent = codeBlock.textContent;
        
        // Try to extract filename from parent elements or code block class
        let filename = '';
        const preText = pre.previousElementSibling?.textContent || '';
        if (preText) {
            // Check for common filename patterns like ```filename.ext or File: filename.ext
            const filenameMatch = preText.match(/(?:```|File:|path:)\s*([^\s]+)/i);
            if (filenameMatch) {
                filename = filenameMatch[1];
            }
        }
        
        // Also check for language class that might indicate file type
        const langClass = Array.from(codeBlock.classList).find(cls => cls.startsWith('language-'));
        if (langClass && !filename) {
            const ext = langClass.replace('language-', '');
            filename = `newfile.${ext}`;
        }
        
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'code-block-buttons';
        
        const applyButton = document.createElement('button');
        applyButton.className = 'code-apply-button';
        
        // Set initial state
        if (filename) {
            applyButton.textContent = `Create ${filename}`;
            applyButton.dataset.filename = filename;
            
            // Check file existence
            vscode.postMessage({
                type: 'checkFileExists',
                filename: filename
            });
        } else {
            applyButton.textContent = 'Apply';
        }
        
        applyButton.onclick = () => {
            console.log('Button clicked:', {
                filename: filename,
                codeContent: codeContent,
                buttonText: applyButton.textContent
            });

            // Disable button and show loading state
            applyButton.disabled = true;
            const originalText = applyButton.textContent;
            applyButton.textContent = 'Creating...';
            
            // Add temporary message to chat
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message assistant-message';
            messageDiv.textContent = `Starting file creation for ${filename}...`;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            try {
                // Send message to create file
                vscode.postMessage({
                    type: 'applyCode',
                    code: codeContent,
                    filename: filename
                });
                console.log('Message sent to create file');
            } catch (error) {
                console.error('Error sending message:', error);
                messageDiv.textContent = `Error: ${error.message}`;
            }
            
            // Reset button after a short delay
            setTimeout(() => {
                applyButton.disabled = false;
                applyButton.textContent = originalText;
            }, 2000);
        };
        
        buttonContainer.appendChild(applyButton);
        pre.appendChild(buttonContainer);
    });
    
    // Add the content to the message
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // Add syntax highlighting to code blocks if Prism is available
    if (window.Prism) {
        Prism.highlightAllUnder(messageDiv);
    }
}

function sendMessage() {
    const message = messageInput.value.trim();
    if (message || currentAttachment) {
        vscode.postMessage({
            type: 'sendMessage',
            value: message,
            attachment: currentAttachment
        });
        messageInput.value = '';
        currentAttachment = null;
        document.getElementById('file-display').innerHTML = '';
    }
}

// File attachment handling
function displayAttachedFile(fileName, filePath) {
    const fileDisplay = document.getElementById('file-display');
    fileDisplay.innerHTML = '';
    
    if (fileName && filePath) {
        currentAttachment = filePath;
        const fileDiv = document.createElement('div');
        fileDiv.className = 'attached-file';
        fileDiv.innerHTML = `
            <span class="file-name">${fileName}</span>
            <button class="cancel-button" title="Remove attachment">×</button>
        `;
        
        fileDiv.querySelector('.cancel-button').addEventListener('click', () => {
            currentAttachment = null;
            fileDisplay.innerHTML = '';
            vscode.postMessage({
                type: 'cancelAttachment'
            });
        });
        
        fileDisplay.appendChild(fileDiv);
    }
}

// Event listeners
window.addEventListener('message', event => {
    const message = event.data;
    switch (message.type) {
        case 'addMessage':
            addMessage(message.message, message.sender);
            break;
        case 'clearMessages':
            chatContainer.innerHTML = '';
            break;
        case 'fileAttached':
            displayAttachedFile(message.fileName, message.filePath);
            break;
        case 'fileExistsResult':
            // Update button text based on file existence
            const buttons = document.querySelectorAll('.code-apply-button');
            buttons.forEach(button => {
                if (button.dataset.filename === message.filename) {
                    button.textContent = message.exists ? 
                        `Apply to ${message.filename}` : 
                        `Create ${message.filename}`;
                }
            });
            break;
    }
});

modelSelect.addEventListener('change', updateConfig);
temperatureInput.addEventListener('change', updateConfig);
maxTokensInput.addEventListener('change', updateConfig);
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

newChatButton.addEventListener('click', () => {
    vscode.postMessage({
        type: 'newChat',
        value: null
    });
    chatContainer.innerHTML = '';
});

attachmentButton.addEventListener('click', () => {
    vscode.postMessage({
        type: 'attachment',
        value: null
    });
});

// Initial config update
updateConfig(); 