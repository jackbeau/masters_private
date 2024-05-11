import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../widgets/custom_navigation_rail.dart';
import '../../features/script_manager/presentation/script_manager_page.dart';


class AppRoutes {
  static GoRouter defineRoutes() {
    return GoRouter(
      initialLocation: '/',
      routes: [
        ShellRoute(
          builder: (BuildContext context, GoRouterState state, Widget child) {
            int currentIndex = _getCurrentIndex(state.fullPath);
            return Scaffold(
              body: Row(
                children: [
                  CustomNavigationRail(
                    selectedIndex: currentIndex
                  ),
                  Expanded(child: child),
                ],
              ),
            );
          },
          routes: [
            GoRoute(
              path: '/',
              pageBuilder: (context, state) => NoTransitionPage(child: const Center(child: Text('First Page'))),
            ),
            GoRoute(
              path: '/second',
              pageBuilder: (context, state) => NoTransitionPage(child: ScriptManagerPage()),
            ),
            GoRoute(
              path: '/third',
              pageBuilder: (context, state) => NoTransitionPage(child: const Center(child: Text('Third Page'))),
            ),
          ],
        ),
      ],
    );
  }

  static int _getCurrentIndex(String? location) {
    if (location == '/') {
      return 0;
    } else if (location == '/second') {
      return 1;
    } else if (location == '/third') {
      return 2;
    } else {
      return 0; // default to home if no match found
    }
  }
}

class NoTransitionPage extends CustomTransitionPage<void> {
  NoTransitionPage({required Widget child})
      : super(
          transitionsBuilder: (_, __, ___, child) => child, // No animation
          child: child,
        );
}