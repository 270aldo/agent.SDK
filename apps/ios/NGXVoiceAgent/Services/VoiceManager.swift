import Foundation
import AVFoundation
import Speech
import SwiftUI
import Combine

@MainActor
class VoiceManager: NSObject, ObservableObject {
    @Published var isRecording = false
    @Published var isPlaying = false
    @Published var recordingPermissionStatus: AVAudioSession.RecordPermission = .undetermined
    @Published var speechRecognitionPermissionStatus: SFSpeechRecognizerAuthorizationStatus = .notDetermined
    @Published var currentTranscription = ""
    @Published var errorMessage: String?
    
    private var audioEngine: AVAudioEngine?
    private var speechRecognizer: SFSpeechRecognizer?
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private var audioPlayer: AVAudioPlayer?
    
    override init() {
        super.init()
        setupAudio()
    }
    
    private func setupAudio() {
        speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
        speechRecognizer?.delegate = self
        
        recordingPermissionStatus = AVAudioSession.sharedInstance().recordPermission
        speechRecognitionPermissionStatus = SFSpeechRecognizer.authorizationStatus()
    }
    
    func configureAudioSession() {
        do {
            let audioSession = AVAudioSession.sharedInstance()
            try audioSession.setCategory(.playAndRecord, mode: .voiceChat, options: [.defaultToSpeaker, .allowBluetooth])
            try audioSession.setActive(true)
        } catch {
            print("Failed to configure audio session: \(error)")
            errorMessage = "Failed to configure audio session"
        }
    }
    
    // MARK: - Permission Requests
    
    func requestRecordingPermission() async -> Bool {
        await withCheckedContinuation { continuation in
            AVAudioSession.sharedInstance().requestRecordPermission { granted in
                DispatchQueue.main.async {
                    self.recordingPermissionStatus = granted ? .granted : .denied
                    continuation.resume(returning: granted)
                }
            }
        }
    }
    
    func requestSpeechRecognitionPermission() async -> Bool {
        await withCheckedContinuation { continuation in
            SFSpeechRecognizer.requestAuthorization { status in
                DispatchQueue.main.async {
                    self.speechRecognitionPermissionStatus = status
                    continuation.resume(returning: status == .authorized)
                }
            }
        }
    }
    
    // MARK: - Recording Methods
    
    func startRecording() async throws {
        // Check permissions
        guard recordingPermissionStatus == .granted else {
            let granted = await requestRecordingPermission()
            if !granted {
                throw VoiceError.recordingPermissionDenied
            }
        }
        
        guard speechRecognitionPermissionStatus == .authorized else {
            let granted = await requestSpeechRecognitionPermission()
            if !granted {
                throw VoiceError.speechRecognitionPermissionDenied
            }
        }
        
        // Stop any existing recording
        if isRecording {
            stopRecording()
        }
        
        try startSpeechRecognition()
        isRecording = true
        currentTranscription = ""
        errorMessage = nil
    }
    
    func stopRecording() {
        audioEngine?.stop()
        recognitionRequest?.endAudio()
        recognitionTask?.cancel()
        
        audioEngine = nil
        recognitionRequest = nil
        recognitionTask = nil
        
        isRecording = false
    }
    
    private func startSpeechRecognition() throws {
        // Cancel any existing task
        recognitionTask?.cancel()
        recognitionTask = nil
        
        // Create audio engine and input node
        audioEngine = AVAudioEngine()
        guard let audioEngine = audioEngine else {
            throw VoiceError.audioEngineError
        }
        
        let inputNode = audioEngine.inputNode
        
        // Create recognition request
        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        guard let recognitionRequest = recognitionRequest else {
            throw VoiceError.speechRecognitionError
        }
        
        recognitionRequest.shouldReportPartialResults = true
        
        // Create recognition task
        recognitionTask = speechRecognizer?.recognitionTask(with: recognitionRequest) { [weak self] result, error in
            DispatchQueue.main.async {
                if let result = result {
                    self?.currentTranscription = result.bestTranscription.formattedString
                }
                
                if let error = error {
                    self?.errorMessage = error.localizedDescription
                    self?.stopRecording()
                }
            }
        }
        
        // Install tap on audio input
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
            recognitionRequest.append(buffer)
        }
        
        // Start audio engine
        audioEngine.prepare()
        try audioEngine.start()
    }
    
    // MARK: - Playback Methods
    
    func playAudio(data: Data) async throws {
        do {
            audioPlayer = try AVAudioPlayer(data: data)
            audioPlayer?.delegate = self
            
            isPlaying = true
            audioPlayer?.play()
        } catch {
            isPlaying = false
            throw VoiceError.playbackError(error)
        }
    }
    
    func playAudio(url: URL) async throws {
        do {
            audioPlayer = try AVAudioPlayer(contentsOf: url)
            audioPlayer?.delegate = self
            
            isPlaying = true
            audioPlayer?.play()
        } catch {
            isPlaying = false
            throw VoiceError.playbackError(error)
        }
    }
    
    func stopPlayback() {
        audioPlayer?.stop()
        audioPlayer = nil
        isPlaying = false
    }
    
    // MARK: - Text-to-Speech
    
    func synthesizeSpeech(text: String) async throws -> Data {
        // This would integrate with ElevenLabs or another TTS service
        // For now, we'll use iOS built-in TTS as fallback
        return try await withCheckedThrowingContinuation { continuation in
            let utterance = AVSpeechUtterance(string: text)
            utterance.rate = 0.5
            utterance.pitchMultiplier = 1.0
            utterance.volume = 1.0
            
            let synthesizer = AVSpeechSynthesizer()
            
            // This is a simplified implementation
            // In production, you would capture the audio output
            synthesizer.speak(utterance)
            
            // Return empty data for now
            continuation.resume(returning: Data())
        }
    }
    
    // MARK: - Utility Methods
    
    var hasPermissions: Bool {
        return recordingPermissionStatus == .granted && speechRecognitionPermissionStatus == .authorized
    }
    
    func checkPermissions() async -> Bool {
        let recordingGranted = await requestRecordingPermission()
        let speechGranted = await requestSpeechRecognitionPermission()
        return recordingGranted && speechGranted
    }
}

// MARK: - SFSpeechRecognizerDelegate

extension VoiceManager: SFSpeechRecognizerDelegate {
    func speechRecognizer(_ speechRecognizer: SFSpeechRecognizer, availabilityDidChange available: Bool) {
        DispatchQueue.main.async {
            if !available {
                self.errorMessage = "Speech recognition not available"
                self.stopRecording()
            }
        }
    }
}

// MARK: - AVAudioPlayerDelegate

extension VoiceManager: AVAudioPlayerDelegate {
    func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        DispatchQueue.main.async {
            self.isPlaying = false
            self.audioPlayer = nil
        }
    }
    
    func audioPlayerDecodeErrorDidOccur(_ player: AVAudioPlayer, error: Error?) {
        DispatchQueue.main.async {
            self.isPlaying = false
            self.audioPlayer = nil
            self.errorMessage = error?.localizedDescription ?? "Audio playback error"
        }
    }
}

// MARK: - Voice Error Enum

enum VoiceError: Error, LocalizedError {
    case recordingPermissionDenied
    case speechRecognitionPermissionDenied
    case audioEngineError
    case speechRecognitionError
    case playbackError(Error)
    case synthesisError(Error)
    
    var errorDescription: String? {
        switch self {
        case .recordingPermissionDenied:
            return "Recording permission denied. Please enable microphone access in Settings."
        case .speechRecognitionPermissionDenied:
            return "Speech recognition permission denied. Please enable speech recognition in Settings."
        case .audioEngineError:
            return "Audio engine could not be initialized"
        case .speechRecognitionError:
            return "Speech recognition failed"
        case .playbackError(let error):
            return "Audio playback failed: \(error.localizedDescription)"
        case .synthesisError(let error):
            return "Speech synthesis failed: \(error.localizedDescription)"
        }
    }
}