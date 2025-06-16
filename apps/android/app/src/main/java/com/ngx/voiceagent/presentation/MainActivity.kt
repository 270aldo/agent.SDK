package com.ngx.voiceagent.presentation

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.core.content.ContextCompat
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.compose.rememberNavController
import com.google.accompanist.systemuicontroller.rememberSystemUiController
import com.ngx.voiceagent.presentation.navigation.NGXNavHost
import com.ngx.voiceagent.presentation.theme.NGXVoiceAgentTheme
import com.ngx.voiceagent.presentation.viewmodel.MainViewModel
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        // Handle permission results
        permissions.entries.forEach {
            when (it.key) {
                Manifest.permission.RECORD_AUDIO -> {
                    if (it.value) {
                        // Audio permission granted
                    } else {
                        // Audio permission denied
                    }
                }
                Manifest.permission.POST_NOTIFICATIONS -> {
                    if (it.value) {
                        // Notification permission granted
                    } else {
                        // Notification permission denied
                    }
                }
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        val splashScreen = installSplashScreen()
        super.onCreate(savedInstanceState)

        setContent {
            NGXVoiceAgentTheme {
                val systemUiController = rememberSystemUiController()
                val backgroundColor = MaterialTheme.colorScheme.background

                LaunchedEffect(backgroundColor) {
                    systemUiController.setSystemBarsColor(
                        color = backgroundColor,
                        darkIcons = true
                    )
                }

                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    NGXApp()
                }
            }
        }

        // Request necessary permissions
        requestPermissions()
    }

    private fun requestPermissions() {
        val permissionsToRequest = mutableListOf<String>()

        // Audio permission
        if (ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.RECORD_AUDIO
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            permissionsToRequest.add(Manifest.permission.RECORD_AUDIO)
        }

        // Notification permission (Android 13+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(
                    this,
                    Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                permissionsToRequest.add(Manifest.permission.POST_NOTIFICATIONS)
            }
        }

        if (permissionsToRequest.isNotEmpty()) {
            permissionLauncher.launch(permissionsToRequest.toTypedArray())
        }
    }
}

@Composable
fun NGXApp(
    viewModel: MainViewModel = hiltViewModel()
) {
    val navController = rememberNavController()
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.checkAuthenticationStatus()
    }

    NGXNavHost(
        navController = navController,
        isAuthenticated = uiState.isAuthenticated,
        isLoading = uiState.isLoading
    )
}