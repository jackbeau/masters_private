import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../widgets/navigation_bar.dart';
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
                  CustomSidebar(
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
              pageBuilder: (context, state) => NoTransitionPage(child: const Center(child: Text('Home'))),
            ),
            GoRoute(
              path: '/script',
              pageBuilder: (context, state) => NoTransitionPage(child: ScriptManagerPage()),
            ),
            GoRoute(
              path: '/cues',
              pageBuilder: (context, state) => NoTransitionPage(child: const Center(child: Text('Cues'))),
            ),
            GoRoute(
              path: '/recordings',
              pageBuilder: (context, state) => NoTransitionPage(child: const Center(child: Text('Recordings'))),
            ),
            GoRoute(
              path: '/users',
              pageBuilder: (context, state) => NoTransitionPage(child: const Center(child: Text('Users'))),
            ),
            GoRoute(
              path: '/settings',
              pageBuilder: (context, state) => NoTransitionPage(child: const Center(child: Text('settings'))),
            ),
          ],
        ),
      ],
    );
  }

  static int _getCurrentIndex(String? location) {
    if (location == '/') {
      return 0;
    } else if (location == '/script') {
      return 1;
    } else if (location == '/cues') {
      return 2;
    } else if (location == '/recordings') {
      return 3;
    } else if (location == '/users') {
      return 4;
    } else if (location == '/settings') {
      return 5;
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