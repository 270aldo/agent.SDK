import Foundation

// MARK: - User Models
struct User: Codable, Identifiable {
    let id: String
    let email: String
    let name: String
    let role: UserRole
    let avatar: String?
    let createdAt: Date
    let lastLoginAt: Date?
    
    enum UserRole: String, Codable, CaseIterable {
        case admin = "admin"
        case operator = "operator"
        case viewer = "viewer"
        
        var displayName: String {
            switch self {
            case .admin:
                return "Administrator"
            case .operator:
                return "Operator"
            case .viewer:
                return "Viewer"
            }
        }
    }
}

// MARK: - Conversation Models
struct Conversation: Codable, Identifiable {
    let id: String
    let userId: String?
    let platform: Platform
    let status: ConversationStatus
    let startedAt: Date
    let endedAt: Date?
    let duration: TimeInterval?
    let messagesCount: Int
    let sentiment: Sentiment
    let qualificationScore: Int
    let conversionProbability: Double
    let transferredToHuman: Bool
    let leadQuality: LeadQuality
    let lastMessage: String?
    let metadata: ConversationMetadata
    
    enum Platform: String, Codable, CaseIterable {
        case leadMagnet = "lead_magnet"
        case landingPage = "landing_page"
        case blog = "blog"
        case mobileApp = "mobile_app"
        
        var displayName: String {
            switch self {
            case .leadMagnet:
                return "Lead Magnet"
            case .landingPage:
                return "Landing Page"
            case .blog:
                return "Blog Widget"
            case .mobileApp:
                return "Mobile App"
            }
        }
        
        var icon: String {
            switch self {
            case .leadMagnet:
                return "magnet"
            case .landingPage:
                return "globe"
            case .blog:
                return "doc.text"
            case .mobileApp:
                return "iphone"
            }
        }
    }
    
    enum ConversationStatus: String, Codable, CaseIterable {
        case active = "active"
        case completed = "completed"
        case transferred = "transferred"
        case abandoned = "abandoned"
        
        var displayName: String {
            switch self {
            case .active:
                return "Active"
            case .completed:
                return "Completed"
            case .transferred:
                return "Transferred"
            case .abandoned:
                return "Abandoned"
            }
        }
    }
    
    enum Sentiment: String, Codable, CaseIterable {
        case positive = "positive"
        case neutral = "neutral"
        case negative = "negative"
        
        var displayName: String {
            switch self {
            case .positive:
                return "Positive"
            case .neutral:
                return "Neutral"
            case .negative:
                return "Negative"
            }
        }
        
        var color: String {
            switch self {
            case .positive:
                return "green"
            case .neutral:
                return "gray"
            case .negative:
                return "red"
            }
        }
    }
    
    enum LeadQuality: String, Codable, CaseIterable {
        case hot = "hot"
        case warm = "warm"
        case cold = "cold"
        case unqualified = "unqualified"
        
        var displayName: String {
            switch self {
            case .hot:
                return "Hot"
            case .warm:
                return "Warm"
            case .cold:
                return "Cold"
            case .unqualified:
                return "Unqualified"
            }
        }
        
        var color: String {
            switch self {
            case .hot:
                return "red"
            case .warm:
                return "orange"
            case .cold:
                return "blue"
            case .unqualified:
                return "gray"
            }
        }
    }
}

struct ConversationMetadata: Codable {
    let userAgent: String?
    let location: String?
    let referrer: String?
    let sessionId: String
}

// MARK: - Message Models
struct Message: Codable, Identifiable {
    let id: String
    let conversationId: String
    let type: MessageType
    let content: String
    let timestamp: Date
    let metadata: MessageMetadata?
    
    enum MessageType: String, Codable {
        case user = "user"
        case agent = "agent"
        case system = "system"
        
        var displayName: String {
            switch self {
            case .user:
                return "User"
            case .agent:
                return "Agent"
            case .system:
                return "System"
            }
        }
    }
}

struct MessageMetadata: Codable {
    let intent: String?
    let entities: [String: AnyCodable]?
    let sentiment: Double?
    let confidence: Double?
}

// MARK: - Analytics Models
struct DashboardStats: Codable {
    let todayConversations: Int
    let todayConversions: Int
    let activeAgents: Int
    let revenue: Double
    let trends: StatsTrends
}

struct StatsTrends: Codable {
    let conversations: Double
    let conversions: Double
    let revenue: Double
}

struct ConversationMetrics: Codable {
    let totalConversations: Int
    let activeConversations: Int
    let completedConversations: Int
    let averageDuration: TimeInterval
    let conversionRate: Double
    let transferRate: Double
    let satisfactionScore: Double
    let trends: TrendData
}

struct TrendData: Codable {
    let period: String
    let data: [DataPoint]
}

struct DataPoint: Codable {
    let date: String
    let conversations: Int
    let conversions: Int
    let avgDuration: TimeInterval
}

// MARK: - Agent Models
struct VoiceAgent: Codable, Identifiable {
    let id: String
    let name: String
    let platform: Conversation.Platform
    let isActive: Bool
    let personality: AgentPersonality
    let triggers: AgentTriggers
    let ui: AgentUI
    let behavior: AgentBehavior
    let qualificationCriteria: QualificationCriteria
}

struct AgentPersonality: Codable {
    let tone: Tone
    let style: Style
    let expertise: [String]
    
    enum Tone: String, Codable, CaseIterable {
        case professional = "professional"
        case friendly = "friendly"
        case casual = "casual"
        case enthusiastic = "enthusiastic"
    }
    
    enum Style: String, Codable, CaseIterable {
        case consultative = "consultative"
        case direct = "direct"
        case educational = "educational"
        case nurturing = "nurturing"
    }
}

struct AgentTriggers: Codable {
    let type: TriggerType
    let threshold: Int?
    let conditions: [String: AnyCodable]?
    
    enum TriggerType: String, Codable, CaseIterable {
        case auto = "auto"
        case scroll = "scroll"
        case time = "time"
        case exitIntent = "exit_intent"
        case manual = "manual"
    }
}

struct AgentUI: Codable {
    let position: UIPosition
    let size: UISize
    let theme: UITheme
    let brandColors: BrandColors?
    
    enum UIPosition: String, Codable, CaseIterable {
        case bottomRight = "bottom-right"
        case bottomLeft = "bottom-left"
        case center = "center"
        case fullscreen = "fullscreen"
    }
    
    enum UISize: String, Codable, CaseIterable {
        case small = "small"
        case medium = "medium"
        case large = "large"
    }
    
    enum UITheme: String, Codable, CaseIterable {
        case light = "light"
        case dark = "dark"
        case auto = "auto"
    }
}

struct BrandColors: Codable {
    let primary: String
    let secondary: String
    let accent: String
}

struct AgentBehavior: Codable {
    let autoStart: Bool
    let enableVoice: Bool
    let enableTransfer: Bool
    let maxDuration: TimeInterval
    let followUpEnabled: Bool
}

struct QualificationCriteria: Codable {
    let minEngagementTime: TimeInterval
    let requiredFields: [String]
    let scoringWeights: [String: Double]
}

// MARK: - Notification Models
struct AppNotification: Identifiable, Codable {
    let id: String
    let title: String
    let message: String
    let type: NotificationType
    var isRead: Bool
    let createdAt: Date
    let actionUrl: String?
    
    enum NotificationType: String, Codable {
        case info = "info"
        case success = "success"
        case warning = "warning"
        case error = "error"
        
        var icon: String {
            switch self {
            case .info:
                return "info.circle"
            case .success:
                return "checkmark.circle"
            case .warning:
                return "exclamationmark.triangle"
            case .error:
                return "xmark.circle"
            }
        }
        
        var color: String {
            switch self {
            case .info:
                return "blue"
            case .success:
                return "green"
            case .warning:
                return "orange"
            case .error:
                return "red"
            }
        }
    }
}

// MARK: - Helper Types
struct AnyCodable: Codable {
    let value: Any
    
    init(_ value: Any) {
        self.value = value
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        
        if let intValue = try? container.decode(Int.self) {
            value = intValue
        } else if let doubleValue = try? container.decode(Double.self) {
            value = doubleValue
        } else if let stringValue = try? container.decode(String.self) {
            value = stringValue
        } else if let boolValue = try? container.decode(Bool.self) {
            value = boolValue
        } else {
            throw DecodingError.typeMismatch(AnyCodable.self, DecodingError.Context(codingPath: decoder.codingPath, debugDescription: "Unsupported type"))
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        
        if let intValue = value as? Int {
            try container.encode(intValue)
        } else if let doubleValue = value as? Double {
            try container.encode(doubleValue)
        } else if let stringValue = value as? String {
            try container.encode(stringValue)
        } else if let boolValue = value as? Bool {
            try container.encode(boolValue)
        } else {
            throw EncodingError.invalidValue(value, EncodingError.Context(codingPath: encoder.codingPath, debugDescription: "Unsupported type"))
        }
    }
}