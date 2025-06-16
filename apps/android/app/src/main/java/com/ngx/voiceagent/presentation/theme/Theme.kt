package com.ngx.voiceagent.presentation.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val DarkColorScheme = darkColorScheme(
    primary = NGXBlue80,
    onPrimary = NGXBlue20,
    primaryContainer = NGXBlue30,
    onPrimaryContainer = NGXBlue90,
    secondary = NGXGreen80,
    onSecondary = NGXGreen20,
    secondaryContainer = NGXGreen30,
    onSecondaryContainer = NGXGreen90,
    tertiary = NGXOrange80,
    onTertiary = NGXOrange20,
    tertiaryContainer = NGXOrange30,
    onTertiaryContainer = NGXOrange90,
    error = NGXRed80,
    onError = NGXRed20,
    errorContainer = NGXRed30,
    onErrorContainer = NGXRed90,
    background = NGXGray10,
    onBackground = NGXGray90,
    surface = NGXGray10,
    onSurface = NGXGray80,
    surfaceVariant = NGXGray30,
    onSurfaceVariant = NGXGray80,
    outline = NGXGray60
)

private val LightColorScheme = lightColorScheme(
    primary = NGXBlue40,
    onPrimary = NGXWhite,
    primaryContainer = NGXBlue90,
    onPrimaryContainer = NGXBlue10,
    secondary = NGXGreen40,
    onSecondary = NGXWhite,
    secondaryContainer = NGXGreen90,
    onSecondaryContainer = NGXGreen10,
    tertiary = NGXOrange40,
    onTertiary = NGXWhite,
    tertiaryContainer = NGXOrange90,
    onTertiaryContainer = NGXOrange10,
    error = NGXRed40,
    onError = NGXWhite,
    errorContainer = NGXRed90,
    onErrorContainer = NGXRed10,
    background = NGXGray99,
    onBackground = NGXGray10,
    surface = NGXGray99,
    onSurface = NGXGray10,
    surfaceVariant = NGXGray90,
    onSurfaceVariant = NGXGray30,
    outline = NGXGray50
)

@Composable
fun NGXVoiceAgentTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    // Dynamic color is available on Android 12+
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }

        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }
    
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = NGXTypography,
        shapes = NGXShapes,
        content = content
    )
}