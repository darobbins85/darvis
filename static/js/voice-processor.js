class VoiceProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.port.onmessage = (event) => {
            // Handle messages from main thread if needed
        };
    }

    process(inputs, outputs, parameters) {
        const input = inputs[0];
        if (input && input.length > 0) {
            const channelData = input[0];
            // Convert Float32 to Int16 PCM
            const pcmData = new Int16Array(channelData.length);
            for (let i = 0; i < channelData.length; i++) {
                const sample = Math.max(-1, Math.min(1, channelData[i]));
                pcmData[i] = Math.round(sample * 32767);
            }
            this.port.postMessage(pcmData);
        }
        return true;
    }
}
registerProcessor('voice-processor', VoiceProcessor);
