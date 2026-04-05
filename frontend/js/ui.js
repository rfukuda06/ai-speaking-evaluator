/**
 * UI renderers — each function returns an HTML string for a screen.
 */
const UI = {
    // SVG icons as inline strings
    _svg: {
        micW: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>',
        micP: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#AD46FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>',
        play: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff"><polygon points="6,3 20,12 6,21"/></svg>',
        pause: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>',
        clock: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
        chat: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
        stop: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#fff"><rect x="6" y="6" width="12" height="12" rx="1"/></svg>',
    },

    _icon(svgStr, w = 20, h = 20) {
        const uri = 'data:image/svg+xml,' + encodeURIComponent(svgStr);
        return `<img src="${uri}" width="${w}" height="${h}" style="display:block;" />`;
    },

    get icons() {
        if (this._icons) return this._icons;
        this._icons = {
            micW: this._icon(this._svg.micW),
            micP: this._icon(this._svg.micP),
            star: this._icon('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#DAB2FF"><path d="M12 2l1.5 4.5L18 8l-4.5 1.5L12 14l-1.5-4.5L6 8l4.5-1.5L12 2z"/><path d="M19 13l1 3 3 1-3 1-1 3-1-3-3-1 3-1 1-3z"/></svg>', 16, 16),
            speaker: this._icon('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#DAB2FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>'),
            globe: this._icon('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#DAB2FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>'),
            clock: this._icon('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#DAB2FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'),
            check: this._icon('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill="rgba(74,222,128,0.15)" stroke="#4ADE80" stroke-width="1.5"/><path d="M8 12l3 3 5-6" fill="none" stroke="#4ADE80" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>', 16, 16),
            kbd: this._icon('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="12" rx="2" ry="2"/><path d="M6 8h0M10 8h0M14 8h0M18 8h0M8 12h8M6 12h0M18 12h0"/></svg>'),
            arrow: this._icon('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>', 16, 16),
        };
        return this._icons;
    },

    // ==================== TOPBAR ====================
    topbar() {
        const i = this.icons;
        return `<div class="topbar">
            <div class="topbar-left">
                <div class="logo">${i.micW}</div>
                <div>
                    <div class="brand-title">AI Speaking Evaluator</div>
                    <div class="brand-sub">IELTS Practice &amp; Assessment</div>
                </div>
            </div>
        </div>`;
    },

    // ==================== LANDING PAGE ====================
    landing() {
        const i = this.icons;
        return `${this.topbar()}
        <div class="content">
            <div class="hero">
                <div class="badge">${i.star} AI-Powered Assessment</div>
                <h1>Test Your English Speaking Skills</h1>
                <p class="hero-desc">Get an authentic IELTS-style speaking evaluation with detailed feedback and band score assessment powered by AI.</p>
            </div>
            <div class="features">
                <div class="feat">${i.speaker}<div class="feat-title">3-Part Interview</div><div class="feat-sub">IELTS format</div></div>
                <div class="feat">${i.globe}<div class="feat-title">Band 1&ndash;9 Score</div><div class="feat-sub">CEFR aligned</div></div>
                <div class="feat">${i.clock}<div class="feat-title">~15 Minutes</div><div class="feat-sub">Full assessment</div></div>
            </div>
            <div class="mode-label">Choose Your Mode</div>
            <div class="modes">
                <div class="mode-card" id="card-voice" onclick="App.selectMode('voice')">
                    <div class="mode-header">
                        <div class="mode-icon voice">${i.micP}</div>
                        <span class="rec-badge">Recommended</span>
                    </div>
                    <h3>Voice Mode</h3>
                    <ul class="mode-list">
                        <li>${i.check} Tests your actual speaking ability</li>
                        <li>${i.check} Natural conversation flow</li>
                        <li>${i.check} Authentic IELTS-style assessment</li>
                        <li>${i.check} Fluency &amp; pronunciation analysis</li>
                    </ul>
                </div>
                <div class="mode-card" id="card-text" onclick="App.selectMode('text')">
                    <div class="mode-header">
                        <div class="mode-icon text">${i.kbd}</div>
                    </div>
                    <h3>Text Mode</h3>
                    <ul class="mode-list">
                        <li>${i.check} Type your responses instead</li>
                        <li>${i.check} No microphone needed</li>
                        <li>${i.check} Simplified assessment</li>
                        <li>${i.check} Good for quiet environments</li>
                    </ul>
                </div>
            </div>
            <div class="start-row">
                <button class="start-btn" id="start-btn" onclick="App.startTest()">Start Test ${i.arrow}</button>
            </div>
        </div>`;
    },

    // ==================== PROGRESS + TABS ====================
    _progressSection(progress, currentPart) {
        const tabs = [1, 2, 3].map(n =>
            `<div class="test-part-tab ${n === currentPart ? 'active' : 'inactive'}">Part ${n}</div>`
        ).join('');

        return `<div class="test-progress">
            <div class="test-progress-header">
                <span>Question ${progress.current} of ${progress.total}</span>
                <span>Part ${currentPart} / 3</span>
            </div>
            <div class="test-progress-track"><div class="test-progress-fill" style="width:${progress.percent}%"></div></div>
        </div>
        <div class="test-part-tabs">${tabs}</div>`;
    },

    _partTabs(currentPart) {
        const tabs = [1, 2, 3].map(n =>
            `<div class="test-part-tab ${n === currentPart ? 'active' : 'inactive'}">Part ${n}</div>`
        ).join('');
        return `<div class="test-part-tabs" style="padding-top:24px">${tabs}</div>`;
    },

    // ==================== AUDIO PLAYER ====================
    _audioPlayer() {
        return `<div class="test-audio-player" id="audio-player">
            <div class="test-audio-player-row">
                <button class="audio-play-btn" id="audio-play-btn" onclick="App.replayQuestion()">
                    ${this._svg.play}
                </button>
                <div class="audio-track-wrapper">
                    <div class="audio-track"><div class="audio-track-fill" id="audio-track-fill"></div></div>
                    <div class="audio-timestamps">
                        <span id="audio-time-current">0:00</span>
                        <span id="audio-time-total">0:00</span>
                    </div>
                </div>
            </div>
            <div class="test-audio-label">Audio: Question</div>
        </div>`;
    },

    // ==================== WAVEFORM DOTS ====================
    _waveformDots(count = 40) {
        let dots = '';
        for (let i = 0; i < count; i++) {
            dots += '<div class="waveform-dot"></div>';
        }
        return `<div class="waveform-dots">${dots}</div>`;
    },

    // ==================== VOICE INPUT (RECORDING AREA) ====================
    _voiceInput(partId) {
        return `<div class="test-record-area" id="recording-area">
            <p class="record-prompt" id="recording-status">Tap the microphone to start recording</p>
            <button class="test-mic-btn" id="record-btn" onclick="App.toggleRecording('${partId}')">
                ${this._svg.micW}
            </button>
            ${this._waveformDots()}
            <div class="record-timer" id="recording-timer">00:00</div>
            <div class="inactivity-message hidden" id="inactivity-message"></div>
            <div class="submit-row hidden" id="voice-submit-row">
                <button class="btn-primary" onclick="App.submitVoice('${partId}')">Submit Recording</button>
            </div>
        </div>`;
    },

    // ==================== TEXT INPUT ====================
    _textInput(placeholder, maxlength, rows) {
        return `<textarea class="test-text-area" id="answer-input" placeholder="${placeholder}" maxlength="${maxlength}" ${rows ? `rows="${rows}"` : ''}></textarea>
        <div class="submit-row">
            <button class="btn-primary" onclick="App.submitAnswer()">Submit</button>
        </div>`;
    },

    // ==================== PART HEADER CONFIG ====================
    _partConfig: {
        1: { title: 'Part 1: The Interview', desc: "I'll ask you some questions about different topics. Please respond with brief, conversational responses." },
        2: { title: 'Part 2: The Long Turn', desc: "You will be given a topic card. You have 1 minute to prepare, then speak for 1-2 minutes." },
        3: { title: 'Part 3: The Discussion', desc: "I'll ask you more abstract questions related to the Part 2 topic. Give detailed, thoughtful responses." },
    },

    // ==================== PART 1 ====================
    part1(state) {
        if (state.is_part_complete) {
            return this._partComplete(state.completion_message, 'Continue to Part 2', 'App.nextPart()');
        }

        const progress = this._progressSection(state.progress, 1);
        const cfg = this._partConfig[1];
        const ack = state.acknowledgment ? `<div class="test-examiner-ack">"${this._esc(state.acknowledgment)}"</div>` : '';
        const redirect = state.is_redirect ? `<div class="redirect-notice">The examiner has rephrased the question. Please try again.</div>` : '';

        let inputArea;
        if (state.test_mode === 'voice') {
            inputArea = `
                ${this._audioPlayer()}
                <div class="test-time-limit">${this._svg.clock} Time Limit: ${state.time_limit} seconds</div>
                ${ack}${redirect}
                <div class="test-examiner-q">${this._esc(state.question)}</div>
                ${this._voiceInput('part1')}`;
        } else {
            inputArea = `
                <div class="test-time-limit">${this._svg.clock} Time Limit: ${state.time_limit} seconds</div>
                ${ack}${redirect}
                <div class="test-examiner-q">${this._esc(state.question)}</div>
                ${this._textInput('Type your answer here...', 1000)}`;
        }

        return `${this.topbar()}<div class="content">
            ${progress}
            <div class="test-card">
                <div class="test-card-header">
                    <h2>${cfg.title}</h2>
                    <p>${cfg.desc}</p>
                </div>
                <div class="test-card-body">
                    <div class="test-topic-badge">${this._svg.chat} Current Topic: ${this._esc(state.topic)}</div>
                    ${inputArea}
                </div>
            </div>
        </div>`;
    },

    // ==================== PART 2 ====================
    part2(state) {
        if (state.is_part_complete) {
            return this._partComplete(state.completion_message, 'Continue to Part 3', 'App.nextPart()');
        }

        if (state.sub_state === 'prep') {
            return this._part2Prep(state);
        } else if (state.sub_state === 'long_response') {
            return this._part2LongResponse(state);
        } else {
            return this._part2Rounding(state);
        }
    },

    _part2Prep(state) {
        const tabs = this._partTabs(2);
        const cfg = this._partConfig[2];
        const pc = state.prompt_card || {};
        const bullets = (pc.bullet_points || []).map(b => `<li>${this._esc(b)}</li>`).join('');

        return `${this.topbar()}<div class="content">
            ${tabs}
            <div class="test-card">
                <div class="test-card-header">
                    <h2>${cfg.title}</h2>
                    <p>${cfg.desc}</p>
                </div>
                <div class="test-card-body">
                    <div class="test-topic-badge">${this._svg.chat} Your Topic</div>
                    <div class="test-examiner-q">${this._esc(pc.main_prompt || '')}</div>
                    ${bullets ? `<div class="prompt-card" style="margin-bottom:16px"><ul>${bullets}</ul></div>` : ''}
                    <div class="prep-timer">
                        <div class="timer-display" id="prep-timer-display">1:00</div>
                        <div class="timer-label">Preparation time remaining</div>
                    </div>
                    <div class="submit-row">
                        <button class="btn-secondary" onclick="App.skipPrep()">Skip Preparation</button>
                    </div>
                </div>
            </div>
        </div>`;
    },

    _part2LongResponse(state) {
        const tabs = this._partTabs(2);
        const cfg = this._partConfig[2];
        const pc = state.prompt_card || {};
        const redirect = state.is_redirect ? `<div class="redirect-notice">${this._esc(state.redirect_message)}</div>` : '';

        let inputArea;
        if (state.test_mode === 'voice') {
            inputArea = `
                ${this._audioPlayer()}
                <div class="test-time-limit">${this._svg.clock} Time Limit: ${state.time_limit} seconds</div>
                ${redirect}
                ${this._voiceInput('part2_long')}`;
        } else {
            inputArea = `
                <div class="test-time-limit">${this._svg.clock} Time Limit: ${state.time_limit} seconds</div>
                ${redirect}
                ${this._textInput('Speak about the topic for 1-2 minutes...', 3000, 8)}`;
        }

        return `${this.topbar()}<div class="content">
            ${tabs}
            <div class="test-card">
                <div class="test-card-header">
                    <h2>${cfg.title}</h2>
                    <p>Now speak about your topic for 1-2 minutes.</p>
                </div>
                <div class="test-card-body">
                    <div class="test-topic-badge">${this._svg.chat} Topic: ${this._esc(pc.main_prompt || '')}</div>
                    ${inputArea}
                </div>
            </div>
        </div>`;
    },

    _part2Rounding(state) {
        const tabs = this._partTabs(2);
        const cfg = this._partConfig[2];
        const rp = state.rounding_progress || {};
        const ack = state.acknowledgment ? `<div class="test-examiner-ack">"${this._esc(state.acknowledgment)}"</div>` : '';
        const redirect = state.is_redirect ? `<div class="redirect-notice">The examiner has rephrased the question. Please try again.</div>` : '';

        let inputArea;
        if (state.test_mode === 'voice') {
            inputArea = `
                ${this._audioPlayer()}
                <div class="test-time-limit">${this._svg.clock} Time Limit: 30 seconds</div>
                ${ack}${redirect}
                <div class="test-examiner-q">${this._esc(state.question)}</div>
                ${this._voiceInput('part2_rounding')}`;
        } else {
            inputArea = `
                <div class="test-time-limit">${this._svg.clock} Time Limit: 30 seconds</div>
                ${ack}${redirect}
                <div class="test-examiner-q">${this._esc(state.question)}</div>
                ${this._textInput('Type your answer here...', 1000)}`;
        }

        return `${this.topbar()}<div class="content">
            ${tabs}
            <div class="test-card">
                <div class="test-card-header">
                    <h2>${cfg.title}</h2>
                    <p>Rounding-off question ${(rp.current || 0) + 1} of ${rp.total || 2}</p>
                </div>
                <div class="test-card-body">
                    ${inputArea}
                </div>
            </div>
        </div>`;
    },

    // ==================== PART 3 ====================
    part3(state) {
        if (state.is_part_complete) {
            return this._partComplete(state.completion_message, 'View Results', 'App.nextPart()');
        }

        const p = state.progress || {};
        const tabs = this._partTabs(3);
        const cfg = this._partConfig[3];
        const ack = state.acknowledgment ? `<div class="test-examiner-ack">"${this._esc(state.acknowledgment)}"</div>` : '';
        const redirect = state.is_redirect ? `<div class="redirect-notice">The examiner has rephrased the question. Please try again.</div>` : '';

        let inputArea;
        if (state.test_mode === 'voice') {
            inputArea = `
                ${this._audioPlayer()}
                <div class="test-time-limit">${this._svg.clock} Time Limit: ${state.time_limit} seconds</div>
                ${ack}${redirect}
                <div class="test-examiner-q">${this._esc(state.question)}</div>
                ${this._voiceInput('part3')}`;
        } else {
            inputArea = `
                <div class="test-time-limit">${this._svg.clock} Time Limit: ${state.time_limit} seconds</div>
                ${ack}${redirect}
                <div class="test-examiner-q">${this._esc(state.question)}</div>
                ${this._textInput('Type your answer here...', 2000, 5)}`;
        }

        const progressInfo = `<div style="font-size:13px;color:var(--text-muted);margin-bottom:16px">
            Main Question ${(p.main_questions || 0) + 1} of ${p.total_main || 3}
            ${p.followups > 0 ? ` · Follow-up ${p.followups}` : ''}
        </div>`;

        return `${this.topbar()}<div class="content">
            ${tabs}
            <div class="test-card">
                <div class="test-card-header">
                    <h2>${cfg.title}</h2>
                    <p>${cfg.desc}</p>
                </div>
                <div class="test-card-body">
                    <div class="test-topic-badge">${this._svg.chat} Theme: ${this._esc(state.theme)}</div>
                    ${progressInfo}
                    ${inputArea}
                </div>
            </div>
        </div>`;
    },

    // ==================== RESULTS ====================
    results(data) {
        const scores = data.scores || {};
        const s = scores.scores || {};

        const band = (scores.final_band || 0).toFixed(1);
        const cefr = scores.cefr_level || 'N/A';

        const criteria = [
            { key: 'fluency_coherence', label: 'Fluency & Coherence', weight: '25%' },
            { key: 'lexical_resource', label: 'Lexical Resource', weight: '20%' },
            { key: 'grammatical_range', label: 'Grammar Range & Accuracy', weight: '20%' },
            { key: 'coherence_cohesion', label: 'Coherence & Cohesion', weight: '15%' },
            { key: 'task_achievement', label: 'Task Achievement', weight: '20%' },
        ];

        const grid = criteria.map(c => {
            const item = s[c.key] || {};
            const sc = (item.score || 0).toFixed(1);
            const pct = ((item.score || 0) / 9 * 100).toFixed(0);
            return `<div class="score-item">
                <div class="label">${c.label} (${c.weight})</div>
                <div class="value">${sc}</div>
                <div class="bar"><div class="bar-fill" style="width:${pct}%"></div></div>
            </div>`;
        }).join('');

        const strengths = (scores.strengths || []).map(s => `<li>${this._esc(s)}</li>`).join('');
        const improvements = (scores.areas_for_improvement || []).map(s => `<li>${this._esc(s)}</li>`).join('');

        return `${this.topbar()}<div class="content">
            <div class="results-header">
                <div class="band-score">${band}</div>
                <div style="font-size:14px;color:var(--text-muted);margin-top:4px">IELTS Band Score</div>
                <div class="cefr-badge">CEFR Level: ${cefr}</div>
            </div>
            <div class="score-grid">${grid}</div>
            ${strengths ? `<div class="feedback-section strengths"><h3>Strengths</h3><ul>${strengths}</ul></div>` : ''}
            ${improvements ? `<div class="feedback-section improvements"><h3>Areas for Improvement</h3><ul>${improvements}</ul></div>` : ''}
            ${scores.overall_feedback ? `<div class="overall-feedback">${this._esc(scores.overall_feedback)}</div>` : ''}
            <div class="submit-row mt-24">
                <button class="btn-primary" onclick="App.retake()">Retake Test</button>
            </div>
        </div>`;
    },

    // ==================== LOADING ====================
    loading(message) {
        return `${this.topbar()}<div class="content">
            <div class="loading">
                <div class="spinner"></div>
                <div class="loading-text">${this._esc(message || 'Loading...')}</div>
            </div>
        </div>`;
    },

    // ==================== SHARED HELPERS ====================
    _partComplete(message, btnLabel, btnAction) {
        return `${this.topbar()}<div class="content">
            <div class="completion-card" style="margin-top:48px">
                <h2>Part Complete</h2>
                <p>${this._esc(message)}</p>
                <button class="btn-primary" onclick="${btnAction}">${btnLabel}</button>
            </div>
        </div>`;
    },

    _esc(str) {
        if (!str) return '';
        const el = document.createElement('span');
        el.textContent = str;
        return el.innerHTML;
    },
};
