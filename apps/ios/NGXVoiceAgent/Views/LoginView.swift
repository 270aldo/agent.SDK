import SwiftUI

struct LoginView: View {
    @EnvironmentObject var authManager: AuthenticationManager
    @State private var email = ""
    @State private var password = ""
    @State private var showingPassword = false
    @FocusState private var emailFocused: Bool
    @FocusState private var passwordFocused: Bool
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 32) {
                    Spacer()
                    
                    // Logo and Title
                    VStack(spacing: 16) {
                        Image(systemName: "mic.circle.fill")
                            .font(.system(size: 80))
                            .foregroundColor(.blue)
                        
                        VStack(spacing: 8) {
                            Text("NGX Voice Agent")
                                .font(.largeTitle)
                                .fontWeight(.bold)
                            
                            Text("Sign in to your dashboard")
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                        }
                    }
                    
                    // Login Form
                    VStack(spacing: 20) {
                        // Email Field
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Email")
                                .font(.headline)
                                .foregroundColor(.primary)
                            
                            TextField("Enter your email", text: $email)
                                .textFieldStyle(RoundedBorderTextFieldStyle())
                                .keyboardType(.emailAddress)
                                .textInputAutocapitalization(.never)
                                .autocorrectionDisabled()
                                .focused($emailFocused)
                        }
                        
                        // Password Field
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Password")
                                .font(.headline)
                                .foregroundColor(.primary)
                            
                            HStack {
                                Group {
                                    if showingPassword {
                                        TextField("Enter your password", text: $password)
                                    } else {
                                        SecureField("Enter your password", text: $password)
                                    }
                                }
                                .focused($passwordFocused)
                                
                                Button(action: { showingPassword.toggle() }) {
                                    Image(systemName: showingPassword ? "eye.slash.fill" : "eye.fill")
                                        .foregroundColor(.secondary)
                                }
                            }
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                        }
                        
                        // Error Message
                        if let errorMessage = authManager.errorMessage {
                            Text(errorMessage)
                                .foregroundColor(.red)
                                .font(.caption)
                                .multilineTextAlignment(.center)
                        }
                        
                        // Login Button
                        Button(action: handleLogin) {
                            HStack {
                                if authManager.isLoading {
                                    ProgressView()
                                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                        .scaleEffect(0.8)
                                } else {
                                    Text("Sign In")
                                        .fontWeight(.semibold)
                                }
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(isFormValid ? Color.blue : Color.gray)
                            .foregroundColor(.white)
                            .cornerRadius(12)
                        }
                        .disabled(!isFormValid || authManager.isLoading)
                        
                        // Demo Credentials
                        VStack(spacing: 8) {
                            Text("Demo Credentials")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            
                            Button(action: fillDemoCredentials) {
                                Text("admin@ngx.com / demo123")
                                    .font(.caption)
                                    .foregroundColor(.blue)
                            }
                        }
                    }
                    .padding(.horizontal)
                    
                    Spacer()
                    
                    // Footer
                    Text("© 2025 NGX Voice Agent")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding()
            }
            .navigationTitle("")
            .navigationBarHidden(true)
            .onSubmit {
                if emailFocused {
                    passwordFocused = true
                } else if passwordFocused {
                    handleLogin()
                }
            }
        }
    }
    
    private var isFormValid: Bool {
        !email.isEmpty && !password.isEmpty && email.contains("@")
    }
    
    private func handleLogin() {
        guard isFormValid else { return }
        
        emailFocused = false
        passwordFocused = false
        
        authManager.login(email: email, password: password)
    }
    
    private func fillDemoCredentials() {
        email = "admin@ngx.com"
        password = "demo123"
    }
}

#Preview {
    LoginView()
        .environmentObject(AuthenticationManager())
}