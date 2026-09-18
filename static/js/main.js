// EcoSort AI - Interactive Client Logic
document.addEventListener('DOMContentLoaded', () => {
    // 1. Navigation Tabs
    const tabs = document.querySelectorAll('.nav-tab');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            const target = tab.getAttribute('data-tab');
            const content = document.getElementById(`tab-${target}`);
            if (content) content.classList.add('active');
        });
    });

    // 2. Load Samples & Wire Classification
    loadSamples();
    wireUploadForm();
    wireRAGChat();
    wireSimulator();
    refreshImpactSummary();
});

// Load Preloaded Samples
async function loadSamples() {
    try {
        const res = await fetch('/api/samples');
        const data = await res.json();
        const container = document.getElementById('samplesList');
        if (!container) return;

        container.innerHTML = '';
        data.samples.forEach((sample, idx) => {
            const btn = document.createElement('button');
            btn.className = `sample-btn ${idx === 0 ? 'selected' : ''}`;
            btn.setAttribute('data-id', sample.id);
            btn.innerHTML = `
                <img src="${sample.image}" alt="${sample.name}" class="sample-thumb">
                <span class="sample-title">${sample.name}</span>
            `;
            btn.addEventListener('click', () => {
                document.querySelectorAll('.sample-btn').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                classifySample(sample.id);
            });
            container.appendChild(btn);
        });

        // Trigger initial classification for first item
        if (data.samples.length > 0) {
            classifySample(data.samples[0].id);
        }
    } catch (err) {
        console.error('Error loading samples:', err);
    }
}

// Classify Preloaded Sample
async function classifySample(sampleId) {
    try {
        const res = await fetch('/api/classify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sample_id: sampleId })
        });
        const data = await res.json();
        renderClassificationResults(data);
    } catch (err) {
        console.error('Error classifying sample:', err);
    }
}

// Wire File Upload & Dropzone
function wireUploadForm() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('imageFileInput');
    const form = document.getElementById('uploadForm');

    if (!dropZone || !fileInput || !form) return;

    dropZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            dropZone.querySelector('p').innerHTML = `<strong>Selected:</strong> ${fileInput.files[0].name}`;
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const hint = document.getElementById('userHintInput').value;

        if (fileInput.files.length === 0) {
            alert('Please select an image file first.');
            return;
        }

        const formData = new FormData();
        formData.append('image', fileInput.files[0]);
        formData.append('hint', hint);

        const analyzeBtn = document.getElementById('analyzeBtn');
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Inspecting...';

        try {
            const res = await fetch('/api/classify', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            renderClassificationResults(data);
            document.querySelectorAll('.sample-btn').forEach(b => b.classList.remove('selected'));
        } catch (err) {
            console.error('Upload classification error:', err);
            alert('Failed to analyze image. Please try again.');
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Analyze Waste';
        }
    });
}

// Render Results on Scanner Tab
function renderClassificationResults(data) {
    const c = data.classification;
    const impact = data.impact;

    // Image preview
    document.getElementById('activePreviewImg').src = data.image_url;
    document.getElementById('activeItemNameBadge').textContent = c.item_name;

    // Confidence
    const confPct = Math.round(c.confidence * 100);
    document.getElementById('confidenceBadge').textContent = `${confPct}% Confidence`;

    // Bin Hero Card
    const binHero = document.getElementById('binHeroCard');
    binHero.style.setProperty('--bin-accent', c.bin.color);
    document.getElementById('binHeroName').textContent = c.bin.name;
    document.getElementById('primaryCategoryText').textContent = c.primary_category;

    const heroIcon = document.getElementById('binHeroIcon');
    heroIcon.className = `fa-solid fa-${c.bin.icon || 'recycle'}`;

    // Contamination Alert Banner
    const alertBox = document.getElementById('contaminationAlert');
    const reasonText = document.getElementById('contaminationReason');
    if (c.is_contaminated) {
        alertBox.classList.remove('hidden');
        reasonText.textContent = c.contamination_details;
    } else {
        alertBox.classList.add('hidden');
    }

    // Material & Weight
    document.getElementById('materialText').textContent = c.material;
    document.getElementById('weightText').textContent = `${c.weight_grams} grams`;

    // Protocol Instructions
    const instrList = document.getElementById('instructionsList');
    instrList.innerHTML = '';
    c.instructions.forEach(step => {
        const li = document.createElement('li');
        li.textContent = step;
        instrList.appendChild(li);
    });

    // Circular Potential
    document.getElementById('circularText').textContent = c.circular_potential;

    // Impact Pills
    document.getElementById('itemCo2Val').textContent = `${impact.co2_saved_kg} kg`;
    document.getElementById('itemWaterVal').textContent = `${impact.water_saved_liters} L`;
    document.getElementById('itemEnergyVal').textContent = `${impact.energy_saved_kwh} kWh`;

    // XAI Attribution
    document.getElementById('xaiText').textContent = c.explainability;

    // Refresh live session counters
    refreshImpactSummary();
}

// Wire IBM Granite RAG Chat
function wireRAGChat() {
    const chatForm = document.getElementById('ragChatForm');
    const chatInput = document.getElementById('ragQueryInput');
    const chatFeed = document.getElementById('chatFeed');
    const toggleBtn = document.getElementById('togglePromptViewBtn');
    const promptDrawer = document.getElementById('granitePromptDrawer');
    const closeDrawerBtn = document.getElementById('closeDrawerBtn');
    const promptPreview = document.getElementById('promptTemplatePreview');

    if (toggleBtn && promptDrawer) {
        toggleBtn.addEventListener('click', () => promptDrawer.classList.toggle('hidden'));
    }
    if (closeDrawerBtn && promptDrawer) {
        closeDrawerBtn.addEventListener('click', () => promptDrawer.classList.add('hidden'));
    }

    // Quick prompts
    document.querySelectorAll('.prompt-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const query = chip.getAttribute('data-q');
            chatInput.value = query;
            sendRAGQuery(query);
        });
    });

    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const query = chatInput.value.trim();
            if (query) {
                sendRAGQuery(query);
                chatInput.value = '';
            }
        });
    }

    async function sendRAGQuery(query) {
        // Append user message
        appendUserMessage(query);

        // Typing indicator
        const typingId = appendTypingIndicator();

        try {
            const res = await fetch('/api/rag_chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });
            const data = await res.json();
            removeMessage(typingId);
            appendAssistantMessage(data);

            if (promptPreview && data.prompt_template_preview) {
                promptPreview.textContent = data.prompt_template_preview;
            }
        } catch (err) {
            removeMessage(typingId);
            console.error('RAG Error:', err);
            appendErrorMessage('Failed to connect to IBM Granite RAG Engine. Please try again.');
        }
    }

    function appendUserMessage(text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'chat-msg user-msg';
        msgDiv.innerHTML = `
            <div class="msg-avatar"><i class="fa-solid fa-user"></i></div>
            <div class="msg-bubble"><p>${escapeHtml(text)}</p></div>
        `;
        chatFeed.appendChild(msgDiv);
        chatFeed.scrollTop = chatFeed.scrollHeight;
    }

    function appendAssistantMessage(data) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'chat-msg assistant-msg';

        let citationsHtml = '';
        if (data.citations && data.citations.length > 0) {
            citationsHtml = '<div class="rag-citation-chips">' +
                data.citations.map(c => `<span class="citation-chip"><i class="fa-solid fa-book-bookmark"></i> ${c.title}</span>`).join('') +
                '</div>';
        }

        let followupsHtml = '';
        if (data.suggested_followups && data.suggested_followups.length > 0) {
            followupsHtml = '<div class="quick-prompts" style="margin-top:12px;"><span class="prompt-title">Suggested Next Questions:</span>' +
                data.suggested_followups.map(q => `<button class="prompt-chip" data-q="${escapeHtml(q)}">${escapeHtml(q)}</button>`).join('') +
                '</div>';
        }

        // Simple markdown bold/newline formatter
        let formatted = data.response
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');

        msgDiv.innerHTML = `
            <div class="msg-avatar"><i class="fa-solid fa-recycle"></i></div>
            <div class="msg-bubble">
                <div class="msg-meta">${data.model}</div>
                <div>${formatted}</div>
                ${citationsHtml}
                ${followupsHtml}
            </div>
        `;
        chatFeed.appendChild(msgDiv);

        // Bind new followup chips
        msgDiv.querySelectorAll('.prompt-chip').forEach(btn => {
            btn.addEventListener('click', () => {
                const q = btn.getAttribute('data-q');
                sendRAGQuery(q);
            });
        });

        chatFeed.scrollTop = chatFeed.scrollHeight;
    }

    function appendTypingIndicator() {
        const id = 'typing_' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.className = 'chat-msg assistant-msg';
        msgDiv.id = id;
        msgDiv.innerHTML = `
            <div class="msg-avatar"><i class="fa-solid fa-recycle"></i></div>
            <div class="msg-bubble"><i class="fa-solid fa-ellipsis fa-fade"></i> IBM Granite RAG retrieving statutory guidelines...</div>
        `;
        chatFeed.appendChild(msgDiv);
        chatFeed.scrollTop = chatFeed.scrollHeight;
        return id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function appendErrorMessage(text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'chat-msg assistant-msg';
        msgDiv.innerHTML = `
            <div class="msg-avatar" style="background-color:#DC2626;"><i class="fa-solid fa-triangle-exclamation"></i></div>
            <div class="msg-bubble" style="border-color:#DC2626;"><p>${text}</p></div>
        `;
        chatFeed.appendChild(msgDiv);
        chatFeed.scrollTop = chatFeed.scrollHeight;
    }
}

// Wire Campus Impact Simulator
function wireSimulator() {
    const slider = document.getElementById('popSlider');
    const popValText = document.getElementById('sliderPopValue');

    if (!slider || !popValText) return;

    slider.addEventListener('input', () => {
        const pop = parseInt(slider.value, 10);
        popValText.textContent = `${pop.toLocaleString()} People`;

        // Mathematical scaling logic:
        // ~0.25 kg solid waste generated per person per day on institutional campuses
        // Annual generation = pop * 0.25 * 300 active campus days = pop * 75 kg = pop * 0.075 metric tons
        // 86.4% landfill diversion with EcoSort AI
        const annualWasteTons = (pop * 75 * 0.864) / 1000.0;
        const annualCo2Tons = annualWasteTons * 1.5;
        const annualSavingsInr = (annualWasteTons * 9350); // Net scrap revenue & hauling savings
        const workersProtected = Math.max(1, Math.round(pop / 400));

        document.getElementById('simWasteDiverted').textContent = `${annualWasteTons.toFixed(1)} Tons`;
        document.getElementById('simCo2Saved').textContent = `${annualCo2Tons.toFixed(1)} Tons`;
        document.getElementById('simSavingsInr').textContent = `₹${(annualSavingsInr / 100000).toFixed(2)} Lakh`;
        document.getElementById('simWorkersProtected').textContent = `${workersProtected} Workers`;
    });
}

// Refresh Live Session Statistics
async function refreshImpactSummary() {
    try {
        const res = await fetch('/api/impact_summary');
        const data = await res.json();
        const s = data.session;

        const countEl = document.getElementById('sessionItemsCount');
        const co2El = document.getElementById('sessionCo2Val');
        const waterEl = document.getElementById('sessionWaterVal');
        const energyEl = document.getElementById('sessionEnergyVal');

        if (countEl) countEl.textContent = s.items_sorted;
        if (co2El) co2El.textContent = s.co2_averted_kg.toFixed(3);
        if (waterEl) waterEl.textContent = s.water_saved_liters.toFixed(2);
        if (energyEl) energyEl.textContent = s.energy_saved_kwh.toFixed(2);
    } catch (err) {
        console.error('Error fetching impact summary:', err);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}