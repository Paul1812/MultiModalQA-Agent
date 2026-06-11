// ── State Management ────────────────────────────────────────────────────────
const state = {
    files: [],
    queriesCount: 0,
    imagesCount: 0,
    docsCount: 0,
    isProcessing: false
};

// ── DOM Elements ────────────────────────────────────────────────────────────
const elements = {
    apiUrl: document.getElementById('apiUrl'),
    apiKey: document.getElementById('apiKey'),
    togglePasswordBtn: document.getElementById('togglePasswordBtn'),
    useLocalModel: document.getElementById('useLocalModel'),
    useOcr: document.getElementById('useOcr'),
    useRag: document.getElementById('useRag'),
    visionModel: document.getElementById('visionModel'),
    
    statQueries: document.getElementById('statQueries'),
    statImages: document.getElementById('statImages'),
    statDocs: document.getElementById('statDocs'),
    clearHistoryBtn: document.getElementById('clearHistoryBtn'),
    
    chatContainer: document.getElementById('chatContainer'),
    welcomeBox: document.getElementById('welcomeBox'),
    questionInput: document.getElementById('questionInput'),
    runPipelineBtn: document.getElementById('runPipelineBtn'),
    
    dragDropZone: document.getElementById('dragDropZone'),
    fileInput: document.getElementById('fileInput'),
    uploadedFilesList: document.getElementById('uploadedFilesList'),
    
    connectionStatus: document.getElementById('connectionStatus'),
    
    // Pipeline steps
    stepMcp: document.getElementById('step_mcp'),
    stepClassify: document.getElementById('step_classify'),
    stepImage: document.getElementById('step_image'),
    stepRetrieval: document.getElementById('step_retrieval'),
    stepFusion: document.getElementById('step_fusion'),
    stepAnswer: document.getElementById('step_answer')
};

// ── Load & Save Config ──────────────────────────────────────────────────────
function loadConfig() {
    const savedApiUrl = localStorage.getItem('mqa_api_url');
    const savedApiKey = localStorage.getItem('mqa_api_key');
    if (savedApiUrl) elements.apiUrl.value = savedApiUrl;
    if (savedApiKey) elements.apiKey.value = savedApiKey;
}

function saveConfig() {
    localStorage.setItem('mqa_api_url', elements.apiUrl.value.trim());
    localStorage.setItem('mqa_api_key', elements.apiKey.value.trim());
}

// ── Event Listeners & Init ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    loadConfig();
    checkConnection();
    
    // Save configuration updates
    elements.apiUrl.addEventListener('input', saveConfig);
    elements.apiKey.addEventListener('input', saveConfig);
    
    // Toggle Password Visibility
    elements.togglePasswordBtn.addEventListener('click', () => {
        const type = elements.apiKey.getAttribute('type') === 'password' ? 'text' : 'password';
        elements.apiKey.setAttribute('type', type);
        elements.togglePasswordBtn.querySelector('i').classList.toggle('fa-eye');
        elements.togglePasswordBtn.querySelector('i').classList.toggle('fa-eye-slash');
    });

    // File Upload handling
    elements.dragDropZone.addEventListener('click', () => elements.fileInput.click());
    elements.fileInput.addEventListener('change', handleFileSelect);
    
    elements.dragDropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.dragDropZone.classList.add('dragover');
    });
    
    elements.dragDropZone.addEventListener('dragleave', () => {
        elements.dragDropZone.classList.remove('dragover');
    });
    
    elements.dragDropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.dragDropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            addFiles(e.dataTransfer.files);
        }
    });

    // Run Pipeline
    elements.runPipelineBtn.addEventListener('click', runPipeline);
    
    // Clear History
    elements.clearHistoryBtn.addEventListener('click', () => {
        if (confirm("Are you sure you want to clear chat history?")) {
            // Remove everything except welcome message
            const welcome = elements.welcomeBox.cloneNode(true);
            elements.chatContainer.innerHTML = '';
            elements.chatContainer.appendChild(welcome);
            elements.welcomeBox = welcome;
            state.queriesCount = 0;
            updateStats();
        }
    });
    
    // Auto ping API every 10 seconds
    setInterval(checkConnection, 10000);
});

// ── Connection Checker ──────────────────────────────────────────────────────
async function checkConnection() {
    const url = elements.apiUrl.value.trim() || 'http://localhost:8000';
    const cleanUrl = url.replace(/\/+$/, ""); // remove trailing slashes
    
    const dot = elements.connectionStatus.querySelector('.status-dot');
    const txt = elements.connectionStatus.querySelector('.status-text');
    
    dot.className = 'status-dot connecting';
    txt.textContent = 'Connecting...';
    
    try {
        const res = await fetch(`${cleanUrl}/`, { method: 'GET', mode: 'cors' });
        if (res.ok) {
            dot.className = 'status-dot online';
            txt.textContent = 'Server online';
        } else {
            throw new Error();
        }
    } catch (e) {
        dot.className = 'status-dot offline';
        txt.textContent = 'Server offline';
    }
}

// ── File Management ─────────────────────────────────────────────────────────
function handleFileSelect(e) {
    if (e.target.files.length > 0) {
        addFiles(e.target.files);
    }
}

function addFiles(fileList) {
    for (let i = 0; i < fileList.length; i++) {
        const file = fileList[i];
        // Prevent duplicates
        if (!state.files.some(f => f.name === file.name && f.size === file.size)) {
            state.files.push(file);
        }
    }
    renderFiles();
}

function removeFile(index) {
    state.files.splice(index, 1);
    renderFiles();
}

function renderFiles() {
    elements.uploadedFilesList.innerHTML = '';
    
    let images = 0;
    let docs = 0;
    
    state.files.forEach((file, index) => {
        const ext = file.name.split('.').pop().toLowerCase();
        let iconClass = 'fa-file-lines';
        
        if (['png', 'jpg', 'jpeg', 'webp'].includes(ext)) {
            iconClass = 'fa-file-image';
            images++;
        } else {
            docs++;
        }
        
        const item = document.createElement('div');
        item.className = 'file-item';
        item.innerHTML = `
            <div class="file-item-info">
                <i class="fa-solid ${iconClass}"></i>
                <span>${file.name}</span>
            </div>
            <button class="file-item-delete" onclick="removeFile(${index})">
                <i class="fa-solid fa-xmark"></i>
            </button>
        `;
        elements.uploadedFilesList.appendChild(item);
    });
    
    state.imagesCount = images;
    state.docsCount = docs;
    updateStats();
}

function updateStats() {
    elements.statQueries.textContent = state.queriesCount;
    elements.statImages.textContent = state.imagesCount;
    elements.statDocs.textContent = state.docsCount;
}

// ── Pipeline Tracker Logic ──────────────────────────────────────────────────
function resetPipelineTracker() {
    const steps = [elements.stepMcp, elements.stepClassify, elements.stepImage, elements.stepRetrieval, elements.stepFusion, elements.stepAnswer];
    steps.forEach(step => {
        step.className = 'pipeline-step';
        step.querySelector('.step-status').innerHTML = '<i class="fa-regular fa-circle"></i>';
    });
}

function updateStepState(stepElement, status) {
    // status can be: 'idle', 'active', 'done'
    if (status === 'active') {
        stepElement.className = 'pipeline-step active';
        stepElement.querySelector('.step-status').innerHTML = '<i class="fa-solid fa-spinner"></i>';
    } else if (status === 'done') {
        stepElement.className = 'pipeline-step done';
        stepElement.querySelector('.step-status').innerHTML = '<i class="fa-solid fa-circle-check"></i>';
    } else {
        stepElement.className = 'pipeline-step';
        stepElement.querySelector('.step-status').innerHTML = '<i class="fa-regular fa-circle"></i>';
    }
}

// ── Run Pipeline ────────────────────────────────────────────────────────────
async function runPipeline() {
    if (state.isProcessing) return;
    
    const question = elements.questionInput.value.trim();
    if (!question) {
        alert("Please enter a question.");
        return;
    }
    
    const useLocal = elements.useLocalModel.checked;
    const apiKey = elements.apiKey.value.trim();
    
    if (!useLocal && !apiKey) {
        alert("Please enter an OpenAI API key in the sidebar, or check 'Use Local Model'.");
        return;
    }
    
    state.isProcessing = true;
    elements.runPipelineBtn.disabled = true;
    elements.runPipelineBtn.querySelector('span').textContent = 'Processing...';
    
    // Hide welcome box on first query
    if (elements.welcomeBox) {
        elements.welcomeBox.remove();
        elements.welcomeBox = null;
    }
    
    // 1. Append User Bubble to Chat
    appendChatBubble('YOU', question, true);
    elements.questionInput.value = '';
    
    // 2. Prepare Pipeline animation sequences
    resetPipelineTracker();
    
    let activeInterval = null;
    let stepCount = 0;
    
    // Interactive pipeline visual animation
    updateStepState(elements.stepMcp, 'active');
    
    activeInterval = setInterval(() => {
        stepCount++;
        if (stepCount === 1) {
            updateStepState(elements.stepMcp, 'done');
            updateStepState(elements.stepClassify, 'active');
        } else if (stepCount === 2) {
            updateStepState(elements.stepClassify, 'done');
            if (state.imagesCount > 0) {
                updateStepState(elements.stepImage, 'active');
            } else {
                updateStepState(elements.stepImage, 'done');
                updateStepState(elements.stepRetrieval, 'active');
                stepCount++; // skip next slot
            }
        } else if (stepCount === 3) {
            updateStepState(elements.stepImage, 'done');
            updateStepState(elements.stepRetrieval, 'active');
        } else if (stepCount === 4) {
            updateStepState(elements.stepRetrieval, 'done');
            updateStepState(elements.stepFusion, 'active');
        } else if (stepCount === 5) {
            updateStepState(elements.stepFusion, 'done');
            updateStepState(elements.stepAnswer, 'active');
            clearInterval(activeInterval);
        }
    }, 450);

    // 3. Prepare FormData
    const formData = new FormData();
    formData.append('question', question);
    formData.append('use_local_model', useLocal ? 'true' : 'false');
    formData.append('api_key', apiKey);
    formData.append('use_ocr', elements.useOcr.checked ? 'true' : 'false');
    formData.append('use_rag', elements.useRag.checked ? 'true' : 'false');
    formData.append('model', elements.visionModel.value);
    
    state.files.forEach(file => {
        formData.append('files', file);
    });

    const url = (elements.apiUrl.value.trim() || 'http://localhost:8000').replace(/\/+$/, "");
    
    try {
        const response = await fetch(`${url}/query`, {
            method: 'POST',
            body: formData,
            mode: 'cors'
        });
        
        if (!response.ok) {
            const errDetails = await response.json();
            throw new Error(errDetails.detail || "Server error occurred");
        }
        
        const data = await response.json();
        
        // Finalize pipeline animation
        clearInterval(activeInterval);
        const steps = [elements.stepMcp, elements.stepClassify, elements.stepImage, elements.stepRetrieval, elements.stepFusion, elements.stepAnswer];
        steps.forEach(step => updateStepState(step, 'done'));
        
        // Append Agent bubble to Chat
        appendChatBubble('AGENT', data.answer, false, data.ocr_text, data.sources);
        state.queriesCount++;
        updateStats();
        
    } catch (e) {
        clearInterval(activeInterval);
        resetPipelineTracker();
        
        // Append error bubble
        appendChatBubble('SYSTEM ERROR', `❌ Failed to execute agent pipeline. Details: ${e.message}`, false);
    } finally {
        state.isProcessing = false;
        elements.runPipelineBtn.disabled = false;
        elements.runPipelineBtn.querySelector('span').textContent = '▶ Run Agent Pipeline';
        checkConnection();
    }
}

// ── Chat Helpers ────────────────────────────────────────────────────────────
function appendChatBubble(sender, text, isUser, ocrText = '', sources = '') {
    const bubbleWrapper = document.createElement('div');
    bubbleWrapper.className = isUser ? 'chat-user-wrapper' : 'chat-agent-wrapper';
    
    const label = document.createElement('div');
    label.className = 'chat-label';
    label.textContent = sender;
    bubbleWrapper.appendChild(label);
    
    const bubble = document.createElement('div');
    bubble.className = isUser ? 'chat-user' : 'chat-agent';
    
    // Simple markdown mapping for the agent response
    if (!isUser) {
        let formattedText = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            // Headings
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Bullet points
            .replace(/^\s*[-*+]\s+(.*$)/gim, '<li>$1</li>')
            // Wrap list items
            .replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>')
            // clean up consecutive list wraps
            .replace(/<\/ul>\s*<ul>/g, '')
            // Paragraph breaks
            .replace(/\n\n/g, '<br><br>');
            
        bubble.innerHTML = formattedText;
        
        // Add OCR box if present
        if (ocrText && ocrText.trim()) {
            const ocrBox = document.createElement('div');
            ocrBox.className = 'expander-box';
            
            const ocrHeader = document.createElement('div');
            ocrHeader.className = 'expander-header';
            ocrHeader.innerHTML = `<span><i class="fa-solid fa-magnifying-glass"></i> OCR Extracted Text</span><i class="fa-solid fa-chevron-down"></i>`;
            
            const ocrContent = document.createElement('div');
            ocrContent.className = 'expander-content';
            ocrContent.textContent = ocrText;
            
            ocrHeader.addEventListener('click', () => {
                ocrContent.classList.toggle('active');
                ocrHeader.querySelector('.fa-chevron-down').classList.toggle('fa-chevron-up');
            });
            
            ocrBox.appendChild(ocrHeader);
            ocrBox.appendChild(ocrContent);
            bubble.appendChild(ocrBox);
        }
        
        // Add Sources box if present
        if (sources && sources.trim()) {
            const sourcesBox = document.createElement('div');
            sourcesBox.className = 'sources-box';
            sourcesBox.innerHTML = `<h5><i class="fa-solid fa-book-open"></i> Retrieved Sources</h5><p>${sources.replace(/\n/g, '<br>')}</p>`;
            bubble.appendChild(sourcesBox);
        }
        
    } else {
        bubble.textContent = text;
    }
    
    bubbleWrapper.appendChild(bubble);
    elements.chatContainer.appendChild(bubbleWrapper);
    
    // Auto-scroll chat
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
}
