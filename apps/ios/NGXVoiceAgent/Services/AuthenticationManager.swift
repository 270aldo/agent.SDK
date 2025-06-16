import Foundation
import SwiftUI
import Combine

@MainActor
class AuthenticationManager: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let networkManager = NetworkManager.shared
    private let keychain = KeychainManager()
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        checkAuthenticationStatus()
    }
    
    func checkAuthenticationStatus() {
        if let token = keychain.getToken() {
            isLoading = true
            
            networkManager.verifyToken(token)
                .receive(on: DispatchQueue.main)
                .sink(
                    receiveCompletion: { [weak self] completion in
                        self?.isLoading = false
                        if case .failure = completion {
                            self?.logout()
                        }
                    },
                    receiveValue: { [weak self] user in
                        self?.currentUser = user
                        self?.isAuthenticated = true
                        self?.isLoading = false
                    }
                )
                .store(in: &cancellables)
        }
    }
    
    func login(email: String, password: String) {
        isLoading = true
        errorMessage = nil
        
        networkManager.login(email: email, password: password)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { [weak self] completion in
                    self?.isLoading = false
                    if case .failure(let error) = completion {
                        self?.errorMessage = error.localizedDescription
                    }
                },
                receiveValue: { [weak self] response in
                    self?.keychain.saveToken(response.token)
                    self?.currentUser = response.user
                    self?.isAuthenticated = true
                    self?.isLoading = false
                    self?.errorMessage = nil
                }
            )
            .store(in: &cancellables)
    }
    
    func logout() {
        keychain.deleteToken()
        currentUser = nil
        isAuthenticated = false
        errorMessage = nil
    }
    
    func refreshToken() {
        guard let token = keychain.getToken() else {
            logout()
            return
        }
        
        networkManager.refreshToken(token)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { [weak self] completion in
                    if case .failure = completion {
                        self?.logout()
                    }
                },
                receiveValue: { [weak self] response in
                    self?.keychain.saveToken(response.token)
                    self?.currentUser = response.user
                }
            )
            .store(in: &cancellables)
    }
}

// MARK: - Authentication Response Models
struct LoginResponse: Codable {
    let user: User
    let token: String
}

struct RefreshTokenResponse: Codable {
    let user: User
    let token: String
}

// MARK: - Keychain Manager
class KeychainManager {
    private let tokenKey = "ngx_auth_token"
    
    func saveToken(_ token: String) {
        let data = token.data(using: .utf8)!
        
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: tokenKey,
            kSecValueData as String: data
        ]
        
        SecItemDelete(query as CFDictionary)
        SecItemAdd(query as CFDictionary, nil)
    }
    
    func getToken() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: tokenKey,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var dataTypeRef: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &dataTypeRef)
        
        if status == errSecSuccess {
            if let data = dataTypeRef as? Data {
                return String(data: data, encoding: .utf8)
            }
        }
        
        return nil
    }
    
    func deleteToken() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: tokenKey
        ]
        
        SecItemDelete(query as CFDictionary)
    }
}