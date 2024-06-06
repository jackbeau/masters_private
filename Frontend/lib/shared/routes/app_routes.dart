/// Author: Jack Beaumont
/// Date: 06/06/2024
/// 
/// This file defines the routes for the application using GoRouter and 
/// provides a custom page transition class `NoTransitionPage`.
library;

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../widgets/side_nav.dart';
import '../../features/script_editor/presentation/screens/script_editor_page.dart';
import '../../features/script_manager/presentation/screens/script_manager_page.dart';

class AppRoutes {
  /// Defines the routes for the application.
  /// 
  /// Returns:
  ///   A [GoRouter] object that contains the route configuration.
  static GoRouter defineRoutes() {
    return GoRouter(
      initialLocation: '/',
      routes: [
        StatefulShellRoute.indexedStack(
          builder: (BuildContext context, GoRouterState state, StatefulNavigationShell child) {
            int currentIndex = _getCurrentIndex(state.fullPath);
            return Scaffold(
              body: Row(
                children: [
                  SideNav(
                    selectedIndex: currentIndex
                  ),
                  Expanded(child: child),
                ],
              ),
            );
          },
          branches: <StatefulShellBranch>[
            StatefulShellBranch(
              routes: <RouteBase>[
                GoRoute(
                  path: '/',
                  pageBuilder: (context, state) => NoTransitionPage(child: const ScriptManager()),
                )
              ],
            ),
            StatefulShellBranch(
              routes: <RouteBase>[
                GoRoute(
                  path: '/script',
                  pageBuilder: (context, state) => NoTransitionPage(child: const ScriptEditorPage()),
                )
              ],
            ),
            StatefulShellBranch(
              routes: <RouteBase>[
                GoRoute(
                  path: '/cues',
                  pageBuilder: (context, state) => NoTransitionPage(child: const Center(child: Text('Cues'))),
                )
              ],
            ),
            StatefulShellBranch(
              routes: <RouteBase>[
                GoRoute(
                  path: '/recordings',
                  pageBuilder: (context, state) => NoTransitionPage(child: const Center(child: Text('Recordings'))),
                )
              ],
            ),
            StatefulShellBranch(
              routes: <RouteBase>[
                GoRoute(
                  path: '/users',
                  pageBuilder: (context, state) => NoTransitionPage(child: const Center(child: Text('Users'))),
                )
              ],
            ),
            StatefulShellBranch(
              routes: <RouteBase>[
                GoRoute(
                  path: '/settings',
                  pageBuilder: (context, state) => NoTransitionPage(child: const Center(child: Text('Settings'))),
                )
              ],
            ),
          ],
        ),
      ],
    );
  }

  /// Determines the current index based on the given location.
  ///
  /// Parameters:
  ///   location (String?): The current location path.
  ///
  /// Returns:
  ///   An integer representing the current index.
  static int _getCurrentIndex(String? location) {
    switch (location) {
      case '/':
        return 0;
      case '/script':
        return 1;
      case '/cues':
        return 2;
      case '/recordings':
        return 3;
      case '/users':
        return 4;
      case '/settings':
        return 5;
      default:
        return 0; // Default to home if no match found
    }
  }
}

class NoTransitionPage extends CustomTransitionPage<void> {
  /// Creates a page with no transition animations.
  ///
  /// Parameters:
  ///   child (Widget): The widget to be displayed on this page.
  NoTransitionPage({required super.child})
      : super(
          transitionsBuilder: (_, __, ___, child) => child,
        );
}
