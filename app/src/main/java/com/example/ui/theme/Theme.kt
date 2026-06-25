package com.example.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val BentoLightColorScheme = lightColorScheme(
    primary = BentoPurplePrimary,
    onPrimary = Color.White,
    secondary = BentoPurpleDark,
    onSecondary = Color.White,
    tertiary = BentoBorderLight,
    onTertiary = BentoPurpleDark,
    background = BentoBg,
    onBackground = BentoTextDark,
    surface = Color.White,
    onSurface = BentoTextDark,
    surfaceVariant = BentoContainerMuted,
    onSurfaceVariant = BentoTextSubtitle,
    error = BentoAccentRed,
    onError = Color.White,
    outline = BentoBorderMedium
)

private val BentoDarkColorScheme = darkColorScheme(
    primary = BentoBorderLight,
    onPrimary = BentoPurpleDark,
    secondary = BentoContainerActive,
    onSecondary = BentoPurpleDark,
    tertiary = BentoPurplePrimary,
    onTertiary = Color.White,
    background = Color(0xFF121115),
    onBackground = Color(0xFFF4EFF4),
    surface = Color(0xFF1D1B20),
    onSurface = Color(0xFFF4EFF4),
    surfaceVariant = Color(0xFF312E38),
    onSurfaceVariant = Color(0xFFCAC4D0),
    error = Color(0xFFF2B8B5),
    onError = Color(0xFF601410),
    outline = Color(0xFF938F99)
)

@Composable
fun MyApplicationTheme(
    darkTheme: Boolean = false, // Default to false to shine with the standard premium light Bento Grid aesthetic
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) BentoDarkColorScheme else BentoLightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
