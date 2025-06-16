package com.ngx.voiceagent.data.model

import android.os.Parcelable
import kotlinx.parcelize.Parcelize
import java.util.Date

// MARK: - User Models
@Parcelize
data class User(
    val id: String,
    val email: String,
    val name: String,
    val role: UserRole,
    val avatar: String? = null,
    val createdAt: Date,
    val lastLoginAt: Date? = null
) : Parcelable

enum class UserRole(val displayName: String) {
    ADMIN("Administrator"),
    OPERATOR("Operator"),
    VIEWER("Viewer")
}

// MARK: - Authentication Models
data class LoginRequest(
    val email: String,
    val password: String
)

data class LoginResponse(
    val user: User,
    val token: String
)

data class RefreshTokenRequest(
    val token: String
)

data class RefreshTokenResponse(
    val user: User,
    val token: String
)

// MARK: - Conversation Models
@Parcelize
data class Conversation(
    val id: String,
    val userId: String? = null,
    val platform: Platform,
    val status: ConversationStatus,
    val startedAt: Date,
    val endedAt: Date? = null,
    val duration: Long? = null,
    val messagesCount: Int,
    val sentiment: Sentiment,
    val qualificationScore: Int,
    val conversionProbability: Double,
    val transferredToHuman: Boolean,
    val leadQuality: LeadQuality,
    val lastMessage: String? = null,
    val metadata: ConversationMetadata
) : Parcelable

enum class Platform(val displayName: String, val iconRes: String) {
    LEAD_MAGNET("Lead Magnet", "ic_magnet"),
    LANDING_PAGE("Landing Page", "ic_web"),
    BLOG("Blog Widget", "ic_article"),
    MOBILE_APP("Mobile App", "ic_phone_android")
}

enum class ConversationStatus(val displayName: String) {
    ACTIVE("Active"),
    COMPLETED("Completed"),
    TRANSFERRED("Transferred"),
    ABANDONED("Abandoned")
}

enum class Sentiment(val displayName: String, val colorRes: String) {
    POSITIVE("Positive", "green"),
    NEUTRAL("Neutral", "gray"),
    NEGATIVE("Negative", "red")
}

enum class LeadQuality(val displayName: String, val colorRes: String) {
    HOT("Hot", "red"),
    WARM("Warm", "orange"),
    COLD("Cold", "blue"),
    UNQUALIFIED("Unqualified", "gray")
}

@Parcelize
data class ConversationMetadata(
    val userAgent: String? = null,
    val location: String? = null,
    val referrer: String? = null,
    val sessionId: String
) : Parcelable

// MARK: - Message Models
@Parcelize
data class Message(
    val id: String,
    val conversationId: String,
    val type: MessageType,
    val content: String,
    val timestamp: Date,
    val metadata: MessageMetadata? = null
) : Parcelable

enum class MessageType(val displayName: String) {
    USER("User"),
    AGENT("Agent"),
    SYSTEM("System")
}

@Parcelize
data class MessageMetadata(
    val intent: String? = null,
    val sentiment: Double? = null,
    val confidence: Double? = null
) : Parcelable

// MARK: - Analytics Models
data class DashboardStats(
    val todayConversations: Int,
    val todayConversions: Int,
    val activeAgents: Int,
    val revenue: Double,
    val trends: StatsTrends
)

data class StatsTrends(
    val conversations: Double,
    val conversions: Double,
    val revenue: Double
)

data class ConversationMetrics(
    val totalConversations: Int,
    val activeConversations: Int,
    val completedConversations: Int,
    val averageDuration: Long,
    val conversionRate: Double,
    val transferRate: Double,
    val satisfactionScore: Double,
    val trends: TrendData
)

data class TrendData(
    val period: String,
    val data: List<DataPoint>
)

data class DataPoint(
    val date: String,
    val conversations: Int,
    val conversions: Int,
    val avgDuration: Long
)

data class PlatformMetrics(
    val platform: String,
    val conversations: Int,
    val conversions: Int,
    val avgDuration: Long,
    val conversionRate: Double,
    val revenue: Double? = null
)

// MARK: - Agent Models
@Parcelize
data class VoiceAgent(
    val id: String,
    val name: String,
    val platform: Platform,
    val isActive: Boolean,
    val personality: AgentPersonality,
    val triggers: AgentTriggers,
    val ui: AgentUI,
    val behavior: AgentBehavior,
    val qualificationCriteria: QualificationCriteria
) : Parcelable

@Parcelize
data class AgentPersonality(
    val tone: Tone,
    val style: Style,
    val expertise: List<String>
) : Parcelable

enum class Tone(val displayName: String) {
    PROFESSIONAL("Professional"),
    FRIENDLY("Friendly"),
    CASUAL("Casual"),
    ENTHUSIASTIC("Enthusiastic")
}

enum class Style(val displayName: String) {
    CONSULTATIVE("Consultative"),
    DIRECT("Direct"),
    EDUCATIONAL("Educational"),
    NURTURING("Nurturing")
}

@Parcelize
data class AgentTriggers(
    val type: TriggerType,
    val threshold: Int? = null
) : Parcelable

enum class TriggerType(val displayName: String) {
    AUTO("Auto"),
    SCROLL("Scroll"),
    TIME("Time"),
    EXIT_INTENT("Exit Intent"),
    MANUAL("Manual")
}

@Parcelize
data class AgentUI(
    val position: UIPosition,
    val size: UISize,
    val theme: UITheme,
    val brandColors: BrandColors? = null
) : Parcelable

enum class UIPosition(val displayName: String) {
    BOTTOM_RIGHT("Bottom Right"),
    BOTTOM_LEFT("Bottom Left"),
    CENTER("Center"),
    FULLSCREEN("Fullscreen")
}

enum class UISize(val displayName: String) {
    SMALL("Small"),
    MEDIUM("Medium"),
    LARGE("Large")
}

enum class UITheme(val displayName: String) {
    LIGHT("Light"),
    DARK("Dark"),
    AUTO("Auto")
}

@Parcelize
data class BrandColors(
    val primary: String,
    val secondary: String,
    val accent: String
) : Parcelable

@Parcelize
data class AgentBehavior(
    val autoStart: Boolean,
    val enableVoice: Boolean,
    val enableTransfer: Boolean,
    val maxDuration: Long,
    val followUpEnabled: Boolean
) : Parcelable

@Parcelize
data class QualificationCriteria(
    val minEngagementTime: Long,
    val requiredFields: List<String>,
    val scoringWeights: Map<String, Double>
) : Parcelable

// MARK: - Notification Models
@Parcelize
data class AppNotification(
    val id: String,
    val title: String,
    val message: String,
    val type: NotificationType,
    val isRead: Boolean,
    val createdAt: Date,
    val actionUrl: String? = null
) : Parcelable

enum class NotificationType(
    val displayName: String,
    val iconRes: String,
    val colorRes: String
) {
    INFO("Info", "ic_info", "blue"),
    SUCCESS("Success", "ic_check_circle", "green"),
    WARNING("Warning", "ic_warning", "orange"),
    ERROR("Error", "ic_error", "red")
}

// MARK: - API Response Models
data class ApiResponse<T>(
    val success: Boolean,
    val data: T? = null,
    val message: String? = null,
    val error: String? = null
)

data class PaginatedResponse<T>(
    val data: List<T>,
    val total: Int,
    val page: Int,
    val limit: Int,
    val pages: Int
)

data class ConversationsResponse(
    val conversations: List<Conversation>,
    val total: Int,
    val page: Int,
    val limit: Int
)

data class ConversationDetail(
    val conversation: Conversation,
    val messages: List<Message>
)

// MARK: - Request Models
data class CreateAgentRequest(
    val name: String,
    val platform: Platform,
    val personality: AgentPersonality,
    val triggers: AgentTriggers,
    val ui: AgentUI,
    val behavior: AgentBehavior,
    val qualificationCriteria: QualificationCriteria
)

data class UpdateAgentRequest(
    val name: String? = null,
    val isActive: Boolean? = null,
    val personality: AgentPersonality? = null,
    val triggers: AgentTriggers? = null,
    val ui: AgentUI? = null,
    val behavior: AgentBehavior? = null,
    val qualificationCriteria: QualificationCriteria? = null
)

// MARK: - Filter Models
data class ConversationFilters(
    val platform: List<Platform>? = null,
    val status: List<ConversationStatus>? = null,
    val sentiment: List<Sentiment>? = null,
    val leadQuality: List<LeadQuality>? = null,
    val dateRange: DateRange? = null,
    val search: String? = null
)

data class DateRange(
    val start: Date,
    val end: Date
)

data class AnalyticsFilters(
    val period: AnalyticsPeriod,
    val platform: List<Platform>? = null,
    val dateRange: DateRange? = null
)

enum class AnalyticsPeriod(val displayName: String, val value: String) {
    TODAY("Today", "today"),
    WEEK("This Week", "week"),
    MONTH("This Month", "month"),
    QUARTER("This Quarter", "quarter"),
    YEAR("This Year", "year"),
    CUSTOM("Custom", "custom")
}

// MARK: - Settings Models
data class AppSettings(
    val notifications: NotificationSettings,
    val analytics: AnalyticsSettings,
    val security: SecuritySettings,
    val integrations: IntegrationSettings
)

data class NotificationSettings(
    val email: Boolean,
    val push: Boolean,
    val sms: Boolean,
    val webhook: Boolean
)

data class AnalyticsSettings(
    val retentionPeriod: Int,
    val enableRealTime: Boolean,
    val exportFormat: ExportFormat
)

enum class ExportFormat(val displayName: String, val extension: String) {
    JSON("JSON", "json"),
    CSV("CSV", "csv"),
    XLSX("Excel", "xlsx")
}

data class SecuritySettings(
    val sessionTimeout: Int,
    val mfaEnabled: Boolean,
    val ipWhitelist: List<String>
)

data class IntegrationSettings(
    val crm: IntegrationConfig,
    val email: IntegrationConfig,
    val sms: IntegrationConfig
)

data class IntegrationConfig(
    val enabled: Boolean,
    val provider: String? = null,
    val apiKey: String? = null
)