import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../domain/bloc/script_manager_bloc.dart';
import '../../../../../core/constants/app_images.dart';

class IconHelper {
  static Image getIcon(BuildContext context, String assetPath, bool isSelected) {
    return Image.asset(
      assetPath, 
      color: isSelected ? Theme.of(context).colorScheme.onBackground : Theme.of(context).colorScheme.onSurface,
      fit: BoxFit.scaleDown, // Ensures the entire icon is visible within the constraints
    );
  }
}

class InspectorSwitcher extends StatelessWidget {
  final InspectorPanel selectedInspector;
  const InspectorSwitcher({
    Key? key,
    required this.selectedInspector,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SegmentedButton<InspectorPanel>(
      showSelectedIcon: false,
      segments: [
        ButtonSegment(
          value: InspectorPanel.show,
          icon: IconHelper.getIcon(context, ThemeIcons.show, selectedInspector == InspectorPanel.show), // Replaced label with icon
        ),
        ButtonSegment(
          value: InspectorPanel.cues,
          icon: IconHelper.getIcon(context, ThemeIcons.cues, selectedInspector == InspectorPanel.cues), // Replaced label with icon
        ),
        ButtonSegment(
          value: InspectorPanel.notes,
          icon: IconHelper.getIcon(context, ThemeIcons.notes, selectedInspector == InspectorPanel.notes), // Replaced label with icon
        ),
        ButtonSegment(
          value: InspectorPanel.comments,
          icon: IconHelper.getIcon(context, ThemeIcons.comments, selectedInspector == InspectorPanel.comments), // Replaced label with icon
        ),
      ],
      selected: {selectedInspector},
      onSelectionChanged: (Set<InspectorPanel> i) {
        if (i.isNotEmpty) {
          BlocProvider.of<ScriptManagerBloc>(context).add(InspectorChanged(i.first));
        }
      },
      style: ButtonStyle(
        textStyle: MaterialStateProperty.resolveWith((states) => Theme.of(context).textTheme.labelMedium),
        backgroundColor: MaterialStateProperty.resolveWith<Color>((states) {
          if (states.contains(MaterialState.selected)) {
            return Theme.of(context).colorScheme.onSurfaceVariant.withOpacity(.6);
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
        padding: MaterialStateProperty.all(EdgeInsets.symmetric(vertical: 0, horizontal: 18)), // Modified padding for visual spacing
      ),
    );
  }
}
