package com.ngx.voiceagent

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build
import androidx.core.content.ContextCompat
import androidx.hilt.work.HiltWorkerFactory
import androidx.work.Configuration
import dagger.hilt.android.HiltAndroidApp
import javax.inject.Inject

@HiltAndroidApp
class NGXVoiceApplication : Application(), Configuration.Provider {

    @Inject
    lateinit var workerFactory: HiltWorkerFactory

    override fun onCreate() {
        super.onCreate()
        createNotificationChannels()
    }

    override fun getWorkManagerConfiguration(): Configuration {
        return Configuration.Builder()
            .setWorkerFactory(workerFactory)
            .build()
    }

    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val notificationManager = ContextCompat.getSystemService(
                this,
                NotificationManager::class.java
            ) as NotificationManager

            // General notifications channel
            val generalChannel = NotificationChannel(
                CHANNEL_GENERAL,
                "General Notifications",
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = "General app notifications"
                enableVibration(true)
                setShowBadge(true)
            }

            // High priority notifications (alerts, emergencies)
            val alertChannel = NotificationChannel(
                CHANNEL_ALERTS,
                "Important Alerts",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Important system alerts and notifications"
                enableVibration(true)
                setShowBadge(true)
            }

            // Conversation notifications
            val conversationChannel = NotificationChannel(
                CHANNEL_CONVERSATIONS,
                "Conversations",
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = "New conversation notifications"
                enableVibration(true)
                setShowBadge(true)
            }

            // Voice processing service
            val serviceChannel = NotificationChannel(
                CHANNEL_SERVICE,
                "Voice Processing",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Voice processing service notifications"
                enableVibration(false)
                setShowBadge(false)
            }

            notificationManager.createNotificationChannels(
                listOf(generalChannel, alertChannel, conversationChannel, serviceChannel)
            )
        }
    }

    companion object {
        const val CHANNEL_GENERAL = "general_notifications"
        const val CHANNEL_ALERTS = "alert_notifications"
        const val CHANNEL_CONVERSATIONS = "conversation_notifications"
        const val CHANNEL_SERVICE = "service_notifications"
    }
}