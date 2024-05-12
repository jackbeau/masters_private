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
        backgroundColor: MaterialStateProperty.resolveWith<Color>((states) {
          if (states.contains(MaterialState.selected)) {
            if (currentMode == Mode.live) {
              return Colors.red; // Red for Live mode when selected
            } else if (currentMode == Mode.review) {
              return Colors.blue; // Blue for Review mode when selected
            } else if (currentMode == Mode.edit) {
              return Colors.green; // Green for Edit mode when selected
            }
          }
          return Theme.of(context).colorScheme.surface; // Default non-selected color
        }),
        foregroundColor: MaterialStateProperty.resolveWith<Color>(
          (states) => states.contains(MaterialState.selected)
              ? Colors.white
              : Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
        ),
        shape: MaterialStateProperty.all<RoundedRectangleBorder>(
          RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(4.0),
          ),
        ),
        padding: MaterialStateProperty.all(EdgeInsets.symmetric(vertical: 0, horizontal: 0)),
      ),
    );
  }
}
