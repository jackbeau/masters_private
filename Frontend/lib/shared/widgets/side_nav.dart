/// File: side_nav.dart
/// Author: Jack Beaumont
/// Date: 06/06/2024
/// Description: This file contains the SideNav widget, which is a custom navigation
/// bar with multiple items and hover effects.
library;

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'custom_crossfade.dart';

class SideNav extends StatefulWidget {
  final int selectedIndex;

  const SideNav({super.key, required this.selectedIndex});

  @override
  SideNavState createState() => SideNavState();
}

class SideNavState extends State<SideNav> {
  late List<bool> isHovering;
  late List<int> updateCounters;

  @override
  void initState() {
    super.initState();
    isHovering = List.generate(6, (_) => false);
    updateCounters = List.generate(6, (_) => 0);
  }

  /// Updates the hover state and increments the counter for the given index.
  /// 
  /// Parameters:
  /// - index (int): The index of the nav item being hovered.
  /// - hoverState (bool): The new hover state (true if hovering, false otherwise).
  void updateHoverState(int index, bool hoverState) {
    setState(() {
      isHovering[index] = hoverState;
      updateCounters[index]++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 64,
      color: Theme.of(context).colorScheme.background,
      child: Column(
        children: <Widget>[
          const SizedBox(height: 16),
          buildNavItem(index: 0, assetPath: "assets/icons/home.png", route: '/', label: 'Home', iconSize: 20),
          const SizedBox(height: 32),
          buildNavItem(index: 1, assetPath: "assets/icons/script.png", route: '/script', label: 'Script', iconSize: 20),
          const SizedBox(height: 18),
          buildNavItem(index: 2, assetPath: "assets/icons/cues.png", route: '/cues', label: 'Cues', iconSize: 20),
          const SizedBox(height: 18),
          buildNavItem(index: 3, assetPath: "assets/icons/recording.png", route: '/recordings', label: 'Recordings', iconSize: 20),
          const SizedBox(height: 18),
          buildNavItem(index: 4, assetPath: "assets/icons/users.png", route: '/users', label: 'Users', iconSize: 20),
          const Spacer(),
          buildNavItem(index: 5, assetPath: "assets/icons/settings.png", route: '/settings', label: 'Settings', iconSize: 20),
          const SizedBox(height: 16),
          buildUserIconNavItem(label: 'User'),
          const SizedBox(height: 18),
        ],
      ),
    );
  }

  /// Builds a navigation item widget with specified parameters.
  ///
  /// Parameters:
  /// - index (int): The index of the navigation item.
  /// - assetPath (String): The path to the icon asset.
  /// - route (String): The navigation route.
  /// - label (String): The label for the navigation item.
  /// - iconSize (double): The size of the icon.
  ///
  /// Returns:
  /// - Widget: The navigation item widget.
  Widget buildNavItem({required int index, required String assetPath, required String route, required String label, required double iconSize}) {
    bool isSelected = widget.selectedIndex == index;

    return InkWell(
      onTap: () {
        _logNavigation(route);
        context.go(route);
      },
      child: MouseRegion(
        onEnter: (_) => updateHoverState(index, true),
        onExit: (_) => updateHoverState(index, false),
        child: Container(
          width: 32,
          height: 32,
          padding: EdgeInsets.all((32 - iconSize) / 2),
          child: isSelected
              ? Image.asset(assetPath, color: Theme.of(context).colorScheme.onPrimary, width: iconSize)
              : CustomCrossfade(
                  showFirst: !isHovering[index],
                  firstChild: Image.asset(assetPath, color: Theme.of(context).colorScheme.onSurfaceVariant, width: iconSize),
                  secondChild: Image.asset(assetPath, color: const Color(0xFF50525E), width: iconSize),
                  duration: const Duration(milliseconds: 120),
                ),
        ),
      ),
    );
  }

  /// Logs the navigation action.
  ///
  /// Parameters:
  /// - route (String): The route to navigate to.
  void _logNavigation(String route) {
    debugPrint('Navigating to $route');
  }

  /// Builds the user icon navigation item.
  ///
  /// Parameters:
  /// - label (String): The label for the user icon.
  ///
  /// Returns:
  /// - Widget: The user icon navigation item widget.
  Widget buildUserIconNavItem({required String label}) {
    return InkWell(
      onTap: () {
        debugPrint("$label pressed");
      },
      child: MouseRegion(
        child: Container(
          width: 32,
          height: 32,
          margin: const EdgeInsets.symmetric(vertical: 8),
          alignment: Alignment.center,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Theme.of(context).colorScheme.primary, Theme.of(context).colorScheme.primaryContainer],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(4),
          ),
          child: const Text(
            "JB",
            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
          ),
        ),
      ),
    );
  }
}
