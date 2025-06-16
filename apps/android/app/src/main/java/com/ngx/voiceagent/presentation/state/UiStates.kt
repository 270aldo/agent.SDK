package com.ngx.voiceagent.presentation.state

import com.ngx.voiceagent.data.model.*

// MARK: - Main UI State
data class MainUiState(
    val isLoading: Boolean = false,
    val isAuthenticated: Boolean = false,
    val currentUser: User? = null,
    val error: String? = null,
    val isConnected: Boolean = true,
    val unreadNotificationCount: Int = 0,
    val deepLinkDestination: String? = null
)

// MARK: - Dashboard UI State
data class DashboardUiState(
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val stats: DashboardStats? = null,
    val recentConversations: List<Conversation> = emptyList(),
    val platformMetrics: List<PlatformMetrics> = emptyList(),
    val error: String? = null,
    val lastUpdated: Long = 0L
)

// MARK: - Conversations UI State
data class ConversationsUiState(
    val isLoading: Boolean = false,
    val isLoadingMore: Boolean = false,
    val conversations: List<Conversation> = emptyList(),
    val filters: ConversationFilters = ConversationFilters(),
    val currentPage: Int = 1,
    val totalPages: Int = 1,
    val hasNextPage: Boolean = false,
    val searchQuery: String = "",
    val selectedConversation: Conversation? = null,
    val error: String? = null
)

// MARK: - Conversation Detail UI State
data class ConversationDetailUiState(
    val isLoading: Boolean = false,
    val conversation: Conversation? = null,
    val messages: List<Message> = emptyList(),
    val isLoadingMessages: Boolean = false,
    val error: String? = null
)

// MARK: - Analytics UI State
data class AnalyticsUiState(
    val isLoading: Boolean = false,
    val metrics: ConversationMetrics? = null,
    val conversionFunnel: List<Map<String, Any>> = emptyList(),
    val selectedPeriod: AnalyticsPeriod = AnalyticsPeriod.WEEK,
    val selectedPlatforms: List<Platform> = emptyList(),
    val dateRange: DateRange? = null,
    val isExporting: Boolean = false,
    val error: String? = null
)

// MARK: - Agents UI State
data class AgentsUiState(
    val isLoading: Boolean = false,
    val agents: List<VoiceAgent> = emptyList(),
    val selectedAgent: VoiceAgent? = null,
    val isCreating: Boolean = false,
    val isUpdating: Boolean = false,
    val isDeleting: Boolean = false,
    val showCreateDialog: Boolean = false,
    val showEditDialog: Boolean = false,
    val showDeleteDialog: Boolean = false,
    val error: String? = null
)

// MARK: - Agent Detail UI State
data class AgentDetailUiState(
    val isLoading: Boolean = false,
    val agent: VoiceAgent? = null,
    val performance: Map<String, Any> = emptyMap(),
    val isUpdating: Boolean = false,
    val isToggling: Boolean = false,
    val error: String? = null
)

// MARK: - Notifications UI State
data class NotificationsUiState(
    val isLoading: Boolean = false,
    val notifications: List<AppNotification> = emptyList(),
    val unreadCount: Int = 0,
    val isMarkingAsRead: Boolean = false,
    val isDeleting: Boolean = false,
    val showUnreadOnly: Boolean = false,
    val error: String? = null
)

// MARK: - Settings UI State
data class SettingsUiState(
    val isLoading: Boolean = false,
    val settings: AppSettings? = null,
    val isSaving: Boolean = false,
    val error: String? = null,
    val successMessage: String? = null
)

// MARK: - Voice UI State
data class VoiceUiState(
    val isRecording: Boolean = false,
    val isPlaying: Boolean = false,
    val isProcessing: Boolean = false,
    val currentTranscription: String = "",
    val recordingDuration: Long = 0L,
    val hasRecordPermission: Boolean = false,
    val hasNotificationPermission: Boolean = false,
    val error: String? = null
)

// MARK: - Login UI State
data class LoginUiState(
    val isLoading: Boolean = false,
    val email: String = "",
    val password: String = "",
    val showPassword: Boolean = false,
    val rememberMe: Boolean = false,
    val error: String? = null,
    val emailError: String? = null,
    val passwordError: String? = null
) {
    val isFormValid: Boolean
        get() = email.isNotBlank() && 
                password.isNotBlank() && 
                emailError == null && 
                passwordError == null &&
                android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()
}

// MARK: - Search UI State
data class SearchUiState(
    val query: String = "",
    val isSearching: Boolean = false,
    val suggestions: List<String> = emptyList(),
    val recentSearches: List<String> = emptyList(),
    val results: SearchResults = SearchResults(),
    val error: String? = null
)

data class SearchResults(
    val conversations: List<Conversation> = emptyList(),
    val agents: List<VoiceAgent> = emptyList(),
    val notifications: List<AppNotification> = emptyList(),
    val totalResults: Int = 0
)

// MARK: - Connection Status
enum class ConnectionStatus(val displayName: String) {
    CONNECTED("Connected"),
    CONNECTING("Connecting..."),
    DISCONNECTED("Disconnected"),
    ERROR("Connection Error")
}

// MARK: - Loading States
sealed class LoadingState {
    object Idle : LoadingState()
    object Loading : LoadingState()
    data class Success<T>(val data: T) : LoadingState()
    data class Error(val message: String, val throwable: Throwable? = null) : LoadingState()
}

// MARK: - UI Events
sealed class UiEvent {
    object Refresh : UiEvent()
    object LoadMore : UiEvent()
    object Retry : UiEvent()
    data class ShowSnackbar(val message: String) : UiEvent()
    data class ShowDialog(val title: String, val message: String) : UiEvent()
    data class Navigate(val route: String) : UiEvent()
    data class NavigateUp(val result: Any? = null) : UiEvent()
}

// MARK: - Form Validation
data class ValidationResult(
    val isValid: Boolean,
    val errorMessage: String? = null
)

// MARK: - Pagination State
data class PaginationState(
    val currentPage: Int = 1,
    val totalPages: Int = 1,
    val hasNextPage: Boolean = false,
    val hasPreviousPage: Boolean = false,
    val isLoading: Boolean = false,
    val isLoadingMore: Boolean = false
)

// MARK: - Filter State
data class FilterState(
    val isFilterActive: Boolean = false,
    val activeFiltersCount: Int = 0,
    val availableFilters: Map<String, List<String>> = emptyMap()
)