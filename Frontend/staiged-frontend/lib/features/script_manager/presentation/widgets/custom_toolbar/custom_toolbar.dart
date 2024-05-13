import 'package:flutter/material.dart';
import '../../../domain/bloc/app_bar_bloc.dart';
import '../../../domain/bloc/script_manager_bloc.dart';
import 'tool_dropdown_button.dart'; // Ensure the file name matches your project structure
import 'mode_switcher.dart';
import 'inspector_switcher.dart';
import '../../../../../core/constants/app_images.dart';

class IconHelper {
  static Image getIcon(BuildContext context, String assetPath, bool isSelected) {
    return Image.asset(
      assetPath, 
      color: isSelected ? Theme.of(context).colorScheme.primaryContainer : Theme.of(context).colorScheme.onSurface,
      // fit: BoxFit.scaleDown, // Ensures the entire icon is visible within the constraints
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
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      height: 52,
      color: Theme.of(context).colorScheme.surface,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Container(
            width: 180,
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
                  icon: IconHelper.getIcon(context, ThemeIcons.camera, isCameraActive),
                  onPressed: () {
                    scriptManagerBloc.add(ToggleCameraView());
                  },
                  isSelected: isCameraActive,
                  tooltip: "Show stage camera"
                ),
                SizedBox(width: 8)
                // Include other buttons and functionalities as needed
              ],
            ),
          ),
          Container(
            width: 220,
            child: InspectorSwitcher(
              selectedInspector: selectedInspector,
              scriptManagerBloc: scriptManagerBloc,
            ),
          ),
        ],
      ),
    );
  }
}
