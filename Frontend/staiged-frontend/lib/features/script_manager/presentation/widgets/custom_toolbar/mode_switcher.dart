import 'package:flutter/material.dart';
import '../../../domain/bloc/script_manager_bloc.dart';

class ModeSwitcher extends StatelessWidget {
  final Mode currentMode;
  final ScriptManagerBloc scriptManagerBloc;

  const ModeSwitcher({
    Key? key,
    required this.currentMode,
    required this.scriptManagerBloc,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SegmentedButton<Mode>(
      showSelectedIcon: false,
      segments: const [
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
      onSelectionChanged: (Set<Mode> selectedModes) {
        if (selectedModes.isNotEmpty) {
          scriptManagerBloc.add(ModeChanged(selectedModes.first));
        }
      },
      style: ButtonStyle(
        textStyle: MaterialStateProperty.resolveWith((states) => Theme.of(context).textTheme.labelMedium),
        backgroundColor: MaterialStateProperty.resolveWith<Color>((states) {
          if (states.contains(MaterialState.selected)) {
            if (currentMode == Mode.live) {
              return const Color.fromARGB(255, 255, 17, 0); // Red for Live mode when selected
            } else if (currentMode == Mode.review) {
              return Colors.blue; // Blue for Review mode when selected
            } else if (currentMode == Mode.edit) {
              return Colors.green; // Green for Edit mode when selected
            }
          }
          return Theme.of(context).colorScheme.surfaceVariant; // Default non-selected color
        }),
        foregroundColor: MaterialStateProperty.resolveWith<Color>(
          (states) => states.contains(MaterialState.selected)
              ? Theme.of(context).colorScheme.onBackground
              : Theme.of(context).colorScheme.onSurface,
        ),
        shape: MaterialStateProperty.all<RoundedRectangleBorder>(
          RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(4.0),
          ),
        ),
      side: MaterialStateProperty.all(BorderSide.none), // Ensure no border around the segments
      padding: MaterialStateProperty.all(
        EdgeInsets.symmetric(vertical: 0, horizontal: 0), // Add horizontal padding for spacing
      ),
        // outlineColor: MaterialStateProperty.all<Color>(Colors.transparent), // Transparent gap between buttons
      ),
    );
  }
}
