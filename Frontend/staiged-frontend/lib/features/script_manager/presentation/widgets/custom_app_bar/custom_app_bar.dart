import 'package:flutter/material.dart';
import '../../../domain/bloc/app_bar_bloc.dart';
import '../../../domain/bloc/script_manager_bloc.dart';
import 'tool_dropdown_button.dart'; // Ensure the file name matches your project structure
import 'mode_switcher.dart';

class CustomToolbar extends StatelessWidget {
  final AppBarBloc appBarBloc;
  final Mode currentMode;
  final ScriptManagerBloc scriptManagerBloc;

  const CustomToolbar({
    super.key,
    required this.scriptManagerBloc,
    required this.appBarBloc,
    required this.currentMode,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8),
      height: 60.0,
      color: Theme.of(context).colorScheme.surface,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            flex: 2,
            child: ModeSwitcher(
              currentMode: currentMode,
              scriptManagerBloc: scriptManagerBloc,
            ),
          ),
          Expanded(
            child: Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                ToolDropdownButton(
                  icon: Icons.edit,
                  items: const ['Black', 'Red', 'Green'],
                  onSelect: (String color) {
                    // Handle color change
                  },
                ),
                IconButton(
                  icon: const Icon(Icons.search, color: Colors.white),
                  onPressed: () {
                    // Implement search functionality
                  },
                ),
                IconButton(
                  icon: const Icon(Icons.zoom_in, color: Colors.white),
                  onPressed: () => appBarBloc.add(ZoomIn()),
                ),
                IconButton(
                  icon: const Icon(Icons.camera_alt, color: Colors.white),
                  onPressed: () {
                    // Implement camera view functionality
                  },
                ),
                // Include other buttons and functionalities as needed
              ],
            ),
          ),
        ],
      ),
    );
  }
}
