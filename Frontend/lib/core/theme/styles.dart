
import 'package:flutter/material.dart';

class CustomStyles {
    static TextTheme getTextTheme() {
    return const TextTheme(
      displayLarge: stageassistantdisplaylarge,
      displayMedium: stageassistantdisplaymedium,
      displaySmall: stageassistantdisplaysmall,
      headlineLarge: stageassistantheadlinelarge,
      headlineMedium: stageassistantheadlinemedium,
      headlineSmall: stageassistantheadlinesmall,
      bodyLarge: stageassistantbodylarge,
      bodyMedium: stageassistantbodymedium,
      bodySmall: stageassistantbodysmall,
      labelLarge: stageassistantlabellarge,
      labelMedium: stageassistantlabelmedium,
      labelSmall: stageassistantlabelsmall,  // Example for button style
      titleLarge: stageassistanttitlelarge,
      titleMedium: stageassistantlabelmedium,
      titleSmall: stageassistanttitlesmall,
    );
  }

  static const TextStyle stageassistantdisplaylarge = TextStyle(
    fontSize: 57,
    decoration: TextDecoration.none,
    fontStyle: FontStyle.normal,
    fontWeight: FontWeight.w400,
    height: 64 / 57,
    letterSpacing: -0.25,
  );

  static const TextStyle stageassistantdisplaymedium = TextStyle(
    fontSize: 45,
    decoration: TextDecoration.none,
    fontStyle: FontStyle.normal,
    fontWeight: FontWeight.w400,
    height: 52 / 45,
    letterSpacing: 0,
  );

  static const TextStyle stageassistantdisplaysmall = TextStyle(
    fontSize: 36,
    decoration: TextDecoration.none,
    fontStyle: FontStyle.normal,
    fontWeight: FontWeight.w400,
    height: 44 / 36,
    letterSpacing: 0,
  );

  static const TextStyle stageassistantheadlinelarge = TextStyle(
    fontSize: 32,
    decoration: TextDecoration.none,
    fontStyle: FontStyle.normal,
    fontWeight: FontWeight.w400,
    height: 40 / 32,
    letterSpacing: 0,
  );

  static const TextStyle stageassistantheadlinemedium = TextStyle(
    fontSize: 28,
    decoration: TextDecoration.none,
    fontStyle: FontStyle.normal,
    fontWeight: FontWeight.w400,
    height: 36 / 28,
    letterSpacing: 0,
  );

  static const TextStyle stageassistantheadlinesmall = TextStyle(
    fontSize: 24,
    decoration: TextDecoration.none,
    fontStyle: FontStyle.normal,
    fontWeight: FontWeight.w400,
    height: 32 / 24,
    letterSpacing: 0,
  );

  static const TextStyle stageassistantbodylarge = TextStyle(
    fontSize: 16,
    decoration: TextDecoration.none,
    fontStyle: FontStyle.normal,
    fontWeight: FontWeight.w400,
    height: 24 / 16,
    letterSpacing: 0.5,
  );

  static const TextStyle stageassistantbodymedium = TextStyle(
    fontSize: 14,
    decoration: TextDecoration.none,
    fontStyle: FontStyle.normal,
    fontWeight: FontWeight.w400,
    height: 20 / 14,
    letterSpacing: 0.25,
  );

  static const TextStyle stageassistantbodysmall = TextStyle(
    fontSize: 12,
    decoration: TextDecoration.none,
    fontStyle: FontStyle.normal,
    fontWeight: FontWeight.w400,
    height: 16 / 12,
    letterSpacing: 0.4,
  );

  static const TextStyle stageassistantlabellarge = TextStyle(
    fontSize: 14,
    decoration: TextDecoration.none,
    fontStyle: FontStyle.normal,
    fontWeight: FontWeight.w500,
    height: 20 / 14,
    letterSpacing: 0.1,
  );

  static const TextStyle stageassistantlabelmedium = TextStyle(
    fontSize: 12,
    decoration: TextDecoration.none,
    fontStyle: FontStyle.normal,
    fontWeight: FontWeight.w500,
    height: 16 / 12,
    letterSpacing: 0.5,
  );

  static const TextStyle stageassistantlabelsmall = TextStyle(
    fontSize: 11,
    decoration: TextDecoration.none,
    fontStyle: FontStyle.normal,
    fontWeight: FontWeight.w500,
    height: 16 / 11,
    letterSpacing: 0.5,
  );

  static const TextStyle stageassistanttitlelarge = TextStyle(
    fontSize: 22,
    decoration: TextDecoration.none,
    fontStyle: FontStyle.normal,
    fontWeight: FontWeight.w400,
    height: 28 / 22,
    letterSpacing: 0,
  );

  static const TextStyle stageassistanttitlemedium = TextStyle(
    fontSize: 16,
    decoration: TextDecoration.none,
    fontStyle: FontStyle.normal,
    fontWeight: FontWeight.w500,
    height: 24 / 16,
    letterSpacing: 0.15,
  );

  static const TextStyle stageassistanttitlesmall = TextStyle(
    fontSize: 14,
    decoration: TextDecoration.none,
    fontStyle: FontStyle.normal,
    fontWeight: FontWeight.w500,
    height: 20 / 14,
    letterSpacing: 0.1,
  );
}

