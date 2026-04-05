/**
 * Timer utilities — countdown timers and formatting.
 */
const Timer = {
    _intervals: {},

    /**
     * Start a countdown timer.
     * @param {string} id - Unique timer ID
     * @param {number} seconds - Duration in seconds
     * @param {function} onTick - Called every second with (remaining, elapsed)
     * @param {function} onExpire - Called when timer reaches 0
     */
    start(id, seconds, onTick, onExpire) {
        this.stop(id);
        let remaining = seconds;
        let elapsed = 0;

        onTick(remaining, elapsed);

        this._intervals[id] = setInterval(() => {
            elapsed++;
            remaining--;
            onTick(remaining, elapsed);
            if (remaining <= 0) {
                this.stop(id);
                if (onExpire) onExpire();
            }
        }, 1000);
    },

    stop(id) {
        if (this._intervals[id]) {
            clearInterval(this._intervals[id]);
            delete this._intervals[id];
        }
    },

    stopAll() {
        Object.keys(this._intervals).forEach(id => this.stop(id));
    },

    /**
     * Format seconds as M:SS
     */
    format(seconds) {
        const s = Math.max(0, Math.floor(seconds));
        const m = Math.floor(s / 60);
        const sec = s % 60;
        return `${m}:${sec.toString().padStart(2, '0')}`;
    },
};
