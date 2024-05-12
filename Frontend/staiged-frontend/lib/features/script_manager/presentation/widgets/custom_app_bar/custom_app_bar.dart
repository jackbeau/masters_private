import 'package:flutter/material.dart';
import '../../../domain/bloc/app_bar_bloc.dart';
import 'script_mode_control.dart';
import 'tool_dropdown_buttol.dart'; 

class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  final int segmentedControlValue;
  final Function(int) onSegmentChanged;
  final AppBarBloc appBarBloc; // This is received from the parent and should be provided by BlocProvider

  CustomAppBar({
    Key? key,
    required this.segmentedControlValue,
    required this.onSegmentChanged,
    required this.appBarBloc,
  }) : super(key: key);

  @override
  final Size preferredSize = const Size.fromHeight(60.0); // Adjust the height as necessary

  @override
  Widget build(BuildContext context) {
    return AppBar(
      titleSpacing: 0,
      backgroundColor: Theme.of(context).colorScheme.surface,
      leadingWidth: 250, // Adjust based on your UI design
      leading: ScriptModeControl(
        children: const {
          0: Text('Review'),
          1: Text('Edit'),
          2: Text('Live'),
        },
        groupValue: segmentedControlValue,
        onValueChanged: (int newValue) => onSegmentChanged(newValue),
      ),
      actions: <Widget>[
        ToolDropdownButton(
          icon: Icons.edit,
          items: ['Black', 'Red', 'Green'],
          onSelect: (String color) {
            // Handle color change
          },
        ),
        IconButton(
          icon: Icon(Icons.search, color: Colors.white),
          onPressed: () {
            // Implement search functionality
          },
        ),
        IconButton(
          icon: Icon(Icons.zoom_in, color: Colors.white),
          onPressed: () => appBarBloc.add(ZoomIn()),
        ),
        IconButton(
          icon: Icon(Icons.camera_alt, color: Colors.white),
          onPressed: () {
            // Implement camera view functionality
          },
        ),
        // Include other buttons and functionalities as needed
      ],
    );
  }
}
