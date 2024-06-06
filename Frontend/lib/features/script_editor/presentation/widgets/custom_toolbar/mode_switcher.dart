/*
 * Author: Jack Beaumont
 * Date: 06/06/2024
 *
 * This widget defines a ModeSwitcher for selecting different modes (Edit, Review, Live)
 * and handles the logic for updating the mode in the ScriptEditorBloc.
 */

import 'package:flutter/material.dart';
import '../../../domain/bloc/script_editor_bloc.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

class ModeSwitcher extends StatelessWidget {
  final Mode currentMode;

  // Constructor for ModeSwitcher
  const ModeSwitcher({
    super.key,
    required this.currentMode,
  });

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
          // Dispatch a ModeChanged event to the ScriptEditorBloc when a mode is selected
          BlocProvider.of<ScriptEditorBloc>(context).add(ModeChanged(selectedModes.first));
        }
      },
      style: ButtonStyle(
        textStyle: MaterialStateProperty.resolveWith(
          (states) => Theme.of(context).textTheme.labelMedium,
        ),
        backgroundColor: MaterialStateProperty.resolveWith<Color>(
          (states) {
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
          },
        ),
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
          const EdgeInsets.symmetric(vertical: 0, horizontal: 0), // Add horizontal padding for spacing
        ),
      ),
    );
  }
}
