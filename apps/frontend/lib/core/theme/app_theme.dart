import 'package:flutter/material.dart';

abstract final class AppTheme {
  static ThemeData get light {
    const seed = Color(0xFF1565C0);

    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(seedColor: seed),
      scaffoldBackgroundColor: const Color(0xFFF7F9FC),
      inputDecorationTheme: const InputDecorationTheme(
        border: OutlineInputBorder(),
      ),
    );
  }
}
