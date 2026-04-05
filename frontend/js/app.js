/**
 * Main application controller — state management and screen switching.
 */
const App = {
    sessionId: null,
    selectedMode: null,
    currentState: null,
    _recording: false,
    _audioBlob: null,
    _busy: false,  // prevent double-submits
    _recInterval: null,

    // ==================== INIT ====================
    async init() {
        this.render(UI.landing());
    },

    render(html) {
        document.getElementById('app').innerHTML = html;
    },

    // ==================== LANDING ====================
    selectMode(mode) {
        this.selectedMode = mode;
        document.getElementById('card-voice').classList.toggle('selected', mode === 'voice');
        document.getElementById('card-text').classList.toggle('selected', mode === 'text');
        document.getElementById('start-btn').classList.add('active');
    },

    async startTest() {
        if (!this.selectedMode || this._busy) return;
        this._busy = true;
        this.render(UI.loading('Starting your test...'));

        try {
            const { session_id } = await API.createSession();
            this.sessionId = session_id;
            const state = await API.startTest(session_id, this.selectedMode);
            this._handleState(state);
        } catch (e) {
            console.error(e);
            alert('Failed to start test: ' + e.message);
            this.render(UI.landing());
        } finally {
            this._busy = false;
        }
    },

    // ==================== STATE ROUTER ====================
    _handleState(state) {
        this.currentState = state;
        Timer.stopAll();

        switch (state.step) {
            case 'PART_1':
                this.render(UI.part1(state));
                if (!state.is_part_complete) {
                    if (state.test_mode === 'voice') {
                        this._playQuestion(state.question);
                        this._startInactivityTimer(state);
                    } else {
                        this._startQuestionTimer(state);
                    }
                }
                break;
            case 'PART_2':
                this.render(UI.part2(state));
                if (state.sub_state === 'prep') {
                    this._startPrepTimer();
                } else if (!state.is_part_complete) {
                    if (state.test_mode === 'voice') {
                        if (state.sub_state === 'rounding' && state.question) {
                            this._playQuestion(state.question);
                        }
                        this._startInactivityTimer(state);
                    } else {
                        this._startQuestionTimer(state);
                    }
                }
                break;
            case 'PART_3':
                this.render(UI.part3(state));
                if (!state.is_part_complete) {
                    if (state.test_mode === 'voice') {
                        this._playQuestion(state.question);
                        this._startInactivityTimer(state);
                    } else {
                        this._startQuestionTimer(state);
                    }
                }
                break;
            case 'RESULTS':
                this.render(UI.results(state));
                break;
            default:
                this.render(UI.landing());
        }
    },

    // ==================== SUBMIT ANSWER ====================
    async submitAnswer() {
        if (this._busy) return;
        const input = document.getElementById('answer-input');
        if (!input) return;
        const answer = input.value.trim();
        if (!answer) return;

        this._busy = true;
        input.disabled = true;

        try {
            const state = await API.submitAnswer(this.sessionId, answer);
            this._handleState(state);
        } catch (e) {
            console.error(e);
            alert('Error submitting answer: ' + e.message);
            input.disabled = false;
        } finally {
            this._busy = false;
        }
    },

    // ==================== VOICE RECORDING ====================
    async toggleRecording(partId) {
        if (this._recording) {
            // Stop recording manually
            this._recording = false;
            this._audioBlob = await Audio_.stopRecording();
            Timer.stop('recording');

            const btn = document.getElementById('record-btn');
            const area = document.getElementById('recording-area');
            const status = document.getElementById('recording-status');
            const submitRow = document.getElementById('voice-submit-row');

            if (this._recInterval) { clearInterval(this._recInterval); this._recInterval = null; }
            if (btn) btn.classList.remove('recording');
            if (area) area.classList.remove('recording');
            if (status) status.textContent = 'Recording complete. Submit or re-record.';
            if (submitRow) submitRow.classList.remove('hidden');
            this._stopWaveformAnimation();
        } else {
            // Start recording
            try {
                // Cancel inactivity timer since user is responding
                Timer.stop('inactivity');
                // Hide any inactivity message
                const inactMsg = document.getElementById('inactivity-message');
                if (inactMsg) inactMsg.classList.add('hidden');

                await Audio_.startRecording();
                this._recording = true;
                this._audioBlob = null;

                const btn = document.getElementById('record-btn');
                const area = document.getElementById('recording-area');
                const status = document.getElementById('recording-status');
                const timerEl = document.getElementById('recording-timer');
                const submitRow = document.getElementById('voice-submit-row');

                if (btn) btn.classList.add('recording');
                if (area) area.classList.add('recording');
                if (status) status.textContent = 'Recording...';
                if (submitRow) submitRow.classList.add('hidden');
                this._startWaveformAnimation();

                // Start recording timer (counts up)
                const limit = this.currentState ? this.currentState.time_limit : 30;
                let elapsed = 0;
                this._recInterval = setInterval(() => {
                    elapsed++;
                    const mm = String(Math.floor(elapsed / 60)).padStart(2, '0');
                    const ss = String(elapsed % 60).padStart(2, '0');
                    if (timerEl) timerEl.textContent = `${mm}:${ss}`;
                }, 1000);

                Timer.start('recording', limit,
                    () => {},
                    async () => {
                        // Time's up — stop recording and show must-submit message
                        this._recording = false;
                        this._audioBlob = await Audio_.stopRecording();
                        if (this._recInterval) { clearInterval(this._recInterval); this._recInterval = null; }
                        this._stopWaveformAnimation();

                        const b = document.getElementById('record-btn');
                        const a = document.getElementById('recording-area');
                        const s = document.getElementById('recording-status');
                        const sr = document.getElementById('voice-submit-row');

                        if (b) b.classList.remove('recording');
                        if (a) a.classList.remove('recording');
                        if (s) {
                            s.textContent = 'Time is up. Please submit your recording.';
                            s.classList.add('warning');
                        }
                        if (sr) sr.classList.remove('hidden');
                    }
                );
            } catch (e) {
                console.error(e);
                alert('Could not access microphone. Please allow microphone access.');
            }
        }
    },

    // ==================== WAVEFORM ANIMATION ====================
    _waveformInterval: null,
    _startWaveformAnimation() {
        const dots = document.querySelectorAll('.waveform-dot');
        if (!dots.length) return;
        this._waveformInterval = setInterval(() => {
            dots.forEach(dot => {
                dot.classList.toggle('active', Math.random() > 0.5);
            });
        }, 150);
    },
    _stopWaveformAnimation() {
        if (this._waveformInterval) { clearInterval(this._waveformInterval); this._waveformInterval = null; }
        document.querySelectorAll('.waveform-dot').forEach(d => d.classList.remove('active'));
    },

    async submitVoice(partId) {
        if (this._busy || !this._audioBlob) return;
        this._busy = true;
        this.render(UI.loading('Transcribing your response...'));

        try {
            const isVoice = this.currentState && this.currentState.test_mode === 'voice';
            const question = this.currentState ? this.currentState.question : '';

            const result = await API.transcribe(this._audioBlob, {
                sessionId: this.sessionId,
                includeTimestamps: isVoice,
                part: partId,
                question: question,
            });

            const text = typeof result === 'string' ? result : (result.text || '');
            if (!text || text === '[No speech detected]') {
                // Treat as skip
                const state = await API.skip(this.sessionId, partId.includes('rounding') ? 'rounding' : partId.includes('long') ? 'long_response' : null);
                this._handleState(state);
            } else {
                const state = await API.submitAnswer(this.sessionId, text);
                this._handleState(state);
            }
        } catch (e) {
            console.error(e);
            alert('Error processing recording: ' + e.message);
            if (this.currentState) this._handleState(this.currentState);
        } finally {
            this._audioBlob = null;
            this._busy = false;
        }
    },

    // ==================== NAVIGATION ====================
    async nextPart() {
        if (this._busy) return;
        this._busy = true;

        const step = this.currentState ? this.currentState.step : '';
        const loadMsg = step === 'PART_3' ? 'Calculating your score...' : 'Loading next part...';
        this.render(UI.loading(loadMsg));

        try {
            const state = await API.nextPart(this.sessionId);
            this._handleState(state);
        } catch (e) {
            console.error(e);
            alert('Error: ' + e.message);
        } finally {
            this._busy = false;
        }
    },

    async skipPrep() {
        if (this._busy) return;
        this._busy = true;
        try {
            const state = await API.skipPrep(this.sessionId);
            this._handleState(state);
        } catch (e) {
            console.error(e);
            alert('Error: ' + e.message);
        } finally {
            this._busy = false;
        }
    },

    async retake() {
        if (this._busy) return;
        this._busy = true;
        Timer.stopAll();
        try {
            await API.deleteSession(this.sessionId);
        } catch (e) { /* ignore */ }
        this.sessionId = null;
        this.selectedMode = null;
        this.currentState = null;
        this._busy = false;
        this.render(UI.landing());
    },

    // ==================== TIMERS ====================
    _startPrepTimer() {
        Timer.start('prep', 60,
            (remaining) => {
                const el = document.getElementById('prep-timer-display');
                if (el) el.textContent = Timer.format(remaining);
            },
            async () => {
                const state = await API.completePrep(this.sessionId);
                this._handleState(state);
            }
        );
    },

    _startQuestionTimer(state) {
        // Text mode: auto-skip after double the time limit
        const limit = (state.time_limit || 30) * 2;
        const expectedSession = this.sessionId;
        Timer.start('question', limit,
            () => {},
            async () => {
                if (!this.sessionId || this.sessionId !== expectedSession) return;
                const phase = state.step === 'PART_2' ?
                    (state.sub_state === 'rounding' ? 'rounding' : 'long_response') : null;
                try {
                    const next = await API.skip(this.sessionId, phase);
                    this._handleState(next);
                } catch (e) {
                    console.error('Auto-skip failed:', e);
                }
            }
        );
    },

    _startInactivityTimer(state) {
        // Voice mode: if user doesn't start recording within 20s, show message then skip
        const expectedSession = this.sessionId;
        Timer.start('inactivity', 20,
            () => {},
            async () => {
                if (!this.sessionId || this.sessionId !== expectedSession) return;
                if (this._recording) return;  // already recording, don't skip

                // Show inactivity message
                const msg = document.getElementById('inactivity-message');
                if (msg) {
                    msg.textContent = 'Skipping this question due to inactivity...';
                    msg.classList.remove('hidden');
                }

                // Brief delay so user sees the message, then skip
                setTimeout(async () => {
                    if (!this.sessionId || this.sessionId !== expectedSession) return;
                    const phase = state.step === 'PART_2' ?
                        (state.sub_state === 'rounding' ? 'rounding' : 'long_response') : null;
                    try {
                        const next = await API.skip(this.sessionId, phase);
                        this._handleState(next);
                    } catch (e) {
                        console.error('Inactivity skip failed:', e);
                    }
                }, 2000);
            }
        );
    },

    // ==================== TTS ====================
    _currentAudio: null,
    _lastQuestionText: null,

    async _playQuestion(text) {
        if (!text) return;
        this._lastQuestionText = text;
        console.log('[TTS] Playing question:', text.substring(0, 50));
        try {
            const url = '/api/audio/tts?text=' + encodeURIComponent(text);
            const audio = new window.Audio(url);
            this._currentAudio = audio;

            // Update audio player UI
            const playBtn = document.getElementById('audio-play-btn');
            const trackFill = document.getElementById('audio-track-fill');
            const timeCurrent = document.getElementById('audio-time-current');
            const timeTotal = document.getElementById('audio-time-total');

            if (playBtn) playBtn.innerHTML = UI._svg.pause;

            audio.ontimeupdate = () => {
                if (!audio.duration) return;
                const pct = (audio.currentTime / audio.duration) * 100;
                if (trackFill) trackFill.style.width = pct + '%';
                if (timeCurrent) timeCurrent.textContent = this._formatAudioTime(audio.currentTime);
            };
            audio.onloadedmetadata = () => {
                if (timeTotal) timeTotal.textContent = this._formatAudioTime(audio.duration);
            };
            audio.onended = () => {
                if (playBtn) playBtn.innerHTML = UI._svg.play;
                if (trackFill) trackFill.style.width = '100%';
            };
            audio.onerror = () => {
                if (playBtn) playBtn.innerHTML = UI._svg.play;
            };

            await audio.play();
            console.log('[TTS] Playback started');
        } catch (e) {
            console.error('[TTS] Playback failed:', e);
        }
    },

    _formatAudioTime(sec) {
        if (!sec || isNaN(sec)) return '0:00';
        const m = Math.floor(sec / 60);
        const s = Math.floor(sec % 60);
        return `${m}:${s.toString().padStart(2, '0')}`;
    },

    async replayQuestion() {
        if (this._currentAudio) {
            // If currently playing, pause
            if (!this._currentAudio.paused) {
                this._currentAudio.pause();
                const playBtn = document.getElementById('audio-play-btn');
                if (playBtn) playBtn.innerHTML = UI._svg.play;
                return;
            }
            // If paused, resume
            if (this._currentAudio.currentTime < this._currentAudio.duration) {
                const playBtn = document.getElementById('audio-play-btn');
                if (playBtn) playBtn.innerHTML = UI._svg.pause;
                this._currentAudio.play();
                return;
            }
        }
        // Replay from scratch
        if (this._lastQuestionText) {
            await this._playQuestion(this._lastQuestionText);
        }
    },
};

// Boot
document.addEventListener('DOMContentLoaded', () => App.init());
