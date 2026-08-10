/**
 * VoxPilot AI — Frontend Application
 *
 * Real-time voice agent interface featuring:
 * - WebSocket session management
 * - Push-to-talk microphone capture → PCM16 → binary WebSocket frames
 * - AudioContext-based playback of PCM audio frames from the server
 * - Live transcript streaming with agent/RAG metadata
 * - Latency metrics and session event timeline
 * - Knowledge document ingestion
 */

// ─── Audio Constants ────────────────────────────────────────────────────────
const TARGET_SAMPLE_RATE = 16000;   // Send 16kHz mono PCM16 to server
const SERVER_SAMPLE_RATE = 24000;   // OpenAI TTS returns 24kHz PCM
const AUDIO_HEADER_MAGIC = 0x41554449; // "AUDI"
const AUDIO_HEADER_BYTES = 12;

// ─── DOM Elements ────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const startSessionBtn   = document.getElementById('startSessionBtn');
    const micBtn            = document.getElementById('micBtn');
    const bargeInBtn        = document.getElementById('bargeInBtn');
    const endSessionBtn     = document.getElementById('endSessionBtn');
    const textTurnInput     = document.getElementById('textTurnInput');
    const sendTextBtn       = document.getElementById('sendTextBtn');
    const ingestDocBtn      = document.getElementById('ingestDocBtn');
    const docTitle          = document.getElementById('docTitle');
    const docContent        = document.getElementById('docContent');
    const ingestStatus      = document.getElementById('ingestStatus');
    const statusDot         = document.getElementById('statusDot');
    const statusText        = document.getElementById('statusText');
    const visualizerState   = document.getElementById('visualizerState');
    const transcriptStream  = document.getElementById('transcriptStream');
    const emptyState        = document.getElementById('emptyState');
    const messageCount      = document.getElementById('messageCount');
    const sessionTimer      = document.getElementById('sessionTimer');
    const toggleDevMode     = document.getElementById('toggleDevMode');
    const devPanel          = document.getElementById('devPanel');
    const runEvalsBtn       = document.getElementById('runEvalsBtn');
    const evalResultsBox    = document.getElementById('evalResultsBox');
    const agentStateBar     = document.getElementById('agentStateBar');
    const stateLabel        = document.getElementById('stateLabel');
    const stateDot          = document.getElementById('stateDot');
    const convState         = document.getElementById('convState');
    const sessionTimeline   = document.getElementById('sessionTimeline');
    const providerBadges    = document.getElementById('providerBadges');
    const llmBadge          = document.getElementById('llmBadge');
    const sttBadge          = document.getElementById('sttBadge');
    const ttsBadge          = document.getElementById('ttsBadge');

    // Metrics elements
    const sttLatencyVal = document.getElementById('sttLatencyVal');
    const ttftVal       = document.getElementById('ttftVal');
    const ttfaVal       = document.getElementById('ttfaVal');
    const e2eVal        = document.getElementById('e2eVal');
    const turnCostVal   = document.getElementById('turnCostVal');
    const stateVal      = document.getElementById('stateVal');

    // ─── State ───────────────────────────────────────────────────────────────
    let ws               = null;
    let isConnected      = false;
    let turnCount        = 0;
    let timerInterval    = null;
    let sessionSeconds   = 0;
    let isRecording      = false;
    let isPlaying        = false;
    let isSpeaking       = false;  // AI is speaking
    let audioContext     = null;
    let mediaStream      = null;
    let audioWorkletNode = null;
    let scriptProcessor  = null;
    let micChunks        = [];
    let audioQueue       = [];     // Queued PCM buffers waiting to play
    let timelineEvents   = [];

    // ─── Canvas Waveform Visualizer ──────────────────────────────────────────
    const canvas = document.getElementById('waveCanvas');
    const ctx    = canvas.getContext('2d');
    let animFrameId = null;
    let analyserNode = null;
    let analyserData = null;

    function drawWaveform() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        if (analyserNode && analyserData && (isRecording || isPlaying)) {
            // Real audio data visualization
            analyserNode.getByteTimeDomainData(analyserData);
            ctx.lineWidth = 2;
            ctx.strokeStyle = isRecording ? '#EF4444' : '#6366F1';
            const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
            if (isRecording) {
                gradient.addColorStop(0, '#EF4444');
                gradient.addColorStop(1, '#F97316');
            } else {
                gradient.addColorStop(0, '#6366F1');
                gradient.addColorStop(1, '#A855F7');
            }
            ctx.strokeStyle = gradient;
            ctx.beginPath();
            const sliceWidth = canvas.width / analyserData.length;
            let x = 0;
            for (let i = 0; i < analyserData.length; i++) {
                const v = analyserData[i] / 128.0;
                const y = (v * canvas.height) / 2;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
                x += sliceWidth;
            }
            ctx.stroke();
        } else if (isConnected) {
            // Idle animation when connected but not recording/playing
            ctx.lineWidth = 1.5;
            const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
            gradient.addColorStop(0, '#6366F1');
            gradient.addColorStop(1, '#A855F7');
            ctx.strokeStyle = gradient;
            ctx.beginPath();
            const time = Date.now() * 0.002;
            const sliceWidth = canvas.width / 80;
            let x = 0;
            for (let i = 0; i < 80; i++) {
                const v = Math.sin(i * 0.15 + time) * 8 + Math.sin(i * 0.4 + time * 1.5) * 3;
                const y = canvas.height / 2 + v;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
                x += sliceWidth;
            }
            ctx.stroke();
        } else {
            // Flat line when disconnected
            ctx.lineWidth = 1;
            ctx.strokeStyle = 'rgba(99,102,241,0.2)';
            ctx.beginPath();
            ctx.moveTo(0, canvas.height / 2);
            ctx.lineTo(canvas.width, canvas.height / 2);
            ctx.stroke();
        }

        animFrameId = requestAnimationFrame(drawWaveform);
    }
    drawWaveform();

    const backendHostInput = document.getElementById('backendHostInput');

    const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const savedHost = localStorage.getItem('voxpilot_backend_host');
    if (backendHostInput) {
        if (savedHost) {
            backendHostInput.value = savedHost;
        } else if (!isLocal) {
            backendHostInput.value = 'voxpilot-backend.onrender.com';
        }
    }

    // ─── Dev Console Toggle ───────────────────────────────────────────────────
    toggleDevMode.addEventListener('click', () => {
        devPanel.classList.toggle('hidden');
    });

    // ─── Session Management ───────────────────────────────────────────────────
    startSessionBtn.addEventListener('click', startSession);

    function startSession() {
        let rawHost = (backendHostInput ? backendHostInput.value.trim() : '') || window.location.host || 'localhost:8000';
        
        // Strip protocol prefix if user pasted full URL
        let host = rawHost.replace(/^(https?|wss?):\/\//i, '').replace(/\/.*$/, '');
        localStorage.setItem('voxpilot_backend_host', host);
        
        const isHostLocal = host.startsWith('localhost') || host.startsWith('127.0.0.1');
        const protocol = (window.location.protocol === 'https:' && !isHostLocal) ? 'wss:' : 'ws:';
        
        const wsUrl = `${protocol}//${host}/api/v1/voice/ws`;

        ws = new WebSocket(wsUrl);
        ws.binaryType = 'arraybuffer';

        ws.onopen = () => {
            isConnected = true;
            statusDot.classList.add('active');
            statusText.textContent = 'Connected';
            visualizerState.textContent = 'Session active — hold the mic button to speak';
            agentStateBar.style.display = 'flex';

            startSessionBtn.disabled = true;
            micBtn.disabled = false;
            bargeInBtn.disabled = false;
            endSessionBtn.disabled = false;
            textTurnInput.disabled = false;
            sendTextBtn.disabled = false;
            ingestDocBtn.disabled = false;

            sessionSeconds = 0;
            timerInterval = setInterval(() => {
                sessionSeconds++;
                const mins = String(Math.floor(sessionSeconds / 60)).padStart(2, '0');
                const secs = String(sessionSeconds % 60).padStart(2, '0');
                sessionTimer.textContent = `${mins}:${secs}`;
            }, 1000);
        };

        ws.onmessage = handleServerMessage;

        ws.onclose = () => cleanupSession();

        ws.onerror = (err) => {
            console.error('WebSocket error:', err);
            cleanupSession();
        };
    }

    function handleServerMessage(event) {
        // Binary message = PCM audio frame from TTS
        if (event.data instanceof ArrayBuffer) {
            handleAudioFrame(event.data);
            return;
        }

        const data = JSON.parse(event.data);

        switch (data.type) {
            case 'session_started':
                if (data.providers) {
                    llmBadge.textContent = `LLM: ${shortName(data.providers.llm)}`;
                    sttBadge.textContent = `STT: ${shortName(data.providers.stt)}`;
                    ttsBadge.textContent = `TTS: ${shortName(data.providers.tts)}`;
                    providerBadges.style.display = 'flex';
                }
                addTimelineEvent('SESSION_START', 'green');
                break;

            case 'processing':
                setAgentState('Thinking…', 'thinking');
                visualizerState.textContent = 'Agent processing your message…';
                break;

            case 'stt_processing':
                setAgentState('Transcribing…', 'thinking');
                visualizerState.textContent = 'Transcribing audio…';
                break;

            case 'transcript':
                if (data.text) {
                    addTimelineEvent(`TRANSCRIPT: "${data.text.substring(0, 40)}…"`, 'blue');
                    if (data.is_final) {
                        renderTranscriptBubble(data.text, 'user-interim');
                    }
                }
                break;

            case 'turn_complete':
                renderTurnMessage(data);
                updateMetrics(data.metrics);
                if (data.cost) updateCost(data.cost);
                if (data.conversational_state) {
                    convState.textContent = data.conversational_state;
                    stateVal.textContent = data.conversational_state;
                }
                addTimelineEvent(`LLM_COMPLETE (${data.model_used || '?'})`, 'purple');
                setAgentState('Playing audio…', 'speaking');
                isSpeaking = true;
                break;

            case 'audio_complete':
                // All audio frames received — audio queue will drain naturally
                addTimelineEvent('TTS_COMPLETE', 'green');
                if (!isPlaying) {
                    setAgentState('Idle', 'idle');
                    isSpeaking = false;
                    visualizerState.textContent = 'Hold the mic button to speak';
                }
                break;

            case 'knowledge_ingested':
                ingestStatus.textContent = `✓ Document ingested (ID: ${data.document_id})`;
                ingestStatus.className = 'ingest-status success';
                addTimelineEvent(`RAG_INGEST: ${data.document_id}`, 'blue');
                break;

            case 'interruption_ack':
                stopAudioPlayback();
                renderSystemNotice('⚡ Barge-in — AI speech interrupted');
                setAgentState('Idle', 'idle');
                isSpeaking = false;
                addTimelineEvent('USER_INTERRUPT', 'orange');
                break;

            case 'error':
                renderSystemNotice(`⚠ Error: ${data.message}`);
                setAgentState('Error', 'error');
                break;
        }
    }

    function shortName(fullName) {
        if (!fullName) return '?';
        return fullName.replace('Provider', '').replace('LLM', '').replace('TTS', '').replace('STT', '').replace('Mock', 'Mock').trim();
    }

    // ─── Audio Playback (PCM16 from server) ───────────────────────────────────
    function ensureAudioContext() {
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioContext.state === 'suspended') {
            audioContext.resume();
        }
    }

    let nextStartTime = 0;

    function handleAudioFrame(arrayBuffer) {
        ensureAudioContext();

        // Parse AUDI header if present
        const view = new DataView(arrayBuffer);
        let pcmData;
        let sampleRate = SERVER_SAMPLE_RATE;

        if (arrayBuffer.byteLength > AUDIO_HEADER_BYTES) {
            const magic = view.getUint32(0, false); // big-endian
            if (magic === AUDIO_HEADER_MAGIC) {
                sampleRate = view.getUint32(4, false);
                pcmData = arrayBuffer.slice(AUDIO_HEADER_BYTES);
            } else {
                pcmData = arrayBuffer;
            }
        } else {
            pcmData = arrayBuffer;
        }

        if (!pcmData || pcmData.byteLength === 0) return;

        // Convert PCM16 bytes to Float32 samples
        const pcmView = new Int16Array(pcmData);
        const floatSamples = new Float32Array(pcmView.length);
        for (let i = 0; i < pcmView.length; i++) {
            floatSamples[i] = pcmView[i] / 32768.0;
        }

        // Create AudioBuffer and schedule playback
        const frameBuffer = audioContext.createBuffer(1, floatSamples.length, sampleRate);
        frameBuffer.copyToChannel(floatSamples, 0);

        const source = audioContext.createBufferSource();
        source.buffer = frameBuffer;

        // Optionally connect through an analyser for waveform display
        if (!analyserNode) {
            analyserNode = audioContext.createAnalyser();
            analyserNode.fftSize = 512;
            analyserData = new Uint8Array(analyserNode.frequencyBinCount);
            analyserNode.connect(audioContext.destination);
        }
        source.connect(analyserNode);

        const now = audioContext.currentTime;
        if (nextStartTime < now) nextStartTime = now + 0.05;  // Small buffer
        source.start(nextStartTime);
        nextStartTime += frameBuffer.duration;

        isPlaying = true;
        source.onended = () => {
            if (audioContext.currentTime >= nextStartTime - 0.02) {
                isPlaying = false;
                if (!isSpeaking) {
                    setAgentState('Idle', 'idle');
                    visualizerState.textContent = 'Hold the mic button to speak';
                }
            }
        };
    }

    function stopAudioPlayback() {
        nextStartTime = 0;
        isPlaying = false;
        if (audioContext) {
            // Close and recreate to stop all queued audio immediately
            audioContext.close();
            audioContext = null;
            analyserNode = null;
            analyserData = null;
        }
    }

    // ─── Microphone Capture (Push-to-Talk) ────────────────────────────────────
    micBtn.addEventListener('mousedown', startRecording);
    micBtn.addEventListener('touchstart', (e) => { e.preventDefault(); startRecording(); });
    micBtn.addEventListener('mouseup', stopRecording);
    micBtn.addEventListener('touchend', (e) => { e.preventDefault(); stopRecording(); });
    micBtn.addEventListener('mouseleave', () => { if (isRecording) stopRecording(); });

    async function startRecording() {
        if (!isConnected || isRecording) return;

        // Resume AudioContext if needed (browser autoplay policy)
        ensureAudioContext();

        try {
            mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    channelCount: 1,
                    sampleRate: TARGET_SAMPLE_RATE,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                }
            });

            isRecording = true;
            micChunks = [];
            micBtn.classList.add('recording');
            visualizerState.textContent = '🔴 Recording… release to send';
            setAgentState('Listening…', 'listening');
            stopAudioPlayback();  // Stop any AI audio playing

            const sourceNode = audioContext.createMediaStreamSource(mediaStream);

            // Set up analyser for waveform visualisation
            if (!analyserNode) {
                analyserNode = audioContext.createAnalyser();
                analyserNode.fftSize = 512;
                analyserData = new Uint8Array(analyserNode.frequencyBinCount);
                analyserNode.connect(audioContext.destination);
            }
            sourceNode.connect(analyserNode);

            // ScriptProcessorNode for PCM capture (works in all browsers)
            // TODO: Upgrade to AudioWorklet for production
            const bufferSize = 4096;
            scriptProcessor = audioContext.createScriptProcessor(bufferSize, 1, 1);
            scriptProcessor.onaudioprocess = (e) => {
                if (!isRecording) return;
                const floatData = e.inputBuffer.getChannelData(0);
                // Downsample to TARGET_SAMPLE_RATE if AudioContext rate differs
                const downsampled = downsampleFloat32(
                    floatData,
                    audioContext.sampleRate,
                    TARGET_SAMPLE_RATE
                );
                // Convert Float32 → PCM16
                const pcm16 = float32ToPCM16(downsampled);
                micChunks.push(pcm16.buffer);
            };

            sourceNode.connect(scriptProcessor);
            scriptProcessor.connect(audioContext.destination);

            addTimelineEvent('USER_SPEECH_START', 'red');

        } catch (err) {
            console.error('Microphone access denied:', err);
            renderSystemNotice('⚠ Microphone access denied. Check browser permissions.');
            isRecording = false;
            micBtn.classList.remove('recording');
        }
    }

    async function stopRecording() {
        if (!isRecording) return;
        isRecording = false;
        micBtn.classList.remove('recording');
        visualizerState.textContent = 'Processing audio…';
        setAgentState('Sending audio…', 'thinking');

        // Disconnect and stop tracks
        if (scriptProcessor) { scriptProcessor.disconnect(); scriptProcessor = null; }
        if (mediaStream) {
            mediaStream.getTracks().forEach(t => t.stop());
            mediaStream = null;
        }

        addTimelineEvent('USER_SPEECH_END', 'orange');

        // Concatenate all PCM chunks into one ArrayBuffer
        if (micChunks.length === 0) {
            visualizerState.textContent = 'Hold the mic button to speak';
            setAgentState('Idle', 'idle');
            return;
        }

        const totalBytes = micChunks.reduce((sum, buf) => sum + buf.byteLength, 0);
        const combined = new Uint8Array(totalBytes);
        let offset = 0;
        for (const chunk of micChunks) {
            combined.set(new Uint8Array(chunk), offset);
            offset += chunk.byteLength;
        }
        micChunks = [];

        // Send as binary WebSocket frame
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(combined.buffer);
        }
    }

    // ─── PCM Utilities ────────────────────────────────────────────────────────
    function downsampleFloat32(input, inputRate, outputRate) {
        if (inputRate === outputRate) return input;
        const ratio = inputRate / outputRate;
        const outputLength = Math.round(input.length / ratio);
        const output = new Float32Array(outputLength);
        for (let i = 0; i < outputLength; i++) {
            output[i] = input[Math.round(i * ratio)];
        }
        return output;
    }

    function float32ToPCM16(float32Array) {
        const pcm16 = new Int16Array(float32Array.length);
        for (let i = 0; i < float32Array.length; i++) {
            const s = Math.max(-1, Math.min(1, float32Array[i]));
            pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        return pcm16;
    }

    // ─── Text Turn ────────────────────────────────────────────────────────────
    function sendTurn() {
        const text = textTurnInput.value.trim();
        if (!text || !ws || ws.readyState !== WebSocket.OPEN) return;
        ws.send(JSON.stringify({ type: 'text_turn', text }));
        textTurnInput.value = '';
        addTimelineEvent(`TEXT_TURN: "${text.substring(0, 30)}"`, 'blue');
    }

    sendTextBtn.addEventListener('click', sendTurn);
    textTurnInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendTurn(); });

    // ─── Barge-In ─────────────────────────────────────────────────────────────
    bargeInBtn.addEventListener('click', () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'interruption' }));
        }
    });

    // ─── End Session ──────────────────────────────────────────────────────────
    endSessionBtn.addEventListener('click', () => {
        if (ws) ws.close();
        cleanupSession();
    });

    function cleanupSession() {
        isConnected = false;
        statusDot.classList.remove('active');
        statusText.textContent = 'Disconnected';
        visualizerState.textContent = 'Press "Start Session" to connect';
        agentStateBar.style.display = 'none';
        providerBadges.style.display = 'none';

        startSessionBtn.disabled = false;
        micBtn.disabled = true;
        bargeInBtn.disabled = true;
        endSessionBtn.disabled = true;
        textTurnInput.disabled = true;
        sendTextBtn.disabled = true;
        ingestDocBtn.disabled = true;

        if (timerInterval) clearInterval(timerInterval);
        sessionTimer.textContent = '00:00';

        stopAudioPlayback();
        if (mediaStream) { mediaStream.getTracks().forEach(t => t.stop()); mediaStream = null; }
        isRecording = false;
        micBtn.classList.remove('recording');
        addTimelineEvent('SESSION_END', 'gray');
    }

    // ─── Knowledge Ingest ─────────────────────────────────────────────────────
    ingestDocBtn.addEventListener('click', () => {
        const title = docTitle.value.trim();
        const content = docContent.value.trim();
        if (!title || !content) {
            ingestStatus.textContent = '⚠ Please fill in both title and content.';
            ingestStatus.className = 'ingest-status error';
            return;
        }
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'ingest_knowledge',
                title,
                content,
            }));
            ingestStatus.textContent = 'Ingesting…';
            ingestStatus.className = 'ingest-status';
        }
    });

    // ─── UI Rendering ─────────────────────────────────────────────────────────
    function renderTurnMessage(data) {
        if (emptyState) emptyState.style.display = 'none';

        // User bubble
        if (data.user_transcript) {
            const userBubble = document.createElement('div');
            userBubble.className = 'message-bubble message-user';
            userBubble.textContent = data.user_transcript;
            transcriptStream.appendChild(userBubble);
        }

        // Assistant bubble
        const assistantBubble = document.createElement('div');
        assistantBubble.className = 'message-bubble message-assistant';
        const tags = [data.agent_name];
        if (data.rag_used) tags.push('RAG');
        if (data.model_used) tags.push(data.model_used);
        assistantBubble.innerHTML = `<span class="agent-tag">[${tags.join(' · ')}]</span>${data.assistant_text}`;
        transcriptStream.appendChild(assistantBubble);

        transcriptStream.scrollTop = transcriptStream.scrollHeight;
        turnCount += data.user_transcript ? 2 : 1;
        messageCount.textContent = `${turnCount} messages`;
    }

    function renderTranscriptBubble(text, cls) {
        if (emptyState) emptyState.style.display = 'none';
        // Remove any previous interim bubble
        const prev = transcriptStream.querySelector('.user-interim');
        if (prev) prev.remove();

        const bubble = document.createElement('div');
        bubble.className = `message-bubble message-user ${cls}`;
        bubble.textContent = text;
        bubble.style.opacity = '0.7';
        transcriptStream.appendChild(bubble);
        transcriptStream.scrollTop = transcriptStream.scrollHeight;
    }

    function renderSystemNotice(msg) {
        const notice = document.createElement('div');
        notice.className = 'system-notice';
        notice.textContent = msg;
        transcriptStream.appendChild(notice);
        transcriptStream.scrollTop = transcriptStream.scrollHeight;
    }

    function setAgentState(label, type) {
        stateLabel.textContent = label;
        stateDot.className = `state-dot state-${type}`;
        visualizerState.textContent = label;
    }

    // ─── Metrics ──────────────────────────────────────────────────────────────
    function updateMetrics(metrics) {
        if (!metrics) return;
        sttLatencyVal.textContent = `${(metrics.stt_latency_ms || 0).toFixed(1)} ms`;
        ttftVal.textContent       = `${(metrics.llm_ttft_ms || 0).toFixed(1)} ms`;
        ttfaVal.textContent       = `${(metrics.tts_ttfa_ms || 0).toFixed(1)} ms`;
        e2eVal.textContent        = `${(metrics.e2e_total_latency_ms || 0).toFixed(1)} ms`;
        addTimelineEvent(`E2E: ${(metrics.e2e_total_latency_ms || 0).toFixed(0)}ms`, 'purple');
    }

    function updateCost(cost) {
        if (!cost) return;
        const total = (cost.total_cost_usd || 0).toFixed(4);
        turnCostVal.textContent = `$${total}`;
    }

    // ─── Session Timeline ─────────────────────────────────────────────────────
    function addTimelineEvent(label, color = 'gray') {
        const elapsed = sessionSeconds;
        const mins = String(Math.floor(elapsed / 60)).padStart(2, '0');
        const secs = String(elapsed % 60).padStart(2, '0');
        timelineEvents.push({ time: `${mins}:${secs}`, label, color });

        const el = document.createElement('div');
        el.className = 'timeline-event';
        el.innerHTML = `<span class="tl-time">${mins}:${secs}</span><span class="tl-dot tl-${color}"></span><span class="tl-label">${label}</span>`;

        // Clear "no events" placeholder
        const empty = sessionTimeline.querySelector('.timeline-empty');
        if (empty) empty.remove();

        sessionTimeline.appendChild(el);
        sessionTimeline.scrollTop = sessionTimeline.scrollHeight;
    }

    // ─── Evals ────────────────────────────────────────────────────────────────
    runEvalsBtn.addEventListener('click', async () => {
        evalResultsBox.textContent = 'Running benchmark evaluations…';
        try {
            const res = await fetch('/api/v1/evals/run', { method: 'POST' });
            const data = await res.json();
            evalResultsBox.textContent =
                `Pass Rate: ${data.overall_pass_rate}%\n` +
                `Passed: ${data.passed_scenarios}/${data.total_scenarios}\n` +
                `Avg Latency: ${(data.avg_latency_ms || 0).toFixed(1)} ms`;
        } catch (err) {
            evalResultsBox.textContent = `Evaluation failed: ${err.message}`;
        }
    });
});
