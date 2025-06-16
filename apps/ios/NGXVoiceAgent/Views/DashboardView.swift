import SwiftUI
import Charts

struct DashboardView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var notificationManager: NotificationManager
    @State private var dashboardStats: DashboardStats?
    @State private var recentConversations: [Conversation] = []
    @State private var isRefreshing = false
    @State private var showingNotifications = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                LazyVStack(spacing: 20) {
                    // Header with refresh and notifications
                    HStack {
                        VStack(alignment: .leading) {
                            Text("Dashboard")
                                .font(.largeTitle)
                                .fontWeight(.bold)
                            
                            Text("Monitor your voice agents")
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                        }
                        
                        Spacer()
                        
                        HStack(spacing: 16) {
                            // Notifications Button
                            Button(action: { showingNotifications = true }) {
                                ZStack {
                                    Image(systemName: "bell")
                                        .font(.title2)
                                    
                                    if notificationManager.unreadCount > 0 {
                                        Text("\(notificationManager.unreadCount)")
                                            .font(.caption2)
                                            .foregroundColor(.white)
                                            .padding(4)
                                            .background(Color.red)
                                            .clipShape(Circle())
                                            .offset(x: 8, y: -8)
                                    }
                                }
                            }
                            
                            // Refresh Button
                            Button(action: refreshData) {
                                Image(systemName: "arrow.clockwise")
                                    .font(.title2)
                                    .rotationEffect(.degrees(isRefreshing ? 360 : 0))
                                    .animation(.linear(duration: 1).repeatWhileTrue(isRefreshing), value: isRefreshing)
                            }
                        }
                    }
                    .padding(.horizontal)
                    
                    // Stats Cards
                    if let stats = dashboardStats {
                        LazyVGrid(columns: [
                            GridItem(.flexible()),
                            GridItem(.flexible())
                        ], spacing: 16) {
                            StatCard(
                                title: "Conversations",
                                value: "\(stats.todayConversations)",
                                change: stats.trends.conversations,
                                icon: "message.circle",
                                color: .blue
                            )
                            
                            StatCard(
                                title: "Conversions",
                                value: "\(stats.todayConversions)",
                                change: stats.trends.conversions,
                                icon: "chart.line.uptrend.xyaxis",
                                color: .green
                            )
                            
                            StatCard(
                                title: "Active Agents",
                                value: "\(stats.activeAgents)",
                                change: 0,
                                icon: "mic.circle",
                                color: .purple
                            )
                            
                            StatCard(
                                title: "Revenue",
                                value: "$\(Int(stats.revenue))",
                                change: stats.trends.revenue,
                                icon: "dollarsign.circle",
                                color: .orange
                            )
                        }
                        .padding(.horizontal)
                    } else {
                        // Loading state for stats
                        LazyVGrid(columns: [
                            GridItem(.flexible()),
                            GridItem(.flexible())
                        ], spacing: 16) {
                            ForEach(0..<4, id: \.self) { _ in
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(Color.gray.opacity(0.3))
                                    .frame(height: 120)
                                    .shimmer()
                            }
                        }
                        .padding(.horizontal)
                    }
                    
                    // Connection Status
                    ConnectionStatusView()
                        .padding(.horizontal)
                    
                    // Quick Actions
                    QuickActionsView()
                        .padding(.horizontal)
                    
                    // Recent Conversations
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Text("Recent Conversations")
                                .font(.headline)
                                .fontWeight(.semibold)
                            
                            Spacer()
                            
                            NavigationLink("View All", destination: ConversationsView())
                                .font(.subheadline)
                                .foregroundColor(.blue)
                        }
                        .padding(.horizontal)
                        
                        if recentConversations.isEmpty {
                            VStack(spacing: 16) {
                                Image(systemName: "message.badge")
                                    .font(.system(size: 40))
                                    .foregroundColor(.gray)
                                
                                Text("No recent conversations")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 40)
                            .background(Color.gray.opacity(0.1))
                            .cornerRadius(12)
                            .padding(.horizontal)
                        } else {
                            ForEach(recentConversations.prefix(5)) { conversation in
                                ConversationRowView(conversation: conversation)
                                    .padding(.horizontal)
                            }
                        }
                    }
                    
                    Spacer(minLength: 100)
                }
            }
            .refreshable {
                await refreshDataAsync()
            }
            .navigationBarHidden(true)
            .sheet(isPresented: $showingNotifications) {
                NotificationsView()
            }
        }
        .onAppear {
            loadData()
        }
    }
    
    private func loadData() {
        Task {
            await loadDashboardStats()
            await loadRecentConversations()
        }
    }
    
    private func refreshData() {
        isRefreshing = true
        
        Task {
            await loadDashboardStats()
            await loadRecentConversations()
            
            await MainActor.run {
                isRefreshing = false
            }
        }
    }
    
    private func refreshDataAsync() async {
        await loadDashboardStats()
        await loadRecentConversations()
    }
    
    @MainActor
    private func loadDashboardStats() async {
        do {
            let stats = try await NetworkManager.shared.getDashboardStats()
                .singleOutput()
            self.dashboardStats = stats
            appState.dashboardStats = stats
        } catch {
            print("Failed to load dashboard stats: \(error)")
        }
    }
    
    @MainActor
    private func loadRecentConversations() async {
        do {
            let conversations = try await NetworkManager.shared.getRecentConversations(limit: 5)
                .singleOutput()
            self.recentConversations = conversations
        } catch {
            print("Failed to load recent conversations: \(error)")
        }
    }
}

// MARK: - Supporting Views

struct StatCard: View {
    let title: String
    let value: String
    let change: Double
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                
                Spacer()
                
                if change != 0 {
                    HStack(spacing: 4) {
                        Image(systemName: change > 0 ? "arrow.up" : "arrow.down")
                            .font(.caption)
                        Text("\(abs(change), specifier: "%.1f")%")
                            .font(.caption)
                    }
                    .foregroundColor(change > 0 ? .green : .red)
                }
            }
            
            VStack(alignment: .leading, spacing: 4) {
                Text(value)
                    .font(.title2)
                    .fontWeight(.bold)
                
                Text(title)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
    }
}

struct ConnectionStatusView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        HStack {
            Circle()
                .fill(appState.connectionStatus.color)
                .frame(width: 8, height: 8)
            
            Text(appState.connectionStatus.description)
                .font(.caption)
                .foregroundColor(.secondary)
            
            Spacer()
        }
        .padding()
        .background(Color.gray.opacity(0.1))
        .cornerRadius(8)
    }
}

struct QuickActionsView: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Quick Actions")
                .font(.headline)
                .fontWeight(.semibold)
            
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 12) {
                QuickActionButton(
                    title: "New Agent",
                    icon: "plus.circle",
                    color: .blue
                ) {
                    // Navigate to create agent
                }
                
                QuickActionButton(
                    title: "Live Chat",
                    icon: "message.badge.waveform",
                    color: .green
                ) {
                    // Navigate to live conversations
                }
                
                QuickActionButton(
                    title: "Analytics",
                    icon: "chart.bar",
                    color: .purple
                ) {
                    // Navigate to analytics
                }
                
                QuickActionButton(
                    title: "Settings",
                    icon: "gear",
                    color: .gray
                ) {
                    // Navigate to settings
                }
            }
        }
    }
}

struct QuickActionButton: View {
    let title: String
    let icon: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                
                Text(title)
                    .font(.caption)
                    .foregroundColor(.primary)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(Color.gray.opacity(0.1))
            .cornerRadius(12)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Extensions

extension Publisher where Output == DashboardStats, Failure == NetworkError {
    func singleOutput() async throws -> DashboardStats {
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

extension Publisher where Output == [Conversation], Failure == NetworkError {
    func singleOutput() async throws -> [Conversation] {
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

// MARK: - View Modifiers

extension View {
    func shimmer() -> some View {
        self.overlay(
            Rectangle()
                .fill(
                    LinearGradient(
                        colors: [.clear, .white.opacity(0.4), .clear],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                )
                .rotationEffect(.degrees(-70))
                .offset(x: -250)
                .animation(.linear(duration: 1.5).repeatForever(autoreverses: false), value: UUID())
        )
        .clipped()
    }
}

extension Animation {
    func repeatWhileTrue(_ condition: Bool) -> Animation {
        return condition ? self.repeatForever(autoreverses: false) : self
    }
}

#Preview {
    DashboardView()
        .environmentObject(AppState())
        .environmentObject(NotificationManager())
}