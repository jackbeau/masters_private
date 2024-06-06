/// Author: Jack Beaumont
/// Date: 06/06/2024
library;

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:logging/logging.dart';

import '../../../domain/bloc/script_editor_bloc.dart';
import '../../../../../core/constants/app_images.dart';

final Logger _logger = Logger('InspectorSwitcher');

/// Helper class to manage icons
class IconHelper {
  /// Returns an Image widget for the given asset path,
  /// changing color based on selection status
  ///
  /// Parameters:
  /// - [context]: BuildContext to access theme data
  /// - [assetPath]: Path to the icon asset
  /// - [isSelected]: Boolean indicating if the icon is selected
  ///
  /// Returns:
  /// - [Image]: The configured Image widget
  static Image getIcon(
      BuildContext context, String assetPath, bool isSelected) {
    return Image.asset(
      assetPath,
      color: isSelected
          ? Theme.of(context).colorScheme.onBackground
          : Theme.of(context).colorScheme.onSurface,
      fit: BoxFit
          .scaleDown, // Ensures the entire icon is visible within the constraints
    );
  }
}

/// A widget to switch between different inspector panels
class InspectorSwitcher extends StatelessWidget {
  final InspectorPanel selectedInspector;

  /// Constructor for InspectorSwitcher
  ///
  /// Parameters:
  /// - [selectedInspector]: The currently selected inspector panel
  const InspectorSwitcher({
    super.key,
    required this.selectedInspector,
  });

  @override
  Widget build(BuildContext context) {
    return SegmentedButton<InspectorPanel>(
      showSelectedIcon: false,
      segments: [
        ButtonSegment(
          value: InspectorPanel.show,
          icon: IconHelper.getIcon(context, ThemeIcons.show,
              selectedInspector == InspectorPanel.show),
        ),
        ButtonSegment(
          value: InspectorPanel.cues,
          icon: IconHelper.getIcon(context, ThemeIcons.cues,
              selectedInspector == InspectorPanel.cues),
        ),
        ButtonSegment(
          value: InspectorPanel.notes,
          icon: IconHelper.getIcon(context, ThemeIcons.notes,
              selectedInspector == InspectorPanel.notes),
        ),
        ButtonSegment(
          value: InspectorPanel.comments,
          icon: IconHelper.getIcon(context, ThemeIcons.comments,
              selectedInspector == InspectorPanel.comments),
        ),
      ],
      selected: {selectedInspector},
      onSelectionChanged: (Set<InspectorPanel> i) {
        if (i.isNotEmpty) {
          _logger.fine('Inspector selection changed: ${i.first}');
          BlocProvider.of<ScriptEditorBloc>(context)
              .add(InspectorChanged(i.first));
        }
      },
      style: ButtonStyle(
        textStyle: MaterialStateProperty.resolveWith(
            (states) => Theme.of(context).textTheme.labelMedium),
        backgroundColor: MaterialStateProperty.resolveWith<Color>((states) {
          if (states.contains(MaterialState.selected)) {
            return Theme.of(context)
                .colorScheme
                .onSurfaceVariant
                .withOpacity(.6);
          }
          return Theme.of(context).colorScheme.surfaceVariant;
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
        side: MaterialStateProperty.all(BorderSide.none),
        padding: MaterialStateProperty.all(const EdgeInsets.symmetric(
            vertical: 0,
            horizontal: 18)), // Modified padding for visual spacing
      ),
    );
  }
}
