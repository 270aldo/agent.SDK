package com.ngx.voiceagent.presentation.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ngx.voiceagent.data.model.User
import com.ngx.voiceagent.domain.repository.AuthRepository
import com.ngx.voiceagent.domain.repository.NotificationRepository
import com.ngx.voiceagent.presentation.state.MainUiState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class MainViewModel @Inject constructor(
    private val authRepository: AuthRepository,
    private val notificationRepository: NotificationRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(MainUiState())
    val uiState: StateFlow<MainUiState> = _uiState.asStateFlow()

    init {
        observeAuthState()
        observeNotifications()
    }

    fun checkAuthenticationStatus() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            
            try {
                val isAuthenticated = authRepository.isAuthenticated()
                val user = if (isAuthenticated) authRepository.getCurrentUser() else null
                
                _uiState.value = _uiState.value.copy(
                    isAuthenticated = isAuthenticated,
                    currentUser = user,
                    isLoading = false
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isAuthenticated = false,
                    currentUser = null,
                    isLoading = false,
                    error = e.message
                )
            }
        }
    }

    fun login(email: String, password: String) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            
            try {
                val result = authRepository.login(email, password)
                result.fold(
                    onSuccess = { loginResponse ->
                        _uiState.value = _uiState.value.copy(
                            isAuthenticated = true,
                            currentUser = loginResponse.user,
                            isLoading = false,
                            error = null
                        )
                    },
                    onFailure = { exception ->
                        _uiState.value = _uiState.value.copy(
                            isAuthenticated = false,
                            currentUser = null,
                            isLoading = false,
                            error = exception.message ?: "Login failed"
                        )
                    }
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isAuthenticated = false,
                    currentUser = null,
                    isLoading = false,
                    error = e.message ?: "An unexpected error occurred"
                )
            }
        }
    }

    fun logout() {
        viewModelScope.launch {
            try {
                authRepository.logout()
                _uiState.value = _uiState.value.copy(
                    isAuthenticated = false,
                    currentUser = null,
                    error = null
                )
            } catch (e: Exception) {
                // Even if logout fails on server, clear local state
                _uiState.value = _uiState.value.copy(
                    isAuthenticated = false,
                    currentUser = null,
                    error = null
                )
            }
        }
    }

    fun refreshToken() {
        viewModelScope.launch {
            try {
                val result = authRepository.refreshToken()
                result.fold(
                    onSuccess = { refreshResponse ->
                        _uiState.value = _uiState.value.copy(
                            currentUser = refreshResponse.user,
                            error = null
                        )
                    },
                    onFailure = {
                        // Token refresh failed, logout user
                        logout()
                    }
                )
            } catch (e: Exception) {
                logout()
            }
        }
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }

    fun updateConnectionStatus(isConnected: Boolean) {
        _uiState.value = _uiState.value.copy(isConnected = isConnected)
    }

    private fun observeAuthState() {
        viewModelScope.launch {
            authRepository.authStateFlow.collect { isAuthenticated ->
                if (!isAuthenticated && _uiState.value.isAuthenticated) {
                    // User was logged out
                    _uiState.value = _uiState.value.copy(
                        isAuthenticated = false,
                        currentUser = null
                    )
                }
            }
        }
    }

    private fun observeNotifications() {
        viewModelScope.launch {
            notificationRepository.unreadCountFlow.collect { count ->
                _uiState.value = _uiState.value.copy(unreadNotificationCount = count)
            }
        }
    }

    fun handleDeepLink(uri: String) {
        viewModelScope.launch {
            try {
                // Parse deep link and navigate accordingly
                when {
                    uri.contains("conversation/") -> {
                        val conversationId = uri.substringAfterLast("/")
                        _uiState.value = _uiState.value.copy(
                            deepLinkDestination = "conversation/$conversationId"
                        )
                    }
                    uri.contains("agent/") -> {
                        val agentId = uri.substringAfterLast("/")
                        _uiState.value = _uiState.value.copy(
                            deepLinkDestination = "agent/$agentId"
                        )
                    }
                    uri.contains("dashboard") -> {
                        _uiState.value = _uiState.value.copy(
                            deepLinkDestination = "dashboard"
                        )
                    }
                }
            } catch (e: Exception) {
                // Invalid deep link, ignore
            }
        }
    }

    fun clearDeepLinkDestination() {
        _uiState.value = _uiState.value.copy(deepLinkDestination = null)
    }
}