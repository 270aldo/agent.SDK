import Foundation
import Combine

class NetworkManager: ObservableObject {
    static let shared = NetworkManager()
    
    private let baseURL: URL
    private let session: URLSession
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder
    
    private init() {
        // Configure base URL from environment or default
        if let urlString = Bundle.main.object(forInfoDictionaryKey: "API_BASE_URL") as? String,
           let url = URL(string: urlString) {
            self.baseURL = url
        } else {
            self.baseURL = URL(string: "http://localhost:8000")!
        }
        
        // Configure URLSession
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60
        self.session = URLSession(configuration: config)
        
        // Configure JSON handling
        self.decoder = JSONDecoder()
        self.decoder.dateDecodingStrategy = .iso8601
        
        self.encoder = JSONEncoder()
        self.encoder.dateEncodingStrategy = .iso8601
    }
    
    func configure() {
        // Additional configuration if needed
    }
    
    // MARK: - Generic Request Methods
    
    private func makeRequest<T: Codable>(
        endpoint: String,
        method: HTTPMethod = .GET,
        body: Encodable? = nil,
        requiresAuth: Bool = true
    ) -> AnyPublisher<T, NetworkError> {
        
        var request = URLRequest(url: baseURL.appendingPathComponent(endpoint))
        request.httpMethod = method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Add authentication header if required
        if requiresAuth, let token = KeychainManager().getToken() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        // Add request body if provided
        if let body = body {
            do {
                request.httpBody = try encoder.encode(body)
            } catch {
                return Fail(error: NetworkError.encodingError(error))
                    .eraseToAnyPublisher()
            }
        }
        
        return session.dataTaskPublisher(for: request)
            .map(\.data)
            .decode(type: T.self, decoder: decoder)
            .mapError { error in
                if error is DecodingError {
                    return NetworkError.decodingError(error)
                } else {
                    return NetworkError.networkError(error)
                }
            }
            .eraseToAnyPublisher()
    }
    
    // MARK: - Authentication Endpoints
    
    func login(email: String, password: String) -> AnyPublisher<LoginResponse, NetworkError> {
        let loginRequest = LoginRequest(email: email, password: password)
        return makeRequest<LoginResponse>(
            endpoint: "auth/login",
            method: .POST,
            body: loginRequest,
            requiresAuth: false
        )
    }
    
    func verifyToken(_ token: String) -> AnyPublisher<User, NetworkError> {
        return makeRequest<User>(endpoint: "auth/verify")
    }
    
    func refreshToken(_ token: String) -> AnyPublisher<RefreshTokenResponse, NetworkError> {
        let refreshRequest = RefreshTokenRequest(token: token)
        return makeRequest<RefreshTokenResponse>(
            endpoint: "auth/refresh",
            method: .POST,
            body: refreshRequest,
            requiresAuth: false
        )
    }
    
    // MARK: - Dashboard Endpoints
    
    func getDashboardStats() -> AnyPublisher<DashboardStats, NetworkError> {
        return makeRequest<DashboardStats>(endpoint: "dashboard/stats")
    }
    
    func getRecentConversations(limit: Int = 10) -> AnyPublisher<[Conversation], NetworkError> {
        return makeRequest<[Conversation]>(endpoint: "conversations/recent?limit=\(limit)")
    }
    
    // MARK: - Conversations Endpoints
    
    func getConversations(
        platform: String? = nil,
        status: String? = nil,
        page: Int = 1,
        limit: Int = 20
    ) -> AnyPublisher<ConversationsResponse, NetworkError> {
        var queryItems: [URLQueryItem] = [
            URLQueryItem(name: "page", value: "\(page)"),
            URLQueryItem(name: "limit", value: "\(limit)")
        ]
        
        if let platform = platform {
            queryItems.append(URLQueryItem(name: "platform", value: platform))
        }
        
        if let status = status {
            queryItems.append(URLQueryItem(name: "status", value: status))
        }
        
        var components = URLComponents()
        components.queryItems = queryItems
        let queryString = components.query ?? ""
        
        return makeRequest<ConversationsResponse>(endpoint: "conversations?\(queryString)")
    }
    
    func getConversation(id: String) -> AnyPublisher<ConversationDetail, NetworkError> {
        return makeRequest<ConversationDetail>(endpoint: "conversations/\(id)")
    }
    
    func getMessages(conversationId: String) -> AnyPublisher<[Message], NetworkError> {
        return makeRequest<[Message]>(endpoint: "conversations/\(conversationId)/messages")
    }
    
    // MARK: - Analytics Endpoints
    
    func getAnalyticsMetrics(
        period: String = "week"
    ) -> AnyPublisher<ConversationMetrics, NetworkError> {
        return makeRequest<ConversationMetrics>(endpoint: "analytics/metrics?period=\(period)")
    }
    
    // MARK: - Agents Endpoints
    
    func getAgents() -> AnyPublisher<[VoiceAgent], NetworkError> {
        return makeRequest<[VoiceAgent]>(endpoint: "agents")
    }
    
    func createAgent(_ agent: CreateAgentRequest) -> AnyPublisher<VoiceAgent, NetworkError> {
        return makeRequest<VoiceAgent>(
            endpoint: "agents",
            method: .POST,
            body: agent
        )
    }
    
    func updateAgent(id: String, _ agent: UpdateAgentRequest) -> AnyPublisher<VoiceAgent, NetworkError> {
        return makeRequest<VoiceAgent>(
            endpoint: "agents/\(id)",
            method: .PUT,
            body: agent
        )
    }
    
    func deleteAgent(id: String) -> AnyPublisher<EmptyResponse, NetworkError> {
        return makeRequest<EmptyResponse>(
            endpoint: "agents/\(id)",
            method: .DELETE
        )
    }
    
    // MARK: - Notifications Endpoints
    
    func getNotifications() -> AnyPublisher<[AppNotification], NetworkError> {
        return makeRequest<[AppNotification]>(endpoint: "notifications")
    }
    
    func markNotificationAsRead(id: String) -> AnyPublisher<EmptyResponse, NetworkError> {
        return makeRequest<EmptyResponse>(
            endpoint: "notifications/\(id)/read",
            method: .PATCH
        )
    }
}

// MARK: - Request/Response Models

struct LoginRequest: Codable {
    let email: String
    let password: String
}

struct RefreshTokenRequest: Codable {
    let token: String
}

struct ConversationsResponse: Codable {
    let conversations: [Conversation]
    let total: Int
    let page: Int
    let limit: Int
}

struct ConversationDetail: Codable {
    let conversation: Conversation
    let messages: [Message]
}

struct CreateAgentRequest: Codable {
    let name: String
    let platform: String
    let personality: AgentPersonality
    let triggers: AgentTriggers
    let ui: AgentUI
    let behavior: AgentBehavior
    let qualificationCriteria: QualificationCriteria
}

struct UpdateAgentRequest: Codable {
    let name: String?
    let isActive: Bool?
    let personality: AgentPersonality?
    let triggers: AgentTriggers?
    let ui: AgentUI?
    let behavior: AgentBehavior?
    let qualificationCriteria: QualificationCriteria?
}

struct EmptyResponse: Codable {}

// MARK: - HTTP Method Enum

enum HTTPMethod: String {
    case GET = "GET"
    case POST = "POST"
    case PUT = "PUT"
    case PATCH = "PATCH"
    case DELETE = "DELETE"
}

// MARK: - Network Error Enum

enum NetworkError: Error, LocalizedError {
    case invalidURL
    case networkError(Error)
    case decodingError(Error)
    case encodingError(Error)
    case unauthorized
    case serverError(Int)
    case unknown
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .decodingError(let error):
            return "Decoding error: \(error.localizedDescription)"
        case .encodingError(let error):
            return "Encoding error: \(error.localizedDescription)"
        case .unauthorized:
            return "Unauthorized access"
        case .serverError(let code):
            return "Server error with code: \(code)"
        case .unknown:
            return "Unknown error occurred"
        }
    }
}