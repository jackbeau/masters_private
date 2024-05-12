import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class SideNav extends StatefulWidget {
  final int selectedIndex;

  const SideNav({Key? key, required this.selectedIndex}) : super(key: key);

  @override
  SideNavState createState() => SideNavState();
}

class SideNavState extends State<SideNav> {
  late List<bool> isHovering;

  @override
  void initState() {
    super.initState();
    isHovering = List.generate(6, (_) => false);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 64,
      color: Theme.of(context).colorScheme.background,
      child: Column(
        children: <Widget>[
          const SizedBox(height: 16),
          buildNavItem(index: 0, assetPath: "assets/icons/home.png", route: '/', label: 'Home'),
          const SizedBox(height: 32),
          buildNavItem(index: 1, assetPath: "assets/icons/script.png", route: '/script', label: 'Script'),
          const SizedBox(height: 18),
          buildNavItem(index: 2, assetPath: "assets/icons/cues.png", route: '/cues', label: 'Cues'),
          const SizedBox(height: 18),
          buildNavItem(index: 3, assetPath: "assets/icons/recording.png", route: '/recordings', label: 'Recordings'),
          const SizedBox(height: 18),
          buildNavItem(index: 4, assetPath: "assets/icons/users.png", route: '/users', label: 'Users'),
          const Spacer(),
          buildNavItem(index: 5, assetPath: "assets/icons/settings.png", route: '/settings', label: 'Settings'),
          const SizedBox(height: 16),
          buildUserIconNavItem(label: 'User'),
          const SizedBox(height: 18),
        ],
      ),
    );
  }
  Widget buildNavItem({required int index, required String assetPath, required String route, required String label}) {
    return InkWell(
      onTap: () => context.go(route),
      child: MouseRegion(
        onEnter: (_) => setState(() => isHovering[index] = true),
        onExit: (_) => setState(() => isHovering[index] = false),
          child: AnimatedSwitcher(
            duration: const Duration(milliseconds: 300),
            child: Container(
                width: 32,
                height: 32,
                alignment: Alignment.center,
                child: Image.asset(
                  assetPath,
                  key: ValueKey<bool>(widget.selectedIndex == index || isHovering[index]),
                  colorBlendMode: BlendMode.srcIn,
                  color: widget.selectedIndex == index
                      ? Theme.of(context).colorScheme.onPrimary
                      : (isHovering[index] && widget.selectedIndex != index
                          ? Theme.of(context).colorScheme.onSurfaceVariant
                          : const Color(0xFF50525E)),
                  width: 20,
                ),
            )
          )
      )
    );
  }

  Widget buildUserIconNavItem({required String label}) {
    return InkWell(
      onTap: () => print("$label pressed"),
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
            borderRadius: BorderRadius.circular(4), // Slightly rounded corners
          ),
          child: const Text(
            "JB",
            style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold, fontSize: 12),
          ),
        ),
      ),
    );
  }
}
