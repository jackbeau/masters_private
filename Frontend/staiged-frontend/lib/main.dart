import 'package:flutter/material.dart';
// If you are going to use settings or any service that needs to be initialized, uncomment these:
// import 'pages/settings/settings_controller.dart';
// import 'pages/settings/settings_service.dart';
import 'core/theme/theme.dart';
import 'shared/routes/app_routes.dart';
import 'package:flutter_web_plugins/url_strategy.dart';


void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Assuming SettingsService is what you might use for loading and saving settings
  // final settingsService = SettingsService();
  // final settingsController = SettingsController(settingsService);
  // await settingsController.loadSettings();

  usePathUrlStrategy();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      debugShowCheckedModeBanner: false,
      title: 'Stage Assistant Client',
      themeMode: ThemeMode.light, // Or ThemeMode.dark, which could be dynamically determined
      theme: GlobalThemeData.lightThemeData, 
      darkTheme: GlobalThemeData.darkThemeData,
      routerConfig: AppRoutes.defineRoutes(),
    );
  }
}