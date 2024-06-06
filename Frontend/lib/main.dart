// Author: Jack Beaumont
// Date: 06/06/2024

import 'package:flutter/material.dart';
import 'package:flutter_web_plugins/url_strategy.dart';
import 'core/theme/theme.dart';
import 'shared/routes/app_routes.dart';

/// Main entry point for the application.
/// 
/// This function ensures Flutter widgets are initialized, sets up URL strategy,
/// and starts the app.
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  usePathUrlStrategy(); // Enables path URL strategy for web apps.
  runApp(const MyApp());
}

/// Root widget of the application.
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      debugShowCheckedModeBanner: false,
      title: 'Stage Assistant Client',
      themeMode: ThemeMode.light,
      theme: GlobalThemeData.lightThemeData,
      darkTheme: GlobalThemeData.darkThemeData,
      routerConfig: AppRoutes.defineRoutes(),
    );
  }
}
