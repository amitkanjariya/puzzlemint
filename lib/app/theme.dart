import 'package:flutter/material.dart';

abstract final class MintColors {
  static const ink = Color(0xFF14182E);
  static const navy = Color(0xFF222844);
  static const teal = Color(0xFF19A99B);
  static const gold = Color(0xFFD9B56D);
  static const canvas = Color(0xFFF7F4EE);
  static const muted = Color(0xFF687087);
}

ThemeData mintTheme() {
  final scheme = ColorScheme.fromSeed(
    seedColor: MintColors.teal,
    brightness: Brightness.light,
    surface: MintColors.canvas,
  );
  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor: MintColors.canvas,
    fontFamily: 'Segoe UI',
    textTheme: const TextTheme(
      displaySmall: TextStyle(fontFamily: 'Georgia', fontSize: 40, fontWeight: FontWeight.bold, color: MintColors.ink, height: 1.12),
      headlineMedium: TextStyle(fontFamily: 'Georgia', fontSize: 28, fontWeight: FontWeight.bold, color: MintColors.ink),
      titleLarge: TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: MintColors.ink),
      bodyMedium: TextStyle(fontSize: 15, color: MintColors.navy, height: 1.5),
    ),
    cardTheme: CardThemeData(color: Colors.white, elevation: 0, shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(18), side: const BorderSide(color: Color(0xFFE5E3E0)))),
    inputDecorationTheme: InputDecorationTheme(
      filled: true, fillColor: Colors.white,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 15),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(style: ElevatedButton.styleFrom(
      backgroundColor: MintColors.teal, foregroundColor: Colors.white,
      padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 18),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      textStyle: const TextStyle(fontWeight: FontWeight.w700),
    )),
  );
}
