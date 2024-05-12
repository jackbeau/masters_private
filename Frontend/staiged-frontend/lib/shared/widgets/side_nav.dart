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
          buildNavItem(index: 0, assetPath: "assets/icons/home.png", route: '/', label: 'Home', iconSize: 22),
          const SizedBox(height: 32),
          buildNavItem(index: 1, assetPath: "assets/icons/script.png", route: '/script', label: 'Script', iconSize: 22),
          const SizedBox(height: 18),
          buildNavItem(index: 2, assetPath: "assets/icons/cues.png", route: '/cues', label: 'Cues', iconSize: 22),
          const SizedBox(height: 18),
          buildNavItem(index: 3, assetPath: "assets/icons/recording.png", route: '/recordings', label: 'Recordings', iconSize: 22),
          const SizedBox(height: 18),
          buildNavItem(index: 4, assetPath: "assets/icons/users.png", route: '/users', label: 'Users', iconSize: 22),
          const Spacer(),
          buildNavItem(index: 5, assetPath: "assets/icons/settings.png", route: '/settings', label: 'Settings', iconSize: 22),
          const SizedBox(height: 16),
          buildUserIconNavItem(label: 'User'),
          const SizedBox(height: 18),
        ],
      ),
    );
  }
  Widget buildNavItem({required int index, required String assetPath, required String route, required String label, required double iconSize}) {
    return InkWell(
      onTap: () => context.go(route),
      child: MouseRegion(
        onEnter: (_) => setState(() => isHovering[index] = true),
        onExit: (_) => setState(() => isHovering[index] = false),
        child: Container(
          width: 32,
          height: 32,
          padding: EdgeInsets.all((32 - iconSize) / 2),
          child: AnimatedSwitcher(
            duration: const Duration(milliseconds: 300),
            child: Image.asset(
              assetPath,
              key: ValueKey<bool>(widget.selectedIndex == index || isHovering[index]),
              colorBlendMode: BlendMode.srcIn,
              color: widget.selectedIndex == index
                  ? Theme.of(context).colorScheme.onPrimary
                  : (isHovering[index] && widget.selectedIndex != index
                      ? Theme.of(context).colorScheme.onSurfaceVariant
                      : const Color(0xFF50525E)),
              width: iconSize,
              height: iconSize,
            ),
          ),
        ),
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
