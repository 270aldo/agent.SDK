import SwiftUI

struct ContentView: View {
    @EnvironmentObject var authManager: AuthenticationManager
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        Group {
            if authManager.isAuthenticated {
                MainTabView()
            } else {
                LoginView()
            }
        }
        .onAppear {
            authManager.checkAuthenticationStatus()
        }
    }
}

struct MainTabView: View {
    @EnvironmentObject var appState: AppState
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            DashboardView()
                .tabItem {
                    Image(systemName: "chart.bar.fill")
                    Text("Dashboard")
                }
                .tag(0)
            
            ConversationsView()
                .tabItem {
                    Image(systemName: "message.fill")
                    Text("Conversations")
                }
                .tag(1)
            
            AgentsView()
                .tabItem {
                    Image(systemName: "mic.fill")
                    Text("Agents")
                }
                .tag(2)
            
            AnalyticsView()
                .tabItem {
                    Image(systemName: "chart.line.uptrend.xyaxis")
                    Text("Analytics")
                }
                .tag(3)
            
            SettingsView()
                .tabItem {
                    Image(systemName: "gear")
                    Text("Settings")
                }
                .tag(4)
        }
        .accentColor(.blue)
        .onAppear {
            // Configure tab bar appearance
            let appearance = UITabBarAppearance()
            appearance.configureWithOpaqueBackground()
            appearance.backgroundColor = UIColor.systemBackground
            UITabBar.appearance().standardAppearance = appearance
            UITabBar.appearance().scrollEdgeAppearance = appearance
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(AuthenticationManager())
        .environmentObject(AppState())
        .environmentObject(VoiceManager())
        .environmentObject(NotificationManager())
}