// AudioWorklet processor that captures raw audio samples
class RecorderProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this._recording = true;
        this.port.onmessage = (event) => {
            if (event.data === 'stop') {
                this._recording = false;
            }
        };
    }

    process(inputs, outputs, parameters) {
        const input = inputs[0];
        if (input && input.length > 0 && this._recording) {
            // Send a copy of the channel data to the main thread
            const channelData = input[0];
            this.port.postMessage(new Float32Array(channelData));
        }
        return this._recording;
    }
}

registerProcessor('recorder-processor', RecorderProcessor);
