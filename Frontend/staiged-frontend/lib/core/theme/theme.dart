import 'package:flutter/material.dart';
import 'styles.dart';

class GlobalThemeData {

  static final Color _lightFocusColor = Colors.black.withOpacity(0.12);
  static final Color _darkFocusColor = Colors.white.withOpacity(0.12);

  static ThemeData lightThemeData = themeData(darkColorScheme, _darkFocusColor);
  static ThemeData darkThemeData = themeData(darkColorScheme, _darkFocusColor);

  static const ColorScheme lightColorScheme = ColorScheme(
    primary: Color(0xFFB93C5D),
    onPrimary: Colors.black,
    secondary: Color(0xFFEFF3F3),
    onSecondary: Color(0xFF322942),
    error: Colors.redAccent,
    onError: Colors.white,
    background: Color(0xFFE6EBEB),
    onBackground: Colors.white,
    surface: Color(0xFFFAFBFB),
    onSurface: Color(0xFF241E30),
    brightness: Brightness.light,
  );

    static const ColorScheme darkColorScheme = ColorScheme(
    brightness: Brightness.dark,

    primary: Color(0xFF0057FF),
    primaryContainer: Color(0xFF0A7AFF),
    onPrimary: Colors.white,

    secondary: Color(0xFF33374A),
    onSecondary: Color(0xFF748AFF),
    
    tertiary: Color(0xFFC8B04E),

    surface: Color(0xFF12141D),
    onSurface: Color(0xFFE0E0E5),
    surfaceVariant: Color(0xFF20222E),
    onSurfaceVariant: Color(0xFF8E91A3),

    background: Color(0xFF000000),
    onBackground: Color(0xFFFFFFFF),

    error: Colors.redAccent,
    onError: Colors.white,

    outlineVariant: Color(0xFF8E91A3),
  );

  static ThemeData themeData(ColorScheme colorScheme, Color focusColor) {
    return ThemeData(
        colorScheme: colorScheme,
        canvasColor: colorScheme.background,
        scaffoldBackgroundColor: colorScheme.background,
        highlightColor: Colors.transparent,
        focusColor: focusColor,
        textTheme: CustomStyles.getTextTheme()
       );
  }
}