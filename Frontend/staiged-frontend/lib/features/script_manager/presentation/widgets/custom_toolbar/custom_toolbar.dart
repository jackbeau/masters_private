import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import '../../../domain/bloc/app_bar_bloc.dart';
import '../../../domain/bloc/script_manager_bloc.dart';
import 'tool_dropdown_button.dart';
import 'mode_switcher.dart';
import 'inspector_switcher.dart';
import '../../../../../core/constants/app_images.dart';

class IconHelper {
  static Image getIcon(BuildContext context, String assetPath, bool isSelected) {
    return Image.asset(
      assetPath,
      color: isSelected ? Theme.of(context).colorScheme.primaryContainer : Theme.of(context).colorScheme.onSurface,
      width: 18
    );
  }
}

class CustomToolbar extends StatelessWidget {
  final AppBarBloc appBarBloc;
  final Mode currentMode;
  final InspectorPanel selectedInspector;
  final ScriptManagerBloc scriptManagerBloc;
  final bool isCameraActive;

  const CustomToolbar({
    super.key,
    required this.scriptManagerBloc,
    required this.appBarBloc,
    required this.currentMode,
    required this.selectedInspector,
    this.isCameraActive = false,
  });

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      height: 52,
      color: Theme.of(context).colorScheme.surface,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            flex: 2,
            child: Row(
              children: [
                Container(
                  width: 180,
                  child: ModeSwitcher(
                    currentMode: currentMode,
                    scriptManagerBloc: scriptManagerBloc,
                  ),
                ),
                const SizedBox(width: 12),
                ToolDropdownButton(
                  icon: Icons.edit,
                  items: const ['Black', 'Red', 'Green'],
                  onSelect: (String color) {
                    // Handle color change
                  },
                ),
              ],
            ),
          ),
          if (screenWidth >= 1080) // Conditionally display the title based on screen width
            Expanded(
              flex: 1,
              child: Center(
                child: Text(
                  "Romeo and Juliet",
                  style: Theme.of(context).textTheme.titleSmall,
                ),
              ),
            ),
          Expanded(
            flex: 2,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
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
                  icon: const Icon(Icons.zoom_out, color: Colors.white),
                  onPressed: () => appBarBloc.add(ZoomOut()),
                ),
                const SizedBox(width: 12),
                IconButton(
                  icon: IconHelper.getIcon(context, ThemeIcons.camera, isCameraActive),
                  onPressed: () {
                    scriptManagerBloc.add(ToggleCameraView());
                  },
                  tooltip: "Show stage camera",
                ),
                const SizedBox(width: 8),
                Container(
                  width: 220,
                  child: InspectorSwitcher(
                    selectedInspector: selectedInspector,
                    scriptManagerBloc: scriptManagerBloc,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
