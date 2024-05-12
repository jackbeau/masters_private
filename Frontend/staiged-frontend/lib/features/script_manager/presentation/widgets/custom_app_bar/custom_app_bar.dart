import 'package:flutter/material.dart';
import '../../../domain/bloc/app_bar_bloc.dart';
import '../../../domain/bloc/script_manager_bloc.dart';
import 'tool_dropdown_buttol.dart'; // Make sure the file name matches your project structure

class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  final AppBarBloc appBarBloc;
  final Mode currentMode;
  final ScriptManagerBloc scriptManagerBloc;

  const CustomAppBar({
    Key? key,
    required this.scriptManagerBloc,
    required this.appBarBloc,
    required this.currentMode,
  }) : super(key: key);

  @override
  final Size preferredSize = const Size.fromHeight(60.0);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      titleSpacing: 0,
      backgroundColor: Theme.of(context).colorScheme.surface,
      leadingWidth: 250,
      leading: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8.0),
        child: SegmentedButton<Mode>(
          segments: [
            ButtonSegment(
              value: Mode.edit,
              label: Text('Edit'),
            ),
            ButtonSegment(
              value: Mode.review,
              label: Text('Review'),
            ),
            ButtonSegment(
              value: Mode.live,
              label: Text('Live'),
            ),
          ],
          selected: {currentMode},
          onSelectionChanged: (selectedModes) {
            if (selectedModes.isNotEmpty) {
              scriptManagerBloc.add(ModeChanged(selectedModes.first));
            }
          },
          // style: SegmentedButton.styleFrom(
          //   backgroundColor: Theme.of(context).colorScheme.surface,
          //   selectedBackgroundColor: Theme.of(context).colorScheme.primary,
          //   foregroundColor: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
          //   selectedForegroundColor: Colors.white,
          //   shape: RoundedRectangleBorder(
          //     borderRadius: BorderRadius.circular(4.0),
          //   ),
          // ),
          // segmentBuilder: (context, segment, isSelected) {
          //   Color bgColor;
          //   switch (segment.value) {
          //     case Mode.live:
          //       bgColor = isSelected ? Colors.redAccent : Colors.red.withOpacity(0.5);
          //       break;
          //     case Mode.review:
          //       bgColor = isSelected ? Colors.blue : Colors.blue.withOpacity(0.5);
          //       break;
          //     case Mode.edit:
          //       bgColor = isSelected ? Colors.green : Colors.green.withOpacity(0.5);
          //       break;
          //   }
          //   return Container(
          //     padding: const EdgeInsets.symmetric(horizontal: 16),
          //     decoration: BoxDecoration(
          //       color: bgColor,
          //       borderRadius: BorderRadius.circular(4.0),
          //     ),
          //     alignment: Alignment.center,
          //     child: Text(
          //       segment.child.data!,
          //       style: TextStyle(color: isSelected ? Colors.white : Colors.black),
          //     ),
          //   );
          // },
        ),
      ),
      actions: <Widget>[
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
    );
  }
}
