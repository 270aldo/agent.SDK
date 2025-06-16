import Foundation
import SwiftUI

@MainActor
class AppState: ObservableObject {
    @Published var isLoading = false
    @Published var currentUser: User?
    @Published var activeConversations: [Conversation] = []
    @Published var notifications: [AppNotification] = []
    @Published var dashboardStats: DashboardStats?
    @Published var selectedConversation: Conversation?
    @Published var connectionStatus: ConnectionStatus = .disconnected
    
    // Settings
    @Published var enableNotifications = true
    @Published var enableVoiceRecording = true
    @Published var autoStartConversations = false
    @Published var preferredLanguage = "en"
    
    enum ConnectionStatus {
        case connected
        case connecting
        case disconnected
        case error
        
        var description: String {
            switch self {
            case .connected:
                return "Connected"
            case .connecting:
                return "Connecting..."
            case .disconnected:
                return "Disconnected"
            case .error:
                return "Connection Error"
            }
        }
        
        var color: Color {
            switch self {
            case .connected:
                return .green
            case .connecting:
                return .orange
            case .disconnected:
                return .gray
            case .error:
                return .red
            }
        }
    }
    
    init() {
        loadSettings()
    }
    
    func loadSettings() {
        // Load user preferences from UserDefaults
        enableNotifications = UserDefaults.standard.bool(forKey: "enableNotifications")
        enableVoiceRecording = UserDefaults.standard.bool(forKey: "enableVoiceRecording")
        autoStartConversations = UserDefaults.standard.bool(forKey: "autoStartConversations")
        preferredLanguage = UserDefaults.standard.string(forKey: "preferredLanguage") ?? "en"
    }
    
    func saveSettings() {
        UserDefaults.standard.set(enableNotifications, forKey: "enableNotifications")
        UserDefaults.standard.set(enableVoiceRecording, forKey: "enableVoiceRecording")
        UserDefaults.standard.set(autoStartConversations, forKey: "autoStartConversations")
        UserDefaults.standard.set(preferredLanguage, forKey: "preferredLanguage")
    }
    
    func addNotification(_ notification: AppNotification) {
        notifications.insert(notification, at: 0)
        
        // Limit to last 50 notifications
        if notifications.count > 50 {
            notifications.removeLast()
        }
    }
    
    func markNotificationAsRead(_ id: String) {
        if let index = notifications.firstIndex(where: { $0.id == id }) {
            notifications[index].isRead = true
        }
    }
    
    func clearAllNotifications() {
        notifications.removeAll()
    }
    
    var unreadNotificationsCount: Int {
        notifications.filter { !$0.isRead }.count
    }
}