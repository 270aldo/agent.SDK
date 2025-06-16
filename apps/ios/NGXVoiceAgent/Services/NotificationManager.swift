import Foundation
import UserNotifications
import SwiftUI
import Combine

@MainActor
class NotificationManager: NSObject, ObservableObject {
    @Published var permissionStatus: UNAuthorizationStatus = .notDetermined
    @Published var notifications: [AppNotification] = []
    @Published var unreadCount = 0
    @Published var isEnabled = true
    
    override init() {
        super.init()
        checkPermissionStatus()
        loadStoredNotifications()
    }
    
    // MARK: - Permission Management
    
    func requestPermissions() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .badge, .sound]) { [weak self] granted, error in
            DispatchQueue.main.async {
                if let error = error {
                    print("Notification permission error: \(error)")
                }
                self?.checkPermissionStatus()
            }
        }
    }
    
    func checkPermissionStatus() {
        UNUserNotificationCenter.current().getNotificationSettings { [weak self] settings in
            DispatchQueue.main.async {
                self?.permissionStatus = settings.authorizationStatus
                self?.isEnabled = settings.authorizationStatus == .authorized
            }
        }
    }
    
    // MARK: - Local Notifications
    
    func scheduleLocalNotification(
        title: String,
        body: String,
        identifier: String = UUID().uuidString,
        timeInterval: TimeInterval? = nil,
        userInfo: [AnyHashable: Any] = [:]
    ) {
        guard isEnabled else { return }
        
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        content.userInfo = userInfo
        
        let trigger: UNNotificationTrigger?
        if let timeInterval = timeInterval {
            trigger = UNTimeIntervalNotificationTrigger(timeInterval: timeInterval, repeats: false)
        } else {
            trigger = nil
        }
        
        let request = UNNotificationRequest(identifier: identifier, content: content, trigger: trigger)
        
        UNUserNotificationCenter.current().add(request) { error in
            if let error = error {
                print("Failed to schedule notification: \(error)")
            }
        }
    }
    
    func cancelNotification(identifier: String) {
        UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: [identifier])
    }
    
    func cancelAllNotifications() {
        UNUserNotificationCenter.current().removeAllPendingNotificationRequests()
    }
    
    // MARK: - In-App Notifications
    
    func addInAppNotification(_ notification: AppNotification) {
        notifications.insert(notification, at: 0)
        updateUnreadCount()
        saveNotifications()
        
        // Limit to 100 notifications
        if notifications.count > 100 {
            notifications.removeLast()
        }
    }
    
    func markAsRead(_ notificationId: String) {
        if let index = notifications.firstIndex(where: { $0.id == notificationId }) {
            notifications[index].isRead = true
            updateUnreadCount()
            saveNotifications()
        }
        
        // Also mark as read on server
        Task {
            do {
                try await NetworkManager.shared.markNotificationAsRead(id: notificationId)
                    .singleOutput()
            } catch {
                print("Failed to mark notification as read on server: \(error)")
            }
        }
    }
    
    func markAllAsRead() {
        for index in notifications.indices {
            notifications[index].isRead = true
        }
        updateUnreadCount()
        saveNotifications()
    }
    
    func removeNotification(_ notificationId: String) {
        notifications.removeAll { $0.id == notificationId }
        updateUnreadCount()
        saveNotifications()
    }
    
    func clearAllNotifications() {
        notifications.removeAll()
        updateUnreadCount()
        saveNotifications()
    }
    
    private func updateUnreadCount() {
        unreadCount = notifications.filter { !$0.isRead }.count
        updateAppBadge()
    }
    
    private func updateAppBadge() {
        UNUserNotificationCenter.current().setBadgeCount(unreadCount) { error in
            if let error = error {
                print("Failed to update app badge: \(error)")
            }
        }
    }
    
    // MARK: - Persistence
    
    private func saveNotifications() {
        do {
            let data = try JSONEncoder().encode(notifications)
            UserDefaults.standard.set(data, forKey: "stored_notifications")
        } catch {
            print("Failed to save notifications: \(error)")
        }
    }
    
    private func loadStoredNotifications() {
        guard let data = UserDefaults.standard.data(forKey: "stored_notifications") else { return }
        
        do {
            notifications = try JSONDecoder().decode([AppNotification].self, from: data)
            updateUnreadCount()
        } catch {
            print("Failed to load stored notifications: \(error)")
        }
    }
    
    // MARK: - Server Sync
    
    func syncWithServer() async {
        do {
            let serverNotifications = try await NetworkManager.shared.getNotifications()
                .singleOutput()
            
            // Merge server notifications with local ones
            mergeServerNotifications(serverNotifications)
        } catch {
            print("Failed to sync notifications with server: \(error)")
        }
    }
    
    private func mergeServerNotifications(_ serverNotifications: [AppNotification]) {
        let existingIds = Set(notifications.map { $0.id })
        let newNotifications = serverNotifications.filter { !existingIds.contains($0.id) }
        
        notifications.insert(contentsOf: newNotifications, at: 0)
        notifications.sort { $0.createdAt > $1.createdAt }
        
        updateUnreadCount()
        saveNotifications()
    }
    
    // MARK: - Predefined Notifications
    
    func notifyNewConversation(_ conversation: Conversation) {
        let notification = AppNotification(
            id: UUID().uuidString,
            title: "New Conversation",
            message: "A new conversation started on \(conversation.platform.displayName)",
            type: .info,
            isRead: false,
            createdAt: Date(),
            actionUrl: "conversation/\(conversation.id)"
        )
        
        addInAppNotification(notification)
        
        scheduleLocalNotification(
            title: notification.title,
            body: notification.message,
            userInfo: ["conversationId": conversation.id]
        )
    }
    
    func notifyHighQualityLead(_ conversation: Conversation) {
        let notification = AppNotification(
            id: UUID().uuidString,
            title: "High Quality Lead",
            message: "New \(conversation.leadQuality.displayName) lead with \(conversation.qualificationScore)% score",
            type: .success,
            isRead: false,
            createdAt: Date(),
            actionUrl: "conversation/\(conversation.id)"
        )
        
        addInAppNotification(notification)
        
        scheduleLocalNotification(
            title: notification.title,
            body: notification.message,
            userInfo: ["conversationId": conversation.id, "leadQuality": conversation.leadQuality.rawValue]
        )
    }
    
    func notifyConversationTransferred(_ conversation: Conversation) {
        let notification = AppNotification(
            id: UUID().uuidString,
            title: "Conversation Transferred",
            message: "A conversation was transferred to human agent",
            type: .warning,
            isRead: false,
            createdAt: Date(),
            actionUrl: "conversation/\(conversation.id)"
        )
        
        addInAppNotification(notification)
        
        scheduleLocalNotification(
            title: notification.title,
            body: notification.message,
            userInfo: ["conversationId": conversation.id, "transferred": true]
        )
    }
    
    func notifySystemAlert(title: String, message: String, type: AppNotification.NotificationType = .warning) {
        let notification = AppNotification(
            id: UUID().uuidString,
            title: title,
            message: message,
            type: type,
            isRead: false,
            createdAt: Date(),
            actionUrl: nil
        )
        
        addInAppNotification(notification)
        
        if type == .error || type == .warning {
            scheduleLocalNotification(
                title: title,
                body: message
            )
        }
    }
}

// MARK: - UNUserNotificationCenterDelegate

extension NotificationManager: UNUserNotificationCenterDelegate {
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        // Show notification even when app is in foreground
        completionHandler([.banner, .sound, .badge])
    }
    
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        // Handle notification tap
        let userInfo = response.notification.request.content.userInfo
        
        if let conversationId = userInfo["conversationId"] as? String {
            // Navigate to conversation detail
            NotificationCenter.default.post(
                name: .navigateToConversation,
                object: conversationId
            )
        }
        
        completionHandler()
    }
}

// MARK: - Extensions

extension Publisher where Output == [AppNotification], Failure == NetworkError {
    func singleOutput() async throws -> [AppNotification] {
        try await withCheckedThrowingContinuation { continuation in
            var cancellable: AnyCancellable?
            cancellable = self
                .first()
                .sink(
                    receiveCompletion: { completion in
                        cancellable?.cancel()
                        if case .failure(let error) = completion {
                            continuation.resume(throwing: error)
                        }
                    },
                    receiveValue: { value in
                        cancellable?.cancel()
                        continuation.resume(returning: value)
                    }
                )
        }
    }
}

extension Publisher where Output == EmptyResponse, Failure == NetworkError {
    func singleOutput() async throws -> EmptyResponse {
        try await withCheckedThrowingContinuation { continuation in
            var cancellable: AnyCancellable?
            cancellable = self
                .first()
                .sink(
                    receiveCompletion: { completion in
                        cancellable?.cancel()
                        if case .failure(let error) = completion {
                            continuation.resume(throwing: error)
                        }
                    },
                    receiveValue: { value in
                        cancellable?.cancel()
                        continuation.resume(returning: value)
                    }
                )
        }
    }
}

// MARK: - Notification Names

extension Notification.Name {
    static let navigateToConversation = Notification.Name("navigateToConversation")
}