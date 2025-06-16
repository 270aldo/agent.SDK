package com.ngx.voiceagent.presentation.navigation

import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.navArgument
import com.ngx.voiceagent.presentation.components.BottomNavigationBar
import com.ngx.voiceagent.presentation.components.LoadingScreen
import com.ngx.voiceagent.presentation.screens.analytics.AnalyticsScreen
import com.ngx.voiceagent.presentation.screens.agents.AgentDetailScreen
import com.ngx.voiceagent.presentation.screens.agents.AgentsScreen
import com.ngx.voiceagent.presentation.screens.agents.CreateAgentScreen
import com.ngx.voiceagent.presentation.screens.conversations.ConversationDetailScreen
import com.ngx.voiceagent.presentation.screens.conversations.ConversationsScreen
import com.ngx.voiceagent.presentation.screens.dashboard.DashboardScreen
import com.ngx.voiceagent.presentation.screens.login.LoginScreen
import com.ngx.voiceagent.presentation.screens.notifications.NotificationsScreen
import com.ngx.voiceagent.presentation.screens.settings.SettingsScreen
import com.ngx.voiceagent.presentation.viewmodel.MainViewModel

@Composable
fun NGXNavHost(
    navController: NavHostController,
    isAuthenticated: Boolean,
    isLoading: Boolean,
    modifier: Modifier = Modifier,
    mainViewModel: MainViewModel = hiltViewModel()
) {
    if (isLoading) {
        LoadingScreen()
        return
    }

    if (isAuthenticated) {
        AuthenticatedNavHost(
            navController = navController,
            modifier = modifier
        )
    } else {
        UnauthenticatedNavHost(
            navController = navController,
            modifier = modifier
        )
    }
}

@Composable
private fun AuthenticatedNavHost(
    navController: NavHostController,
    modifier: Modifier = Modifier
) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    val bottomNavRoutes = listOf(
        Screen.Dashboard.route,
        Screen.Conversations.route,
        Screen.Analytics.route,
        Screen.Agents.route,
        Screen.Settings.route
    )

    val showBottomNav = currentRoute in bottomNavRoutes

    Scaffold(
        bottomBar = {
            if (showBottomNav) {
                BottomNavigationBar(
                    navController = navController,
                    currentRoute = currentRoute
                )
            }
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = Screen.Dashboard.route,
            modifier = modifier.padding(paddingValues),
            enterTransition = {
                slideInHorizontally(
                    initialOffsetX = { 1000 },
                    animationSpec = tween(300)
                ) + fadeIn(animationSpec = tween(300))
            },
            exitTransition = {
                slideOutHorizontally(
                    targetOffsetX = { -1000 },
                    animationSpec = tween(300)
                ) + fadeOut(animationSpec = tween(300))
            },
            popEnterTransition = {
                slideInHorizontally(
                    initialOffsetX = { -1000 },
                    animationSpec = tween(300)
                ) + fadeIn(animationSpec = tween(300))
            },
            popExitTransition = {
                slideOutHorizontally(
                    targetOffsetX = { 1000 },
                    animationSpec = tween(300)
                ) + fadeOut(animationSpec = tween(300))
            }
        ) {
            // Dashboard
            composable(Screen.Dashboard.route) {
                DashboardScreen(
                    onNavigateToConversations = {
                        navController.navigate(Screen.Conversations.route)
                    },
                    onNavigateToAgents = {
                        navController.navigate(Screen.Agents.route)
                    },
                    onNavigateToAnalytics = {
                        navController.navigate(Screen.Analytics.route)
                    },
                    onNavigateToNotifications = {
                        navController.navigate(Screen.Notifications.route)
                    },
                    onConversationClick = { conversationId ->
                        navController.navigate(Screen.ConversationDetail.createRoute(conversationId))
                    }
                )
            }

            // Conversations
            composable(Screen.Conversations.route) {
                ConversationsScreen(
                    onConversationClick = { conversationId ->
                        navController.navigate(Screen.ConversationDetail.createRoute(conversationId))
                    },
                    onNavigateBack = {
                        navController.popBackStack()
                    }
                )
            }

            // Conversation Detail
            composable(
                route = Screen.ConversationDetail.route,
                arguments = listOf(
                    navArgument("conversationId") { type = NavType.StringType }
                )
            ) { backStackEntry ->
                val conversationId = backStackEntry.arguments?.getString("conversationId") ?: ""
                ConversationDetailScreen(
                    conversationId = conversationId,
                    onNavigateBack = {
                        navController.popBackStack()
                    }
                )
            }

            // Analytics
            composable(Screen.Analytics.route) {
                AnalyticsScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    }
                )
            }

            // Agents
            composable(Screen.Agents.route) {
                AgentsScreen(
                    onAgentClick = { agentId ->
                        navController.navigate(Screen.AgentDetail.createRoute(agentId))
                    },
                    onCreateAgentClick = {
                        navController.navigate(Screen.CreateAgent.route)
                    },
                    onNavigateBack = {
                        navController.popBackStack()
                    }
                )
            }

            // Agent Detail
            composable(
                route = Screen.AgentDetail.route,
                arguments = listOf(
                    navArgument("agentId") { type = NavType.StringType }
                )
            ) { backStackEntry ->
                val agentId = backStackEntry.arguments?.getString("agentId") ?: ""
                AgentDetailScreen(
                    agentId = agentId,
                    onNavigateBack = {
                        navController.popBackStack()
                    },
                    onEditAgent = {
                        // Navigate to edit screen (can reuse CreateAgentScreen with edit mode)
                    }
                )
            }

            // Create Agent
            composable(Screen.CreateAgent.route) {
                CreateAgentScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    },
                    onAgentCreated = {
                        navController.popBackStack()
                    }
                )
            }

            // Notifications
            composable(Screen.Notifications.route) {
                NotificationsScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    },
                    onNotificationClick = { notification ->
                        notification.actionUrl?.let { url ->
                            // Handle notification action navigation
                            when {
                                url.contains("conversation/") -> {
                                    val conversationId = url.substringAfterLast("/")
                                    navController.navigate(Screen.ConversationDetail.createRoute(conversationId))
                                }
                                url.contains("agent/") -> {
                                    val agentId = url.substringAfterLast("/")
                                    navController.navigate(Screen.AgentDetail.createRoute(agentId))
                                }
                            }
                        }
                    }
                )
            }

            // Settings
            composable(Screen.Settings.route) {
                SettingsScreen(
                    onNavigateBack = {
                        navController.popBackStack()
                    }
                )
            }
        }
    }
}

@Composable
private fun UnauthenticatedNavHost(
    navController: NavHostController,
    modifier: Modifier = Modifier
) {
    NavHost(
        navController = navController,
        startDestination = Screen.Login.route,
        modifier = modifier,
        enterTransition = {
            fadeIn(animationSpec = tween(300))
        },
        exitTransition = {
            fadeOut(animationSpec = tween(300))
        }
    ) {
        composable(Screen.Login.route) {
            LoginScreen()
        }
    }
}

// Screen definitions
sealed class Screen(val route: String, val title: String) {
    object Login : Screen("login", "Login")
    object Dashboard : Screen("dashboard", "Dashboard")
    object Conversations : Screen("conversations", "Conversations")
    object ConversationDetail : Screen("conversation/{conversationId}", "Conversation") {
        fun createRoute(conversationId: String) = "conversation/$conversationId"
    }
    object Analytics : Screen("analytics", "Analytics")
    object Agents : Screen("agents", "Agents")
    object AgentDetail : Screen("agent/{agentId}", "Agent") {
        fun createRoute(agentId: String) = "agent/$agentId"
    }
    object CreateAgent : Screen("create_agent", "Create Agent")
    object Notifications : Screen("notifications", "Notifications")
    object Settings : Screen("settings", "Settings")
}