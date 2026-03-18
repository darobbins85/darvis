class VoiceClient {
    constructor(socket) {
        this.socket = socket;
        this.audioContext = null;
        this.mediaStream = null;
        this.processor = null;
        this.isRecording = false;
        
        // Silence detection
        this.silenceThreshold = 0.01;
        this.silenceDuration = 1.5; // seconds
        this.silentChunks = 0;
        this.chunkDuration = 0.125; // 4096 samples / 32768 Hz ≈ 0.125s
        
        // TTS playback
        this.ttsAudioContext = null;
        this.audioQueue = [];
        this.isPlaying = false;
        
        // Status callbacks
        this.onStatusChange = null;
    }

    setStatusCallback(callback) {
        this.onStatusChange = callback;
    }

    updateStatus(status) {
        if (this.onStatusChange) {
            this.onStatusChange(status);
        }
    }

    // Analyze audio for silence detection
    analyzeAudioLevel(int16Data) {
        let sum = 0;
        for (let i = 0; i < int16Data.length; i++) {
            sum += Math.abs(int16Data[i]) / 32767;
        }
        return sum / int16Data.length;
    }

    async startRecording() {
        try {
            this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.audioContext = new AudioContext();
            const source = this.audioContext.createMediaStreamSource(this.mediaStream);
            
            // Load AudioWorklet
            await this.audioContext.audioWorklet.addModule('/static/js/voice-processor.js');
            
            this.processor = new AudioWorkletNode(this.audioContext, 'voice-processor');
            
            // Reset silence detection
            this.silentChunks = 0;
            
            // Send audio data to server with silence detection
            this.processor.port.onmessage = (event) => {
                if (this.isRecording) {
                    const audioLevel = this.analyzeAudioLevel(event.data);
                    
                    if (audioLevel < this.silenceThreshold) {
                        this.silentChunks++;
                        const silentTime = this.silentChunks * this.chunkDuration;
                        if (silentTime >= this.silenceDuration) {
                            // Stop after 1.5s of silence
                            this.stopRecording();
                            return;
                        }
                    } else {
                        this.silentChunks = 0;
                    }
                    
                    this.socket.emit('voice_data', { audio: event.data });
                }
            };
            
            source.connect(this.processor);
            this.processor.connect(this.audioContext.destination);
            
            this.isRecording = true;
            this.socket.emit('voice_start');
            this.updateStatus('listening');
            
        } catch (error) {
            console.error('Failed to start recording:', error);
        }
    }

    stopRecording() {
        if (this.isRecording) {
            this.isRecording = false;
            this.socket.emit('voice_end');
            
            if (this.mediaStream) {
                this.mediaStream.getTracks().forEach(track => track.stop());
            }
            if (this.audioContext) {
                this.audioContext.close();
            }
            
            this.updateStatus('processing');
        }
    }

    // TTS Playback
    initTTS() {
        this.ttsAudioContext = new AudioContext();
        
        this.socket.on('tts_start', () => {
            this.updateStatus('speaking');
        });
        
        this.socket.on('tts_audio', (data) => {
            this.playTTSChunk(data.audio);
        });
        
        this.socket.on('tts_end', () => {
            this.updateStatus('idle');
        });
    }

    playTTSChunk(base64Audio) {
        if (!this.ttsAudioContext) {
            this.initTTS();
        }
        
        // Decode base64
        const binaryString = atob(base64Audio);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        
        this.ttsAudioContext.decodeAudioData(bytes.buffer, (buffer) => {
            this.audioQueue.push(buffer);
            this.playNext();
        });
    }

    playNext() {
        if (this.isPlaying || this.audioQueue.length === 0) return;
        
        this.isPlaying = true;
        const buffer = this.audioQueue.shift();
        const source = this.ttsAudioContext.createBufferSource();
        source.buffer = buffer;
        source.connect(this.ttsAudioContext.destination);
        source.onended = () => {
            this.isPlaying = false;
            this.playNext();
        };
        source.start();
    }

    speak(text) {
        this.socket.emit('request_tts', { text: text });
    }
}

// Export for use in main app
window.VoiceClient = VoiceClient;
