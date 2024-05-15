import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../domain/bloc/app_bar_bloc.dart';
import '../../../domain/bloc/script_manager_bloc.dart';
import 'tool_dropdown_button.dart';
import 'mode_switcher.dart';
import 'inspector_switcher.dart';
import '../../../../../core/constants/app_images.dart';

class IconHelper {
  static Image getIcon(BuildContext context, String assetPath, bool isSelected, {double width = 20}) {
    return Image.asset(
      assetPath,
      color: isSelected ? Theme.of(context).colorScheme.primaryContainer : Theme.of(context).colorScheme.onSurface,
      width: width,
    );
  }
}

class CustomToolbar extends StatelessWidget {
  final Mode currentMode;
  final InspectorPanel selectedInspector;
  final ScriptManagerBloc scriptManagerBloc;
  final bool isCameraActive;
  final Tool selectedTool;

  const CustomToolbar({
    super.key,
    required this.scriptManagerBloc,
    required this.currentMode,
    required this.selectedInspector,
    required this.selectedTool,
    this.isCameraActive = false,
  });

  @override
  Widget build(BuildContext context) {
    return BlocProvider<AppBarBloc>(
      create: (context) => AppBarBloc(scriptManagerBloc.state.pdfController!),
      child: Builder(
        builder: (context) {
          final appBarBloc = BlocProvider.of<AppBarBloc>(context);
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
                      if (scriptManagerBloc.state.mode == Mode.edit)
                        IconButton(
                          icon: IconHelper.getIcon(context, ThemeIcons.cue_tool, selectedTool == Tool.new_cue, width: 24),
                          onPressed: () => scriptManagerBloc.add(ToolChanged(selectedTool == Tool.new_cue ? Tool.none : Tool.new_cue)),
                          tooltip: "Add cue",
                        ),
                    ],
                  ),
                ),
                if (screenWidth >= 1080)
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
                        icon: Icon(Icons.search, color: Theme.of(context).colorScheme.onSurface),
                        onPressed: () {},
                      ),
                      IconButton(
                        icon: Icon(Icons.zoom_out, color: Theme.of(context).colorScheme.onSurface),
                        onPressed: () => appBarBloc.add(ZoomOut()),
                      ),
                      IconButton(
                        icon: Icon(Icons.zoom_in, color: Theme.of(context).colorScheme.onSurface),
                        onPressed: () => appBarBloc.add(ZoomIn()),
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
        },
      ),
    );
  }
}
