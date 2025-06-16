import SwiftUI
import UserNotifications

@main
struct NGXVoiceAgentApp: App {
    @StateObject private var appState = AppState()
    @StateObject private var authManager = AuthenticationManager()
    @StateObject private var voiceManager = VoiceManager()
    @StateObject private var notificationManager = NotificationManager()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .environmentObject(authManager)
                .environmentObject(voiceManager)
                .environmentObject(notificationManager)
                .onAppear {
                    setupApp()
                }
        }
    }
    
    private func setupApp() {
        // Configure app on launch
        requestNotificationPermissions()
        configureAudioSession()
        setupNetworking()
    }
    
    private func requestNotificationPermissions() {
        notificationManager.requestPermissions()
    }
    
    private func configureAudioSession() {
        voiceManager.configureAudioSession()
    }
    
    private func setupNetworking() {
        NetworkManager.shared.configure()
    }
}