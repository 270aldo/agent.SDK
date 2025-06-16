export type PlatformType = 'ios' | 'android' | 'web';

export interface NotificationPayload {
    id: string;
    title: string;
    body: string;
    userId?: string;
    data?: Record<string, any>;
    image?: string;
    sound?: string;
    badge?: number;
    channelId?: string;
    actions?: NotificationAction[];
    priority?: 'high' | 'normal' | 'low';
    ttl?: number; // Time to live in seconds
    collapseKey?: string;
    tags?: string[];
}

export interface NotificationAction {
    action: string;
    title: string;
    icon?: string;
    url?: string;
}

export interface DeviceToken {
    id: string;
    userId: string;
    token: string;
    platform: PlatformType;
    isActive: boolean;
    createdAt: Date;
    updatedAt: Date;
    metadata?: {
        appVersion?: string;
        osVersion?: string;
        deviceModel?: string;
        timeZone?: string;
        language?: string;
    };
}

export interface NotificationResult {
    success: Array<{
        token: string;
        platform: PlatformType;
        messageId: string;
    }>;
    failed: Array<{
        token: string;
        platform: PlatformType;
        error: string;
    }>;
    totalSent: number;
    totalFailed: number;
}

export interface NotificationStats {
    totalSent: number;
    totalFailed: number;
    sentByPlatform: Record<PlatformType, number>;
    failedByPlatform: Record<PlatformType, number>;
}

export interface NotificationTemplate {
    id: string;
    name: string;
    title: string;
    body: string;
    data?: Record<string, any>;
    image?: string;
    sound?: string;
    badge?: number;
    channelId?: string;
    actions?: NotificationAction[];
    isActive: boolean;
    createdAt: Date;
    updatedAt: Date;
}

export interface NotificationLog {
    id: string;
    title: string;
    body: string;
    userId?: string;
    totalSent: number;
    totalFailed: number;
    sentAt: Date;
    data?: Record<string, any>;
}

export interface PushSubscription {
    endpoint: string;
    keys: {
        p256dh: string;
        auth: string;
    };
}

export interface BulkNotificationRequest {
    notifications: NotificationPayload[];
    sendImmediately?: boolean;
    batchSize?: number;
    delayBetweenBatches?: number;
}

export interface TemplateNotificationRequest {
    templateId: string;
    data: Record<string, any>;
    targetTokens?: string[];
    targetUsers?: string[];
    scheduledAt?: string;
}

export interface DeviceRegistrationRequest {
    token: string;
    platform: PlatformType;
    userId: string;
    metadata?: {
        appVersion?: string;
        osVersion?: string;
        deviceModel?: string;
        timeZone?: string;
        language?: string;
    };
}

export interface NotificationChannel {
    id: string;
    name: string;
    description: string;
    importance: 'high' | 'default' | 'low' | 'min';
    sound?: string;
    vibration?: boolean;
    lightColor?: string;
    lockscreenVisibility?: 'public' | 'private' | 'secret';
}

export interface NotificationPreferences {
    userId: string;
    enablePush: boolean;
    enableEmail: boolean;
    enableSMS: boolean;
    quietHours?: {
        start: string; // HH:mm format
        end: string;   // HH:mm format
        timeZone: string;
    };
    categories: {
        [category: string]: {
            enabled: boolean;
            channels: PlatformType[];
        };
    };
}

export interface NotificationCategory {
    id: string;
    name: string;
    description: string;
    defaultEnabled: boolean;
    allowOptOut: boolean;
}

// Webhook types
export interface WebhookPayload {
    event: string;
    data: any;
    timestamp: string;
    signature?: string;
}

export interface WebhookEndpoint {
    id: string;
    url: string;
    events: string[];
    isActive: boolean;
    secret?: string;
    retryCount: number;
    lastSuccessAt?: Date;
    lastFailureAt?: Date;
    createdAt: Date;
}

// Queue job types
export interface NotificationJob {
    id: string;
    payload: NotificationPayload;
    attempts: number;
    maxAttempts: number;
    delay?: number;
    priority: number;
    createdAt: Date;
    processedAt?: Date;
    failedAt?: Date;
    error?: string;
}

// Analytics types
export interface NotificationAnalytics {
    period: {
        start: Date;
        end: Date;
    };
    totalSent: number;
    totalDelivered: number;
    totalOpened: number;
    totalClicked: number;
    deliveryRate: number;
    openRate: number;
    clickRate: number;
    byPlatform: Record<PlatformType, {
        sent: number;
        delivered: number;
        opened: number;
        clicked: number;
    }>;
    byCategory: Record<string, {
        sent: number;
        delivered: number;
        opened: number;
        clicked: number;
    }>;
    topFailureReasons: Array<{
        reason: string;
        count: number;
    }>;
}

// Error types
export class NotificationError extends Error {
    constructor(
        message: string,
        public code: string,
        public platform?: PlatformType,
        public token?: string
    ) {
        super(message);
        this.name = 'NotificationError';
    }
}

export class RateLimitError extends Error {
    constructor(
        message: string,
        public retryAfter: number
    ) {
        super(message);
        this.name = 'RateLimitError';
    }
}

// Configuration types
export interface ServiceConfig {
    port: number;
    database: {
        host: string;
        port: number;
        database: string;
        username: string;
        password: string;
        ssl?: boolean;
    };
    redis: {
        host: string;
        port: number;
        password?: string;
        db?: number;
    };
    firebase: {
        serviceAccountPath?: string;
        projectId?: string;
    };
    apns: {
        keyPath?: string;
        keyId?: string;
        teamId?: string;
        bundleId?: string;
        production?: boolean;
    };
    webPush: {
        vapidPublicKey?: string;
        vapidPrivateKey?: string;
        vapidSubject?: string;
    };
    rateLimit: {
        windowMs: number;
        maxRequests: number;
    };
    webhooks: {
        enabled: boolean;
        retryAttempts: number;
        retryDelay: number;
    };
}