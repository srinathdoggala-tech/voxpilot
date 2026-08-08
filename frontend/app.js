document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const startSessionBtn = document.getElementById('startSessionBtn');
    const bargeInBtn = document.getElementById('bargeInBtn');
    const endSessionBtn = document.getElementById('endSessionBtn');
    const textTurnInput = document.getElementById('textTurnInput');
    const sendTextBtn = document.getElementById('sendTextBtn');
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.getElementById('statusText');
    const visualizerState = document.getElementById('visualizerState');
    const transcriptStream = document.getElementById('transcriptStream');
    const messageCount = document.getElementById('messageCount');
    const sessionTimer = document.getElementById('sessionTimer');
    const toggleDevMode = document.getElementById('toggleDevMode');
    const devPanel = document.getElementById('devPanel');
    const runEvalsBtn = document.getElementById('runEvalsBtn');
    const evalResultsBox = document.getElementById('evalResultsBox');

    // Metrics Elements
    const sttLatencyVal = document.getElementById('sttLatencyVal');
    const ttftVal = document.getElementById('ttftVal');
    const ttfaVal = document.getElementById('ttfaVal');
    const e2eVal = document.getElementById('e2eVal');

    // State Variables
    let ws = null;
    let isConnected = false;
    let turnCount = 0;
    let timerInterval = null;
    let sessionSeconds = 0;

    // Canvas Audio Visualizer setup
    const canvas = document.getElementById('waveCanvas');
    const ctx = canvas.getContext('2d');
    let animFrameId = null;

    function drawWaveform() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#6366F1';
        ctx.beginPath();

        const sliceWidth = canvas.width * 1.0 / 50;
        let x = 0;
        const time = Date.now() * 0.005;

        for (let i = 0; i < 50; i++) {
            const v = isConnected ? Math.sin(i * 0.2 + time) * 30 + Math.random() * 5 : 2;
            const y = canvas.height / 2 + v;

            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
            x += sliceWidth;
        }

        ctx.stroke();
        animFrameId = requestAnimationFrame(drawWaveform);
    }
    drawWaveform();

    // Toggle Developer Mode
    toggleDevMode.addEventListener('click', () => {
        devPanel.classList.toggle('hidden');
    });

    // Start Voice Session
    startSessionBtn.addEventListener('click', () => {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host || 'localhost:8000';
        const wsUrl = `${protocol}//${host}/api/v1/voice/ws`;

        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            isConnected = true;
            statusDot.classList.add('active');
            statusText.textContent = 'Active (Connected)';
            visualizerState.textContent = 'Voice Pipeline active — Microphone streaming...';
            
            startSessionBtn.disabled = true;
            bargeInBtn.disabled = false;
            endSessionBtn.disabled = false;
            textTurnInput.disabled = false;
            sendTextBtn.disabled = false;

            // Start Session Timer
            sessionSeconds = 0;
            timerInterval = setInterval(() => {
                sessionSeconds++;
                const mins = String(Math.floor(sessionSeconds / 60)).padStart(2, '0');
                const secs = String(sessionSeconds % 60).padStart(2, '0');
                sessionTimer.textContent = `${mins}:${secs}`;
            }, 1000);
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'turn_complete') {
                renderTurnMessage(data);
                updateMetrics(data.metrics);
            } else if (data.type === 'interruption_ack') {
                renderSystemNotice('Barge-in actuation triggered — output audio cancelled.');
            }
        };

        ws.onclose = () => {
            cleanupSession();
        };

        ws.onerror = (err) => {
            console.error('WebSocket error:', err);
            cleanupSession();
        };
    });

    // Send Text Turn
    function sendTurn() {
        const text = textTurnInput.value.trim();
        if (!text || !ws || ws.readyState !== WebSocket.OPEN) return;

        ws.send(JSON.stringify({
            type: 'text_turn',
            text: text
        }));

        textTurnInput.value = '';
    }

    sendTextBtn.addEventListener('click', sendTurn);
    textTurnInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') sendTurn();
    });

    // Barge-In Interruption
    bargeInBtn.addEventListener('click', () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'interruption' }));
        }
    });

    // End Session
    endSessionBtn.addEventListener('click', () => {
        if (ws) ws.close();
        cleanupSession();
    });

    function cleanupSession() {
        isConnected = false;
        statusDot.classList.remove('active');
        statusText.textContent = 'Disconnected';
        visualizerState.textContent = 'Press "Start Session" to connect microphone audio';

        startSessionBtn.disabled = false;
        bargeInBtn.disabled = true;
        endSessionBtn.disabled = true;
        textTurnInput.disabled = true;
        sendTextBtn.disabled = true;

        if (timerInterval) clearInterval(timerInterval);
        sessionTimer.textContent = '00:00';
    }

    function renderTurnMessage(data) {
        // Clear empty state if present
        const emptyState = transcriptStream.querySelector('.empty-state');
        if (emptyState) emptyState.remove();

        // User turn bubble
        const userBubble = document.createElement('div');
        userBubble.className = 'message-bubble message-user';
        userBubble.textContent = data.user_transcript;
        transcriptStream.appendChild(userBubble);

        // Assistant turn bubble
        const assistantBubble = document.createElement('div');
        assistantBubble.className = 'message-bubble message-assistant';
        assistantBubble.innerHTML = `<span class="agent-tag">[${data.agent_name}${data.rag_used ? ' + RAG' : ''}]</span>${data.assistant_text}`;
        transcriptStream.appendChild(assistantBubble);

        transcriptStream.scrollTop = transcriptStream.scrollHeight;
        turnCount += 2;
        messageCount.textContent = `${turnCount} messages`;
    }

    function renderSystemNotice(msg) {
        const notice = document.createElement('div');
        notice.style.textAlign = 'center';
        notice.style.fontSize = '0.75rem';
        notice.style.color = '#F59E0B';
        notice.style.margin = '4px 0';
        notice.textContent = msg;
        transcriptStream.appendChild(notice);
        transcriptStream.scrollTop = transcriptStream.scrollHeight;
    }

    function updateMetrics(metrics) {
        if (!metrics) return;
        sttLatencyVal.textContent = `${metrics.stt_latency_ms.toFixed(1)} ms`;
        ttftVal.textContent = `${metrics.llm_ttft_ms.toFixed(1)} ms`;
        ttfaVal.textContent = `${metrics.tts_ttfa_ms.toFixed(1)} ms`;
        e2eVal.textContent = `${metrics.e2e_total_latency_ms.toFixed(1)} ms`;
    }

    // Trigger AI Evaluation Benchmark Suite
    runEvalsBtn.addEventListener('click', async () => {
        evalResultsBox.textContent = 'Executing AI benchmark evaluation scenarios...';
        try {
            const res = await fetch('/api/v1/evals/run', { method: 'POST' });
            const data = await res.json();
            evalResultsBox.textContent = `Overall Pass Rate: ${data.overall_pass_rate}%\nPassed: ${data.passed_scenarios}/${data.total_scenarios}\nAvg Latency: ${data.avg_latency_ms.toFixed(1)} ms`;
        } catch (err) {
            evalResultsBox.textContent = `Evaluation execution failed: ${err.message}`;
        }
    });
});
