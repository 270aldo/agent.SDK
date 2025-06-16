package com.ngx.voiceagent.data.network

import com.ngx.voiceagent.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    // MARK: - Authentication Endpoints
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>

    @POST("auth/refresh")
    suspend fun refreshToken(@Body request: RefreshTokenRequest): Response<RefreshTokenResponse>

    @GET("auth/verify")
    suspend fun verifyToken(): Response<User>

    @POST("auth/logout")
    suspend fun logout(): Response<Unit>

    // MARK: - Dashboard Endpoints
    @GET("dashboard/stats")
    suspend fun getDashboardStats(): Response<DashboardStats>

    @GET("conversations/recent")
    suspend fun getRecentConversations(
        @Query("limit") limit: Int = 10
    ): Response<List<Conversation>>

    @GET("dashboard/platform-metrics")
    suspend fun getPlatformMetrics(): Response<List<PlatformMetrics>>

    // MARK: - Conversations Endpoints
    @GET("conversations")
    suspend fun getConversations(
        @Query("platform") platform: String? = null,
        @Query("status") status: String? = null,
        @Query("sentiment") sentiment: String? = null,
        @Query("leadQuality") leadQuality: String? = null,
        @Query("search") search: String? = null,
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20,
        @Query("startDate") startDate: String? = null,
        @Query("endDate") endDate: String? = null
    ): Response<ConversationsResponse>

    @GET("conversations/{id}")
    suspend fun getConversation(@Path("id") id: String): Response<ConversationDetail>

    @GET("conversations/{id}/messages")
    suspend fun getMessages(
        @Path("id") conversationId: String,
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 50
    ): Response<List<Message>>

    @PATCH("conversations/{id}/status")
    suspend fun updateConversationStatus(
        @Path("id") id: String,
        @Body status: Map<String, String>
    ): Response<Conversation>

    // MARK: - Analytics Endpoints
    @GET("analytics/metrics")
    suspend fun getAnalyticsMetrics(
        @Query("period") period: String = "week",
        @Query("platform") platform: String? = null,
        @Query("startDate") startDate: String? = null,
        @Query("endDate") endDate: String? = null
    ): Response<ConversationMetrics>

    @GET("analytics/funnel")
    suspend fun getConversionFunnel(
        @Query("period") period: String = "week",
        @Query("platform") platform: String? = null
    ): Response<List<Map<String, Any>>>

    @GET("analytics/export")
    suspend fun exportAnalytics(
        @Query("format") format: String,
        @Query("period") period: String,
        @Query("platform") platform: String? = null
    ): Response<String>

    // MARK: - Agents Endpoints
    @GET("agents")
    suspend fun getAgents(): Response<List<VoiceAgent>>

    @GET("agents/{id}")
    suspend fun getAgent(@Path("id") id: String): Response<VoiceAgent>

    @POST("agents")
    suspend fun createAgent(@Body request: CreateAgentRequest): Response<VoiceAgent>

    @PUT("agents/{id}")
    suspend fun updateAgent(
        @Path("id") id: String,
        @Body request: UpdateAgentRequest
    ): Response<VoiceAgent>

    @DELETE("agents/{id}")
    suspend fun deleteAgent(@Path("id") id: String): Response<Unit>

    @PATCH("agents/{id}/toggle")
    suspend fun toggleAgent(@Path("id") id: String): Response<VoiceAgent>

    @GET("agents/{id}/performance")
    suspend fun getAgentPerformance(
        @Path("id") id: String,
        @Query("period") period: String = "week"
    ): Response<Map<String, Any>>

    // MARK: - Notifications Endpoints
    @GET("notifications")
    suspend fun getNotifications(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 50,
        @Query("unreadOnly") unreadOnly: Boolean = false
    ): Response<List<AppNotification>>

    @PATCH("notifications/{id}/read")
    suspend fun markNotificationAsRead(@Path("id") id: String): Response<Unit>

    @PATCH("notifications/read-all")
    suspend fun markAllNotificationsAsRead(): Response<Unit>

    @DELETE("notifications/{id}")
    suspend fun deleteNotification(@Path("id") id: String): Response<Unit>

    @DELETE("notifications")
    suspend fun deleteAllNotifications(): Response<Unit>

    // MARK: - Settings Endpoints
    @GET("settings")
    suspend fun getSettings(): Response<AppSettings>

    @PUT("settings")
    suspend fun updateSettings(@Body settings: AppSettings): Response<AppSettings>

    @GET("settings/integrations")
    suspend fun getIntegrations(): Response<IntegrationSettings>

    @PUT("settings/integrations")
    suspend fun updateIntegrations(@Body integrations: IntegrationSettings): Response<IntegrationSettings>

    // MARK: - Voice Endpoints
    @Multipart
    @POST("voice/transcribe")
    suspend fun transcribeAudio(
        @Part("audio") audio: okhttp3.RequestBody,
        @Part("language") language: okhttp3.RequestBody? = null
    ): Response<Map<String, String>>

    @POST("voice/synthesize")
    suspend fun synthesizeText(
        @Body request: Map<String, String>
    ): Response<okhttp3.ResponseBody>

    // MARK: - Health Check
    @GET("health")
    suspend fun healthCheck(): Response<Map<String, String>>

    @GET("version")
    suspend fun getVersion(): Response<Map<String, String>>
}