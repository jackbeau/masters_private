import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class CustomNavigationRail extends StatelessWidget {
  final int selectedIndex;
  
  const CustomNavigationRail({
    Key? key,
    required this.selectedIndex,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        NavigationRail(
          backgroundColor: Theme.of(context).colorScheme.background,
          selectedIndex: selectedIndex,
          onDestinationSelected: (int index) {
            switch (index) {
              case 0:
                context.go('/');
                break;
              case 1:
                context.go('/second');
                break;
              case 2:
                context.go('/third');
                break;
            }
          },
          labelType: NavigationRailLabelType.selected,
          minWidth: 48,
          destinations: const [
            NavigationRailDestination(
              icon: Icon(Icons.book),
              selectedIcon: Icon(Icons.book_outlined),
              label: Text('Scripts'),
            ),
            NavigationRailDestination(
              icon: Icon(Icons.layers),
              selectedIcon: Icon(Icons.layers_outlined),
              label: Text('Layers'),
            ),
            NavigationRailDestination(
              icon: Icon(Icons.extension),
              selectedIcon: Icon(Icons.extension_outlined),
              label: Text('Extensions'),
            ),
          ],
        ),
        Positioned(
          bottom: 20,
          left: 0,
          right: 0,
          child: IconButton(
            icon: Icon(Icons.settings),
            onPressed: () => print("hi"),
          ),
        ),
      ],
    );
  }
}
