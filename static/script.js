const chatHistory = document.getElementById('chat-history');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const reasoningLog = document.getElementById('reasoning-log');

let currentAnswerDiv = null;
let currentSessionId = null;
let currentEventSource = null;

function detectFiles(text) {
    // Detect file patterns in text: .csv, .json, .txt, .xlsx, .pdf, etc.
    const filePattern = /\b([\w-]+\.(csv|json|txt|xlsx|xls|pdf|docx|doc|xml|html))\b/gi;
    const matches = text.match(filePattern);
    return matches ? [...new Set(matches)] : [];
}

function addMessage(text, isUser) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    // Check for files in bot messages
    if (!isUser) {
        const files = detectFiles(text);
        if (files.length > 0) {
            // Create message with text and download buttons
            const textDiv = document.createElement('div');
            textDiv.textContent = text;
            msgDiv.appendChild(textDiv);
            
            // Add download buttons
            const fileDiv = document.createElement('div');
            fileDiv.style.cssText = 'margin-top: 10px; display: flex; flex-wrap: wrap; gap: 8px;';
            
            files.forEach(filename => {
                const downloadBtn = document.createElement('button');
                downloadBtn.className = 'download-btn';
                downloadBtn.innerHTML = `📥 Tải ${filename}`;
                downloadBtn.onclick = () => downloadFile(filename);
                fileDiv.appendChild(downloadBtn);
            });
            
            msgDiv.appendChild(fileDiv);
        } else {
            msgDiv.textContent = text;
        }
    } else {
        msgDiv.textContent = text;
    }
    
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    return msgDiv;
}

function downloadFile(filename) {
    const link = document.createElement('a');
    link.href = `/download/${filename}`;
    link.download = filename;
    link.click();
}

function startStreamingAnswer() {
    currentAnswerDiv = document.createElement('div');
    currentAnswerDiv.className = 'message bot-message';
    currentAnswerDiv.textContent = '';
    chatHistory.appendChild(currentAnswerDiv);
    return currentAnswerDiv;
}

function appendToAnswer(text) {
    if (currentAnswerDiv) {
        currentAnswerDiv.textContent += text;
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
}

async function showQuestionDialog(question) {
    return new Promise((resolve) => {
        // Add question to chat as bot message
        const questionDiv = document.createElement('div');
        questionDiv.className = 'message bot-message';
        questionDiv.innerHTML = `<strong>❓ Câu hỏi:</strong><br>${question}`;
        chatHistory.appendChild(questionDiv);
        
        // Create answer input area
        const answerArea = document.createElement('div');
        answerArea.style.cssText = 'display: flex; padding: 1rem; border-top: 1px solid #ddd; background: #f0f8ff;';
        answerArea.innerHTML = `
            <input type="text" id="temp-answer-input" style="flex: 1; padding: 0.5rem; border: 1px solid #3498db; border-radius: 4px;" placeholder="Nhập câu trả lời của bạn...">
            <button id="temp-submit-btn" style="margin-left: 0.5rem; padding: 0.5rem 1rem; background-color: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">Trả lời</button>
        `;
        
        // Replace current input area with answer area
        const inputArea = document.querySelector('.input-area');
        const parent = inputArea.parentElement;
        parent.insertBefore(answerArea, inputArea);
        inputArea.style.display = 'none';
        
        const answerInput = answerArea.querySelector('#temp-answer-input');
        const submitBtn = answerArea.querySelector('#temp-submit-btn');
        
        answerInput.focus();
        chatHistory.scrollTop = chatHistory.scrollHeight;
        
        const handleSubmit = () => {
            const answer = answerInput.value.trim();
            if (answer) {
                // Show user's answer in chat
                addMessage(answer, true);
                
                // Remove answer area and restore input
                parent.removeChild(answerArea);
                inputArea.style.display = 'flex';
                
                resolve(answer);
            }
        };
        
        submitBtn.addEventListener('click', handleSubmit);
        answerInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleSubmit();
        });
    });
}

async function submitAnswer(sessionId, answer) {
    try {
        const response = await fetch('/answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, answer: answer })
        });
        return await response.json();
    } catch (error) {
        console.error('Error submitting answer:', error);
        return { status: 'error', message: error.message };
    }
}

function addReasoningEntry(type, content) {
    const entry = document.createElement('div');
    entry.className = `reasoning-entry ${type}`;
    
    const timestamp = new Date().toLocaleTimeString('vi-VN');
    const typeLabel = getTypeLabel(type);
    
    entry.innerHTML = `
        <div class="timestamp">${timestamp}</div>
        <div class="type">${typeLabel}</div>
        <div class="content">${formatContent(content)}</div>
    `;
    
    reasoningLog.appendChild(entry);
    reasoningLog.scrollTop = reasoningLog.scrollHeight;
}

function getTypeLabel(type) {
    const labels = {
        'agent-name': '🤖 Agent',
        'thought': '💭 Suy nghĩ',
        'tool': '🔧 Công cụ',
        'action_input': '⚡ Hành động',
        'observation': '👀 Quan sát',
        'answer': '✅ Câu trả lời',
        'tasks': '📋 Nhiệm vụ',
        'description': '📝 Mô tả',
        'question': '❓ Câu hỏi',
        'info': 'ℹ️ Thông tin'
    };
    return labels[type] || type.toUpperCase();
}

function formatContent(content) {
    if (typeof content === 'object') {
        return JSON.stringify(content, null, 2);
    }
    return content;
}

async function sendMessage() {
    const query = userInput.value.trim();
    if (!query) return;

    addMessage(query, true);
    userInput.value = '';
    
    // Clear previous reasoning log
    reasoningLog.innerHTML = '<div style="color: #7f8c8d; text-align: center; padding: 1rem;">Đang xử lý...</div>';

    currentEventSource = new EventSource(`/stream?message=${encodeURIComponent(query)}`);

    currentEventSource.onmessage = async (event) => {
        const data = JSON.parse(event.data);
        
        // Store session ID
        if (data.session_id) {
            currentSessionId = data.session_id;
        }
        
        if (data.type === 'done') {
            currentAnswerDiv = null;
            currentEventSource.close();
            currentSessionId = null;
            return;
        }

        if (data.type === 'error') {
            addMessage(`Lỗi: ${data.content}`, false);
            addReasoningEntry('error', data.content);
            currentEventSource.close();
            return;
        }

        if (data.type === 'question') {
            // Show question dialog and wait for user answer
            const answer = await showQuestionDialog(data.content);
            addReasoningEntry('question', data.content);
            addReasoningEntry('info', `Câu trả lời: ${answer}`);
            
            // Submit answer to backend
            await submitAnswer(currentSessionId, answer);
            return;
        }

        if (data.type === 'answer_start') {
            startStreamingAnswer();
        } else if (data.type === 'answer_chunk') {
            appendToAnswer(data.content);
        } else if (data.type === 'answer_end') {
            // Check if streamed answer contains files
            if (currentAnswerDiv) {
                const answerText = currentAnswerDiv.textContent;
                const files = detectFiles(answerText);
                if (files.length > 0) {
                    const fileDiv = document.createElement('div');
                    fileDiv.style.cssText = 'margin-top: 10px; display: flex; flex-wrap: wrap; gap: 8px;';
                    
                    files.forEach(filename => {
                        const downloadBtn = document.createElement('button');
                        downloadBtn.className = 'download-btn';
                        downloadBtn.innerHTML = `📥 Tải ${filename}`;
                        downloadBtn.onclick = () => downloadFile(filename);
                        fileDiv.appendChild(downloadBtn);
                    });
                    
                    currentAnswerDiv.appendChild(fileDiv);
                }
            }
            currentAnswerDiv = null;
            
            // Final answer received, add to reasoning log
            if (reasoningLog.innerHTML.includes('Đang xử lý...')) {
                reasoningLog.innerHTML = '';
            }
            addReasoningEntry('answer', data.content);
        } else {
            // Add non-answer events to reasoning log only
            if (reasoningLog.innerHTML.includes('Đang xử lý...')) {
                reasoningLog.innerHTML = '';
            }
            addReasoningEntry(data.type, data.content);
        }
    };

    currentEventSource.onerror = () => {
        addMessage("Mất kết nối hoặc có lỗi xảy ra.", false);
        currentEventSource.close();
    };
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

