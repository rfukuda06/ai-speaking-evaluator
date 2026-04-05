/**
 * API wrapper — all fetch calls to the FastAPI backend.
 */
const API = {
    baseUrl: '',

    async _json(method, path, body) {
        const opts = {
            method,
            headers: { 'Content-Type': 'application/json' },
        };
        if (body) opts.body = JSON.stringify(body);
        const res = await fetch(this.baseUrl + path, opts);
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(err.detail || 'Request failed');
        }
        return res.json();
    },

    // Session
    createSession() { return this._json('POST', '/api/session'); },
    getSession(id) { return this._json('GET', `/api/session/${id}`); },
    deleteSession(id) { return this._json('DELETE', `/api/session/${id}`); },

    // Test flow
    startTest(sessionId, mode) {
        return this._json('POST', '/api/test/start', { session_id: sessionId, mode });
    },
    submitAnswer(sessionId, answer) {
        return this._json('POST', '/api/test/answer', { session_id: sessionId, answer });
    },
    skip(sessionId, phase) {
        return this._json('POST', '/api/test/skip', { session_id: sessionId, phase });
    },
    nextPart(sessionId) {
        return this._json('POST', '/api/test/next-part', { session_id: sessionId });
    },
    skipPrep(sessionId) {
        return this._json('POST', '/api/test/skip-prep', { session_id: sessionId });
    },
    completePrep(sessionId) {
        return this._json('POST', '/api/test/complete-prep', { session_id: sessionId });
    },
    score(sessionId) {
        return this._json('POST', '/api/test/score', { session_id: sessionId });
    },

    // Audio
    async tts(text) {
        const form = new FormData();
        form.append('text', text);
        const res = await fetch(this.baseUrl + '/api/audio/tts', { method: 'POST', body: form });
        if (!res.ok) throw new Error('TTS failed');
        return res.blob();
    },

    async transcribe(audioBlob, { sessionId, includeTimestamps, part, question } = {}) {
        const form = new FormData();
        form.append('file', audioBlob, 'audio.webm');
        if (sessionId) form.append('session_id', sessionId);
        if (includeTimestamps) form.append('include_timestamps', 'true');
        if (part) form.append('part', part);
        if (question) form.append('question', question);
        const res = await fetch(this.baseUrl + '/api/audio/transcribe', { method: 'POST', body: form });
        if (!res.ok) throw new Error('Transcription failed');
        return res.json();
    },
};
