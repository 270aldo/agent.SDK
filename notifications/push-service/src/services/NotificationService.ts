import admin from 'firebase-admin';
import apn from 'node-apn';
import webpush from 'web-push';
import { DatabaseService } from './DatabaseService';
import { QueueService } from './QueueService';
import { Logger } from '../utils/Logger';
import { 
    NotificationPayload, 
    DeviceToken, 
    NotificationResult,
    NotificationStats,
    PlatformType,
    NotificationTemplate
} from '../types';

export class NotificationService {
    private fcmApp: admin.app.App | null = null;
    private apnProvider: apn.Provider | null = null;
    private isInitialized = false;
    private stats: NotificationStats = {
        totalSent: 0,
        totalFailed: 0,
        sentByPlatform: {
            ios: 0,
            android: 0,
            web: 0
        },
        failedByPlatform: {
            ios: 0,
            android: 0,
            web: 0
        }
    };

    constructor(
        private databaseService: DatabaseService,
        private queueService: QueueService
    ) {}

    async initialize(): Promise<void> {
        try {
            await this.initializeFCM();
            await this.initializeAPNS();
            await this.initializeWebPush();
            
            this.isInitialized = true;
            Logger.info('NotificationService initialized successfully');
        } catch (error) {
            Logger.error('Failed to initialize NotificationService:', error);
            throw error;
        }
    }

    private async initializeFCM(): Promise<void> {
        if (!process.env.FIREBASE_SERVICE_ACCOUNT_PATH) {
            Logger.warn('Firebase service account not configured');
            return;
        }

        try {
            const serviceAccount = require(process.env.FIREBASE_SERVICE_ACCOUNT_PATH);
            
            this.fcmApp = admin.initializeApp({
                credential: admin.credential.cert(serviceAccount),
                projectId: serviceAccount.project_id
            });

            Logger.info('Firebase Admin SDK initialized');
        } catch (error) {
            Logger.error('Failed to initialize Firebase:', error);
            throw error;
        }
    }

    private async initializeAPNS(): Promise<void> {
        if (!process.env.APNS_KEY_PATH || !process.env.APNS_KEY_ID || !process.env.APNS_TEAM_ID) {
            Logger.warn('APNS configuration not complete');
            return;
        }

        try {
            this.apnProvider = new apn.Provider({
                token: {
                    key: process.env.APNS_KEY_PATH,
                    keyId: process.env.APNS_KEY_ID,
                    teamId: process.env.APNS_TEAM_ID
                },
                production: process.env.NODE_ENV === 'production'
            });

            Logger.info('APNS provider initialized');
        } catch (error) {
            Logger.error('Failed to initialize APNS:', error);
            throw error;
        }
    }

    private async initializeWebPush(): Promise<void> {
        if (!process.env.VAPID_PUBLIC_KEY || !process.env.VAPID_PRIVATE_KEY) {
            Logger.warn('Web Push VAPID keys not configured');
            return;
        }

        try {
            webpush.setVapidDetails(
                process.env.VAPID_SUBJECT || 'mailto:admin@ngx.com',
                process.env.VAPID_PUBLIC_KEY,
                process.env.VAPID_PRIVATE_KEY
            );

            Logger.info('Web Push initialized');
        } catch (error) {
            Logger.error('Failed to initialize Web Push:', error);
            throw error;
        }
    }

    async sendNotification(
        payload: NotificationPayload,
        targetTokens?: string[]
    ): Promise<NotificationResult> {
        if (!this.isInitialized) {
            throw new Error('NotificationService not initialized');
        }

        const result: NotificationResult = {
            success: [],
            failed: [],
            totalSent: 0,
            totalFailed: 0
        };

        try {
            // Get target devices
            const devices = targetTokens 
                ? await this.getDevicesByTokens(targetTokens)
                : await this.getDevicesForUser(payload.userId);

            if (devices.length === 0) {
                Logger.warn(`No devices found for notification: ${payload.id}`);
                return result;
            }

            // Group devices by platform
            const devicesByPlatform = this.groupDevicesByPlatform(devices);

            // Send to each platform
            const promises = [];

            if (devicesByPlatform.ios.length > 0) {
                promises.push(this.sendToIOS(payload, devicesByPlatform.ios));
            }

            if (devicesByPlatform.android.length > 0) {
                promises.push(this.sendToAndroid(payload, devicesByPlatform.android));
            }

            if (devicesByPlatform.web.length > 0) {
                promises.push(this.sendToWeb(payload, devicesByPlatform.web));
            }

            // Wait for all platforms to complete
            const platformResults = await Promise.allSettled(promises);

            // Combine results
            platformResults.forEach((platformResult) => {
                if (platformResult.status === 'fulfilled') {
                    result.success.push(...platformResult.value.success);
                    result.failed.push(...platformResult.value.failed);
                } else {
                    Logger.error('Platform notification failed:', platformResult.reason);
                }
            });

            result.totalSent = result.success.length;
            result.totalFailed = result.failed.length;

            // Update stats
            this.updateStats(result);

            // Log notification attempt
            await this.logNotification(payload, result);

            Logger.info(`Notification sent: ${result.totalSent} success, ${result.totalFailed} failed`);

            return result;

        } catch (error) {
            Logger.error('Failed to send notification:', error);
            throw error;
        }
    }

    private async sendToIOS(
        payload: NotificationPayload,
        devices: DeviceToken[]
    ): Promise<NotificationResult> {
        if (!this.apnProvider) {
            throw new Error('APNS not initialized');
        }

        const result: NotificationResult = {
            success: [],
            failed: [],
            totalSent: 0,
            totalFailed: 0
        };

        try {
            const notification = new apn.Notification();
            notification.expiry = Math.floor(Date.now() / 1000) + 3600; // 1 hour
            notification.badge = payload.badge || 1;
            notification.sound = payload.sound || 'ping.aiff';
            notification.alert = {
                title: payload.title,
                body: payload.body
            };
            notification.payload = {
                notificationId: payload.id,
                ...payload.data
            };
            notification.topic = process.env.IOS_BUNDLE_ID || 'com.ngx.voiceagent';

            const tokens = devices.map(device => device.token);
            const apnResult = await this.apnProvider.send(notification, tokens);

            // Process results
            apnResult.sent.forEach((token, index) => {
                result.success.push({
                    token: token.device,
                    platform: 'ios' as PlatformType,
                    messageId: `apns-${Date.now()}-${index}`
                });
            });

            apnResult.failed.forEach((failure) => {
                result.failed.push({
                    token: failure.device,
                    platform: 'ios' as PlatformType,
                    error: failure.error?.message || 'Unknown APNS error'
                });
            });

            result.totalSent = result.success.length;
            result.totalFailed = result.failed.length;

            this.stats.sentByPlatform.ios += result.totalSent;
            this.stats.failedByPlatform.ios += result.totalFailed;

            return result;

        } catch (error) {
            Logger.error('iOS notification failed:', error);
            throw error;
        }
    }

    private async sendToAndroid(
        payload: NotificationPayload,
        devices: DeviceToken[]
    ): Promise<NotificationResult> {
        if (!this.fcmApp) {
            throw new Error('FCM not initialized');
        }

        const result: NotificationResult = {
            success: [],
            failed: [],
            totalSent: 0,
            totalFailed: 0
        };

        try {
            const message = {
                notification: {
                    title: payload.title,
                    body: payload.body,
                    imageUrl: payload.image
                },
                data: {
                    notificationId: payload.id,
                    ...Object.fromEntries(
                        Object.entries(payload.data || {}).map(([key, value]) => [
                            key,
                            typeof value === 'string' ? value : JSON.stringify(value)
                        ])
                    )
                },
                android: {
                    notification: {
                        icon: 'ic_notification',
                        color: '#3B82F6',
                        sound: payload.sound || 'default',
                        channelId: payload.channelId || 'default'
                    },
                    priority: 'high' as const
                },
                tokens: devices.map(device => device.token)
            };

            const fcmResult = await admin.messaging(this.fcmApp).sendMulticast(message);

            // Process results
            fcmResult.responses.forEach((response, index) => {
                const token = devices[index].token;
                
                if (response.success) {
                    result.success.push({
                        token,
                        platform: 'android' as PlatformType,
                        messageId: response.messageId || `fcm-${Date.now()}-${index}`
                    });
                } else {
                    result.failed.push({
                        token,
                        platform: 'android' as PlatformType,
                        error: response.error?.message || 'Unknown FCM error'
                    });
                }
            });

            result.totalSent = fcmResult.successCount;
            result.totalFailed = fcmResult.failureCount;

            this.stats.sentByPlatform.android += result.totalSent;
            this.stats.failedByPlatform.android += result.totalFailed;

            return result;

        } catch (error) {
            Logger.error('Android notification failed:', error);
            throw error;
        }
    }

    private async sendToWeb(
        payload: NotificationPayload,
        devices: DeviceToken[]
    ): Promise<NotificationResult> {
        const result: NotificationResult = {
            success: [],
            failed: [],
            totalSent: 0,
            totalFailed: 0
        };

        try {
            const webPayload = JSON.stringify({
                title: payload.title,
                body: payload.body,
                icon: payload.image || '/icons/icon-192x192.png',
                badge: '/icons/badge-72x72.png',
                data: {
                    notificationId: payload.id,
                    ...payload.data
                },
                actions: payload.actions || []
            });

            const promises = devices.map(async (device, index) => {
                try {
                    const pushSubscription = JSON.parse(device.token);
                    await webpush.sendNotification(pushSubscription, webPayload);
                    
                    result.success.push({
                        token: device.token,
                        platform: 'web' as PlatformType,
                        messageId: `web-${Date.now()}-${index}`
                    });
                } catch (error: any) {
                    result.failed.push({
                        token: device.token,
                        platform: 'web' as PlatformType,
                        error: error.message || 'Unknown Web Push error'
                    });
                }
            });

            await Promise.allSettled(promises);

            result.totalSent = result.success.length;
            result.totalFailed = result.failed.length;

            this.stats.sentByPlatform.web += result.totalSent;
            this.stats.failedByPlatform.web += result.totalFailed;

            return result;

        } catch (error) {
            Logger.error('Web notification failed:', error);
            throw error;
        }
    }

    async sendBulkNotifications(
        notifications: NotificationPayload[]
    ): Promise<NotificationResult[]> {
        const results: NotificationResult[] = [];

        for (const notification of notifications) {
            try {
                const result = await this.sendNotification(notification);
                results.push(result);
            } catch (error) {
                Logger.error(`Failed to send notification ${notification.id}:`, error);
                results.push({
                    success: [],
                    failed: [],
                    totalSent: 0,
                    totalFailed: 1
                });
            }
        }

        return results;
    }

    async sendTemplateNotification(
        templateId: string,
        data: Record<string, any>,
        targetTokens?: string[]
    ): Promise<NotificationResult> {
        const template = await this.getNotificationTemplate(templateId);
        if (!template) {
            throw new Error(`Template not found: ${templateId}`);
        }

        const payload: NotificationPayload = {
            id: `template-${templateId}-${Date.now()}`,
            title: this.renderTemplate(template.title, data),
            body: this.renderTemplate(template.body, data),
            data: { ...template.data, ...data },
            image: template.image,
            sound: template.sound,
            badge: template.badge,
            channelId: template.channelId,
            actions: template.actions,
            userId: data.userId
        };

        return this.sendNotification(payload, targetTokens);
    }

    private renderTemplate(template: string, data: Record<string, any>): string {
        return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
            return data[key] || match;
        });
    }

    private async getDevicesForUser(userId: string): Promise<DeviceToken[]> {
        return this.databaseService.getDeviceTokensForUser(userId);
    }

    private async getDevicesByTokens(tokens: string[]): Promise<DeviceToken[]> {
        return this.databaseService.getDevicesByTokens(tokens);
    }

    private groupDevicesByPlatform(devices: DeviceToken[]): {
        ios: DeviceToken[];
        android: DeviceToken[];
        web: DeviceToken[];
    } {
        return devices.reduce((acc, device) => {
            acc[device.platform].push(device);
            return acc;
        }, {
            ios: [] as DeviceToken[],
            android: [] as DeviceToken[],
            web: [] as DeviceToken[]
        });
    }

    private updateStats(result: NotificationResult): void {
        this.stats.totalSent += result.totalSent;
        this.stats.totalFailed += result.totalFailed;
    }

    private async logNotification(
        payload: NotificationPayload,
        result: NotificationResult
    ): Promise<void> {
        try {
            await this.databaseService.logNotification({
                id: payload.id,
                title: payload.title,
                body: payload.body,
                userId: payload.userId,
                totalSent: result.totalSent,
                totalFailed: result.totalFailed,
                sentAt: new Date(),
                data: payload.data
            });
        } catch (error) {
            Logger.error('Failed to log notification:', error);
        }
    }

    private async getNotificationTemplate(templateId: string): Promise<NotificationTemplate | null> {
        return this.databaseService.getNotificationTemplate(templateId);
    }

    public getStats(): NotificationStats {
        return { ...this.stats };
    }

    public async queueNotification(payload: NotificationPayload, delay?: number): Promise<void> {
        await this.queueService.addNotificationJob(payload, delay);
    }

    public async scheduleNotification(
        payload: NotificationPayload,
        scheduledAt: Date
    ): Promise<void> {
        const delay = scheduledAt.getTime() - Date.now();
        if (delay > 0) {
            await this.queueNotification(payload, delay);
        } else {
            await this.sendNotification(payload);
        }
    }
}