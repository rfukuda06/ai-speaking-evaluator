/**
 * Audio utilities — MediaRecorder for recording, TTS playback.
 */
const Audio_ = {
    _recorder: null,
    _chunks: [],
    _stream: null,

    /**
     * Start recording audio from microphone.
     * @returns {Promise<void>}
     */
    async startRecording() {
        this._chunks = [];
        this._stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this._recorder = new MediaRecorder(this._stream, { mimeType: 'audio/webm' });
        this._recorder.ondataavailable = (e) => {
            if (e.data.size > 0) this._chunks.push(e.data);
        };
        this._recorder.start();
    },

    /**
     * Stop recording and return the audio blob.
     * @returns {Promise<Blob>}
     */
    stopRecording() {
        return new Promise((resolve) => {
            if (!this._recorder || this._recorder.state === 'inactive') {
                resolve(null);
                return;
            }
            this._recorder.onstop = () => {
                const blob = new Blob(this._chunks, { type: 'audio/webm' });
                this._chunks = [];
                if (this._stream) {
                    this._stream.getTracks().forEach(t => t.stop());
                    this._stream = null;
                }
                resolve(blob);
            };
            this._recorder.stop();
        });
    },

    isRecording() {
        return this._recorder && this._recorder.state === 'recording';
    },

    /**
     * Play TTS audio from a blob.
     * @param {Blob} blob - Audio blob (audio/mpeg)
     * @returns {Promise<void>} Resolves when playback ends
     */
    playBlob(blob) {
        return new Promise((resolve, reject) => {
            const url = URL.createObjectURL(blob);
            const audio = new window.Audio(url);
            audio.onended = () => { URL.revokeObjectURL(url); resolve(); };
            audio.onerror = (e) => { URL.revokeObjectURL(url); reject(e); };
            audio.play().catch(reject);
        });
    },

    /**
     * Fetch TTS and play it using streaming.
     * Points an <audio> element at a GET endpoint so the browser
     * handles buffered streaming playback — audio starts as soon as
     * enough data arrives, before the full file is downloaded.
     * @param {string} text - Text to speak
     * @returns {Promise<void>}
     */
    speak(text) {
        return new Promise((resolve, reject) => {
            const url = '/api/audio/tts?text=' + encodeURIComponent(text);
            const audio = new window.Audio(url);
            audio.onended = resolve;
            audio.onerror = (e) => reject(e);
            audio.play().catch(reject);
        });
    },
};
