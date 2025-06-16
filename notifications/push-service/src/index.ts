import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import { NotificationService } from './services/NotificationService';
import { DatabaseService } from './services/DatabaseService';
import { QueueService } from './services/QueueService';
import { AuthMiddleware } from './middleware/AuthMiddleware';
import { RateLimitMiddleware } from './middleware/RateLimitMiddleware';
import { ErrorHandler } from './middleware/ErrorHandler';
import { Logger } from './utils/Logger';
import { notificationRoutes } from './routes/notifications';
import { deviceRoutes } from './routes/devices';
import { webhookRoutes } from './routes/webhooks';

// Load environment variables
dotenv.config();

class PushNotificationServer {
    private app: express.Application;
    private port: number;
    private notificationService: NotificationService;
    private databaseService: DatabaseService;
    private queueService: QueueService;

    constructor() {
        this.app = express();
        this.port = parseInt(process.env.PORT || '3001', 10);
        this.setupServices();
        this.setupMiddleware();
        this.setupRoutes();
        this.setupErrorHandling();
    }

    private async setupServices(): Promise<void> {
        try {
            // Initialize database
            this.databaseService = new DatabaseService();
            await this.databaseService.connect();

            // Initialize queue service
            this.queueService = new QueueService();
            await this.queueService.connect();

            // Initialize notification service
            this.notificationService = new NotificationService(
                this.databaseService,
                this.queueService
            );
            await this.notificationService.initialize();

            Logger.info('All services initialized successfully');
        } catch (error) {
            Logger.error('Failed to initialize services:', error);
            process.exit(1);
        }
    }

    private setupMiddleware(): void {
        // Security middleware
        this.app.use(helmet());
        this.app.use(cors({
            origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
            credentials: true
        }));

        // Body parsing middleware
        this.app.use(express.json({ limit: '10mb' }));
        this.app.use(express.urlencoded({ extended: true }));

        // Rate limiting
        this.app.use(RateLimitMiddleware.createLimiter());

        // Request logging
        this.app.use((req, res, next) => {
            Logger.info(`${req.method} ${req.path}`, {
                ip: req.ip,
                userAgent: req.get('User-Agent')
            });
            next();
        });
    }

    private setupRoutes(): void {
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'ok',
                timestamp: new Date().toISOString(),
                uptime: process.uptime(),
                version: process.env.npm_package_version || '1.0.0'
            });
        });

        // API routes
        this.app.use('/api/notifications', AuthMiddleware.authenticate, notificationRoutes);
        this.app.use('/api/devices', AuthMiddleware.authenticate, deviceRoutes);
        this.app.use('/api/webhooks', webhookRoutes);

        // Admin routes (require admin role)
        this.app.use('/api/admin', AuthMiddleware.requireAdmin, (req, res) => {
            res.json({
                message: 'Admin routes - coming soon',
                stats: this.notificationService.getStats()
            });
        });
    }

    private setupErrorHandling(): void {
        // 404 handler
        this.app.use('*', (req, res) => {
            res.status(404).json({
                error: 'Route not found',
                method: req.method,
                path: req.originalUrl
            });
        });

        // Global error handler
        this.app.use(ErrorHandler.handle);
    }

    public async start(): Promise<void> {
        try {
            this.app.listen(this.port, () => {
                Logger.info(`Push notification service started on port ${this.port}`);
                Logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
            });

            // Graceful shutdown
            process.on('SIGTERM', () => this.shutdown());
            process.on('SIGINT', () => this.shutdown());

        } catch (error) {
            Logger.error('Failed to start server:', error);
            process.exit(1);
        }
    }

    private async shutdown(): Promise<void> {
        Logger.info('Shutting down push notification service...');

        try {
            await this.queueService.disconnect();
            await this.databaseService.disconnect();
            Logger.info('Graceful shutdown completed');
            process.exit(0);
        } catch (error) {
            Logger.error('Error during shutdown:', error);
            process.exit(1);
        }
    }
}

// Start the server
const server = new PushNotificationServer();
server.start().catch((error) => {
    Logger.error('Failed to start push notification service:', error);
    process.exit(1);
});

export default PushNotificationServer;