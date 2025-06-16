import { VoiceConfig } from '../types';

export class VoiceManager {
  private config: VoiceConfig;
  private currentAudio?: HTMLAudioElement;
  private enabled: boolean;

  constructor(config: VoiceConfig) {
    this.config = {
      enabled: true,
      autoPlay: true,
      speed: 1.0,
      volume: 1.0,
      ...config
    };
    this.enabled = this.config.enabled || false;
  }

  async playAudio(audioUrl: string): Promise<void> {
    if (!this.enabled) {
      return;
    }

    try {
      // Stop current audio if playing
      this.stopAudio();

      // Create new audio element
      this.currentAudio = new Audio(audioUrl);
      this.currentAudio.volume = this.config.volume || 1.0;
      this.currentAudio.playbackRate = this.config.speed || 1.0;

      // Play audio
      await this.currentAudio.play();

      return new Promise((resolve, reject) => {
        if (!this.currentAudio) {
          reject(new Error('Audio element not available'));
          return;
        }

        this.currentAudio.onended = () => resolve();
        this.currentAudio.onerror = () => reject(new Error('Audio playback failed'));
      });
    } catch (error) {
      console.error('Failed to play audio:', error);
      throw error;
    }
  }

  stopAudio(): void {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.currentAudio = undefined;
    }
  }

  setEnabled(enabled: boolean): void {
    this.enabled = enabled;
    if (!enabled) {
      this.stopAudio();
    }
  }

  setVolume(volume: number): void {
    this.config.volume = Math.max(0, Math.min(1, volume));
    if (this.currentAudio) {
      this.currentAudio.volume = this.config.volume;
    }
  }

  setSpeed(speed: number): void {
    this.config.speed = Math.max(0.5, Math.min(2, speed));
    if (this.currentAudio) {
      this.currentAudio.playbackRate = this.config.speed;
    }
  }

  isPlaying(): boolean {
    return this.currentAudio ? !this.currentAudio.paused : false;
  }

  destroy(): void {
    this.stopAudio();
    this.enabled = false;
  }
}