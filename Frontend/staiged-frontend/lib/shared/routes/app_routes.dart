import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../widgets/side_nav.dart';
import '../../features/script_editor/presentation/screens/script_editor_page.dart';
import '../../features/script_manager/presentation/screens/script_manager_page.dart';



class AppRoutes {
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
                  pageBuilder: (context, state) => NoTransitionPage(child: ScriptManager()),
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