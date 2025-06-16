import { Router } from 'express';
import { body, param, query, validationResult } from 'express-validator';
import { NotificationService } from '../services/NotificationService';
import { DatabaseService } from '../services/DatabaseService';
import { Logger } from '../utils/Logger';
import { 
    NotificationPayload, 
    BulkNotificationRequest, 
    TemplateNotificationRequest 
} from '../types';

const router = Router();

// Validation middleware
const validateRequest = (req: any, res: any, next: any) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({
            error: 'Validation failed',
            details: errors.array()
        });
    }
    next();
};

// Send single notification
router.post(
    '/send',
    [
        body('title').notEmpty().withMessage('Title is required'),
        body('body').notEmpty().withMessage('Body is required'),
        body('userId').optional().isString(),
        body('targetTokens').optional().isArray(),
        body('data').optional().isObject(),
        body('priority').optional().isIn(['high', 'normal', 'low']),
        body('scheduledAt').optional().isISO8601(),
        validateRequest
    ],
    async (req, res) => {
        try {
            const notificationService = req.app.locals.notificationService as NotificationService;
            
            const payload: NotificationPayload = {
                id: `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                title: req.body.title,
                body: req.body.body,
                userId: req.body.userId,
                data: req.body.data || {},
                image: req.body.image,
                sound: req.body.sound,
                badge: req.body.badge,
                channelId: req.body.channelId,
                actions: req.body.actions,
                priority: req.body.priority || 'normal',
                ttl: req.body.ttl,
                collapseKey: req.body.collapseKey,
                tags: req.body.tags
            };

            let result;

            if (req.body.scheduledAt) {
                const scheduledAt = new Date(req.body.scheduledAt);
                await notificationService.scheduleNotification(payload, scheduledAt);
                result = { scheduled: true, scheduledAt };
            } else {
                result = await notificationService.sendNotification(
                    payload, 
                    req.body.targetTokens
                );
            }

            res.json({
                success: true,
                notificationId: payload.id,
                result
            });

        } catch (error: any) {
            Logger.error('Failed to send notification:', error);
            res.status(500).json({
                error: 'Failed to send notification',
                message: error.message
            });
        }
    }
);

// Send bulk notifications
router.post(
    '/send-bulk',
    [
        body('notifications').isArray().withMessage('Notifications must be an array'),
        body('notifications.*.title').notEmpty().withMessage('Title is required for all notifications'),
        body('notifications.*.body').notEmpty().withMessage('Body is required for all notifications'),
        body('batchSize').optional().isInt({ min: 1, max: 100 }),
        body('delayBetweenBatches').optional().isInt({ min: 0 }),
        validateRequest
    ],
    async (req, res) => {
        try {
            const notificationService = req.app.locals.notificationService as NotificationService;
            const request: BulkNotificationRequest = req.body;

            const notifications: NotificationPayload[] = request.notifications.map((notif, index) => ({
                id: `bulk-${Date.now()}-${index}`,
                title: notif.title,
                body: notif.body,
                userId: notif.userId,
                data: notif.data || {},
                image: notif.image,
                sound: notif.sound,
                badge: notif.badge,
                channelId: notif.channelId,
                actions: notif.actions,
                priority: notif.priority || 'normal'
            }));

            if (request.sendImmediately) {
                const results = await notificationService.sendBulkNotifications(notifications);
                res.json({
                    success: true,
                    totalNotifications: notifications.length,
                    results
                });
            } else {
                // Queue all notifications
                for (const notification of notifications) {
                    await notificationService.queueNotification(notification);
                }
                
                res.json({
                    success: true,
                    totalNotifications: notifications.length,
                    queued: true
                });
            }

        } catch (error: any) {
            Logger.error('Failed to send bulk notifications:', error);
            res.status(500).json({
                error: 'Failed to send bulk notifications',
                message: error.message
            });
        }
    }
);

// Send template notification
router.post(
    '/send-template',
    [
        body('templateId').notEmpty().withMessage('Template ID is required'),
        body('data').isObject().withMessage('Data must be an object'),
        body('targetTokens').optional().isArray(),
        body('targetUsers').optional().isArray(),
        body('scheduledAt').optional().isISO8601(),
        validateRequest
    ],
    async (req, res) => {
        try {
            const notificationService = req.app.locals.notificationService as NotificationService;
            const request: TemplateNotificationRequest = req.body;

            const result = await notificationService.sendTemplateNotification(
                request.templateId,
                request.data,
                request.targetTokens
            );

            res.json({
                success: true,
                templateId: request.templateId,
                result
            });

        } catch (error: any) {
            Logger.error('Failed to send template notification:', error);
            res.status(500).json({
                error: 'Failed to send template notification',
                message: error.message
            });
        }
    }
);

// Get notification history
router.get(
    '/history',
    [
        query('userId').optional().isString(),
        query('limit').optional().isInt({ min: 1, max: 100 }),
        query('offset').optional().isInt({ min: 0 }),
        query('startDate').optional().isISO8601(),
        query('endDate').optional().isISO8601(),
        validateRequest
    ],
    async (req, res) => {
        try {
            const databaseService = req.app.locals.databaseService as DatabaseService;
            
            const filters = {
                userId: req.query.userId as string,
                limit: parseInt(req.query.limit as string) || 50,
                offset: parseInt(req.query.offset as string) || 0,
                startDate: req.query.startDate ? new Date(req.query.startDate as string) : undefined,
                endDate: req.query.endDate ? new Date(req.query.endDate as string) : undefined
            };

            const history = await databaseService.getNotificationHistory(filters);

            res.json({
                success: true,
                history,
                pagination: {
                    limit: filters.limit,
                    offset: filters.offset,
                    total: history.length
                }
            });

        } catch (error: any) {
            Logger.error('Failed to get notification history:', error);
            res.status(500).json({
                error: 'Failed to get notification history',
                message: error.message
            });
        }
    }
);

// Get notification statistics
router.get('/stats', async (req, res) => {
    try {
        const notificationService = req.app.locals.notificationService as NotificationService;
        const databaseService = req.app.locals.databaseService as DatabaseService;

        const serviceStats = notificationService.getStats();
        const dbStats = await databaseService.getNotificationStats();

        res.json({
            success: true,
            stats: {
                ...serviceStats,
                ...dbStats
            }
        });

    } catch (error: any) {
        Logger.error('Failed to get notification stats:', error);
        res.status(500).json({
            error: 'Failed to get notification stats',
            message: error.message
        });
    }
});

// Get notification by ID
router.get(
    '/:id',
    [
        param('id').notEmpty().withMessage('Notification ID is required'),
        validateRequest
    ],
    async (req, res) => {
        try {
            const databaseService = req.app.locals.databaseService as DatabaseService;
            const notification = await databaseService.getNotificationById(req.params.id);

            if (!notification) {
                return res.status(404).json({
                    error: 'Notification not found'
                });
            }

            res.json({
                success: true,
                notification
            });

        } catch (error: any) {
            Logger.error('Failed to get notification:', error);
            res.status(500).json({
                error: 'Failed to get notification',
                message: error.message
            });
        }
    }
);

// Cancel scheduled notification
router.delete(
    '/:id/cancel',
    [
        param('id').notEmpty().withMessage('Notification ID is required'),
        validateRequest
    ],
    async (req, res) => {
        try {
            const queueService = req.app.locals.queueService;
            const cancelled = await queueService.cancelJob(req.params.id);

            if (!cancelled) {
                return res.status(404).json({
                    error: 'Notification not found or already processed'
                });
            }

            res.json({
                success: true,
                message: 'Notification cancelled successfully'
            });

        } catch (error: any) {
            Logger.error('Failed to cancel notification:', error);
            res.status(500).json({
                error: 'Failed to cancel notification',
                message: error.message
            });
        }
    }
);

// Test notification (development only)
if (process.env.NODE_ENV === 'development') {
    router.post('/test', async (req, res) => {
        try {
            const notificationService = req.app.locals.notificationService as NotificationService;
            
            const testPayload: NotificationPayload = {
                id: `test-${Date.now()}`,
                title: 'Test Notification',
                body: 'This is a test notification from NGX Voice Agent',
                data: { test: true },
                priority: 'normal'
            };

            const result = await notificationService.sendNotification(testPayload, []);

            res.json({
                success: true,
                message: 'Test notification sent',
                result
            });

        } catch (error: any) {
            Logger.error('Failed to send test notification:', error);
            res.status(500).json({
                error: 'Failed to send test notification',
                message: error.message
            });
        }
    });
}

export { router as notificationRoutes };