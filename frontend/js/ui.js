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
        replay: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>',
        speaker: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>',
        edit: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>',
        tip: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
        arrowRight: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>',
        checkCircle: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
        chevronDown: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>',
        barChart: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
        bookOpen: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
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
    _progressSection(progress, currentPart, label) {
        const tabs = [1, 2, 3].map(n =>
            `<div class="test-part-tab ${n === currentPart ? 'active' : 'inactive'}">Part ${n}</div>`
        ).join('');
        const displayLabel = label || `Question ${progress.current} of ${progress.total}`;

        return `<div class="test-progress">
            <div class="test-progress-header">
                <span>${displayLabel}</span>
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

    // ==================== AUDIO DISPLAY ====================
    _audioDisplay() {
        return `<div class="test-audio-display" id="audio-player">
            <button class="audio-play-btn" id="audio-play-btn" onclick="App.replayQuestion()">
                ${this._svg.play}
            </button>
            <div class="audio-display-info">
                <div class="audio-display-label">AI Examiner</div>
                <div class="audio-display-status" id="audio-status">Playing question...</div>
            </div>
            <button class="audio-replay-btn" id="audio-replay-btn" onclick="App.replayQuestion()" title="Replay question">
                ${this._svg.replay}
            </button>
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
        const redirect = state.is_redirect ? `<div class="redirect-notice">The examiner has rephrased the question. Please try again.</div>` : '';

        let inputArea;
        if (state.test_mode === 'voice') {
            inputArea = `
                ${this._audioDisplay()}
                <div class="test-time-limit">${this._svg.clock} Time Limit: ${state.time_limit} seconds</div>
                ${redirect}
                ${this._voiceInput('part1')}`;
        } else {
            inputArea = `
                <div class="test-time-limit">${this._svg.clock} Time Limit: ${state.time_limit} seconds</div>
                ${redirect}
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
        const pc = state.prompt_card || {};
        const circumference = 2 * Math.PI * 52; // r=52 → ≈326.73

        const bullets = (pc.bullet_points || []).map((b, i) => `
            <div class="prep-bullet-item">
                <span class="prep-bullet-num">${i + 1}</span>
                <span class="prep-bullet-text">${this._esc(b)}</span>
            </div>`).join('');

        return `${this.topbar()}<div class="content">
            ${tabs}
            <div class="prep-page-header">
                <div class="prep-page-badge">${this._svg.clock} Preparation Time — Part 2</div>
                <h2 class="prep-page-title">Read &amp; Prepare Your Response</h2>
                <p class="prep-page-subtitle">You have 1 minute to read the topic card and organize your thoughts before speaking.</p>
            </div>

            <div class="prep-topic-card">
                <div class="prep-topic-header">
                    <div class="prep-topic-icon">${this._svg.chat}</div>
                    <span class="prep-topic-label">Your Topic</span>
                </div>
                <div class="prep-topic-body">
                    <h3 class="prep-topic-title">${this._esc(pc.main_prompt || '')}</h3>
                    <div class="prep-say-label">You should say:</div>
                    <div class="prep-bullet-list">${bullets}</div>
                </div>
            </div>

            <div class="prep-bottom-row">
                <div class="prep-timer-wrap">
                    <div class="prep-timer-circle-wrap">
                        <svg class="prep-ring" width="144" height="144" viewBox="0 0 144 144">
                            <circle class="prep-ring-bg" cx="72" cy="72" r="52" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="6"/>
                            <circle class="prep-ring-fill" id="prep-ring-fill" cx="72" cy="72" r="52" fill="none"
                                stroke="url(#prepGrad)" stroke-width="6" stroke-linecap="round"
                                stroke-dasharray="${circumference}" stroke-dashoffset="0"
                                transform="rotate(-90 72 72)"/>
                            <defs>
                                <linearGradient id="prepGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" stop-color="#AD46FF"/>
                                    <stop offset="100%" stop-color="#8E51FF"/>
                                </linearGradient>
                            </defs>
                        </svg>
                        <div class="prep-timer-inner">
                            <span class="prep-timer-display" id="prep-timer-display">1:00</span>
                            <span class="prep-timer-remaining">remaining</span>
                        </div>
                    </div>
                    <div class="prep-timer-label">Preparation time</div>
                </div>

                <div class="prep-notes-card">
                    <div class="prep-notes-header">
                        <div class="prep-notes-icon">${this._svg.edit}</div>
                        <span class="prep-notes-title">Quick Notes</span>
                        <span class="prep-notes-optional">Optional</span>
                    </div>
                    <textarea class="prep-notes-area" placeholder="Jot down key ideas, vocabulary, or structure..."></textarea>
                </div>
            </div>

            <div class="prep-tip-banner">
                <div class="prep-tip-icon">${this._svg.tip}</div>
                <p><span class="prep-tip-bold">Tip:</span> Structure your answer with an introduction, main points, and a conclusion. Use specific examples to support your ideas.</p>
            </div>

            <div class="prep-actions">
                <button class="prep-skip-btn" onclick="App.skipPrep()">Skip Preparation</button>
                <button class="btn-primary" onclick="App.skipPrep()">I'm Ready to Speak ${this._svg.arrowRight}</button>
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
                ${this._audioDisplay()}
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
        const redirect = state.is_redirect ? `<div class="redirect-notice">The examiner has rephrased the question. Please try again.</div>` : '';

        let inputArea;
        if (state.test_mode === 'voice') {
            inputArea = `
                ${this._audioDisplay()}
                <div class="test-time-limit">${this._svg.clock} Time Limit: 30 seconds</div>
                ${redirect}
                ${this._voiceInput('part2_rounding')}`;
        } else {
            inputArea = `
                <div class="test-time-limit">${this._svg.clock} Time Limit: 30 seconds</div>
                ${redirect}
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
        const cfg = this._partConfig[3];
        const redirect = state.is_redirect ? `<div class="redirect-notice">The examiner has rephrased the question. Please try again.</div>` : '';
        const total = p.total_main || 3;
        const current = Math.min((p.main_questions || 0) + 1, total);
        const followupSuffix = p.followups > 0 ? ` · Follow-up ${p.followups}` : '';
        const progressLabel = `Main Question ${current} of ${total}${followupSuffix}`;
        const progress = this._progressSection({ current, total, percent: ((current - 1) / total) * 100 }, 3, progressLabel);

        let inputArea;
        if (state.test_mode === 'voice') {
            inputArea = `
                ${this._audioDisplay()}
                <div class="test-time-limit">${this._svg.clock} Time Limit: ${state.time_limit} seconds</div>
                ${redirect}
                ${this._voiceInput('part3')}`;
        } else {
            inputArea = `
                <div class="test-time-limit">${this._svg.clock} Time Limit: ${state.time_limit} seconds</div>
                ${redirect}
                <div class="test-examiner-q">${this._esc(state.question)}</div>
                ${this._textInput('Type your answer here...', 2000, 5)}`;
        }

        return `${this.topbar()}<div class="content">
            ${progress}
            <div class="test-card">
                <div class="test-card-header">
                    <h2>${cfg.title}</h2>
                    <p>${cfg.desc}</p>
                </div>
                <div class="test-card-body">
                    <div class="test-topic-badge">${this._svg.chat} Theme: ${this._esc(state.theme)}</div>
                    ${inputArea}
                </div>
            </div>
        </div>`;
    },

    // ==================== RESULTS ====================
    _cefrDescriptions: {
        'C2': 'Mastery', 'C1': 'Advanced', 'B2': 'Upper Intermediate',
        'B1': 'Intermediate', 'A2': 'Elementary', 'A1': 'Beginner'
    },

    results(data) {
        const scores = data.scores || {};
        const s = scores.scores || {};
        const band = (scores.final_band || 0).toFixed(1);
        const cefr = scores.cefr_level || 'B1';
        const cefrLabel = `${cefr} — ${this._cefrDescriptions[cefr] || cefr}`;

        const criteria = [
            { key: 'fluency_coherence',  label: 'Fluency & Coherence',         weight: '25%' },
            { key: 'lexical_resource',   label: 'Lexical Resource',             weight: '20%' },
            { key: 'grammatical_range',  label: 'Grammar Range & Accuracy',     weight: '20%' },
            { key: 'coherence_cohesion', label: 'Coherence & Cohesion',         weight: '15%' },
            { key: 'task_achievement',   label: 'Task Achievement',             weight: '20%' },
        ];

        const scoreRows = criteria.map((c, i) => {
            const item = s[c.key] || {};
            const score = item.score || 0;
            const scoreDisp = score % 1 === 0 ? String(score) : score.toFixed(1);
            const pct = (score / 9 * 100).toFixed(1);
            const isLast = i === criteria.length - 1;
            const isGreen = score >= 7;
            const badgeBg    = isGreen ? 'rgba(0,188,125,0.15)'  : 'rgba(254,154,0,0.15)';
            const badgeBdr   = isGreen ? 'rgba(0,188,125,0.25)'  : 'rgba(254,154,0,0.25)';
            const scoreColor = isGreen ? '#00D492'                : '#FFB900';
            const barGrad    = isGreen ? 'linear-gradient(90deg,#00D492,#00BC7D)' : 'linear-gradient(90deg,#FFB900,#FE9A00)';
            return `<div class="res-score-row${isLast ? ' res-score-row--last' : ''}">
                <div class="res-score-badge" style="background:${badgeBg};border-color:${badgeBdr};color:${scoreColor}">${scoreDisp}</div>
                <div class="res-score-info">
                    <div class="res-score-name-row">
                        <span class="res-score-name">${this._esc(c.label)}</span>
                        <span class="res-score-weight">${c.weight}</span>
                    </div>
                    <div class="res-score-bar"><div class="res-score-bar-fill" style="width:${pct}%;background:${barGrad}"></div></div>
                </div>
            </div>`;
        }).join('');

        const svgCheck = `<svg viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 7l3.5 3.5L12 3" stroke="#00BC7D" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
        const svgWarn  = `<svg viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M7 2L13 12H1L7 2z" stroke="#FE9A00" stroke-width="1.5" stroke-linejoin="round"/><path d="M7 6v3" stroke="#FE9A00" stroke-width="1.5" stroke-linecap="round"/><circle cx="7" cy="10.5" r="0.75" fill="#FE9A00"/></svg>`;
        const svgTrend = `<svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 11l4-4 3 3 5-6" stroke="#00BC7D" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M11 4h3v3" stroke="#00BC7D" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
        const svgAlert = `<svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="8" cy="8" r="6.5" stroke="#FE9A00" stroke-width="1.5"/><path d="M8 5v4" stroke="#FE9A00" stroke-width="1.5" stroke-linecap="round"/><circle cx="8" cy="11" r="0.75" fill="#FE9A00"/></svg>`;

        const strengthItems = (scores.strengths || []).map(t =>
            `<div class="res-fb-item">
                <div class="res-fb-dot res-fb-dot--green">${svgCheck}</div>
                <span>${this._esc(t)}</span>
            </div>`).join('');

        const improveItems = (scores.areas_for_improvement || []).map(t =>
            `<div class="res-fb-item">
                <div class="res-fb-dot res-fb-dot--orange">${svgWarn}</div>
                <span>${this._esc(t)}</span>
            </div>`).join('');

        return `${this.topbar()}<div class="content">
            <div class="res-header">
                <div class="res-complete-badge">${this._svg.checkCircle} Assessment Complete</div>
                <h1 class="res-title">Your Speaking Assessment Results</h1>
            </div>

            <div class="res-hero-card">
                <div class="res-hero-bg">
                    <p class="res-hero-label">Your IELTS Speaking Band Score</p>
                    <div class="res-band-circle"><span class="res-band-num">${band}</span></div>
                    <div class="res-cefr-pill"><span class="res-cefr-muted">CEFR Level:</span> ${this._esc(cefrLabel)}</div>
                </div>
                ${scores.overall_feedback ? `<div class="res-hero-feedback"><p>${this._esc(scores.overall_feedback)}</p></div>` : ''}
            </div>

            <div class="res-fb-row">
                <div class="res-fb-card">
                    <div class="res-fb-card-header">
                        <div class="res-fb-icon res-fb-icon--green">${svgTrend}</div>
                        <span>Strengths</span>
                    </div>
                    <div class="res-fb-items">${strengthItems}</div>
                </div>
                <div class="res-fb-card">
                    <div class="res-fb-card-header">
                        <div class="res-fb-icon res-fb-icon--orange">${svgAlert}</div>
                        <span>Areas to Improve</span>
                    </div>
                    <div class="res-fb-items">${improveItems}</div>
                </div>
            </div>

            <div class="res-breakdown">
                <div class="res-breakdown-header">
                    ${this._svg.barChart}
                    <h2>Score Breakdown</h2>
                </div>
                <div class="res-score-card">${scoreRows}</div>
            </div>

            <div class="res-actions res-actions--center">
                <button class="btn-primary" onclick="App.retake()">${this._svg.replay} Take Another Test</button>
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
