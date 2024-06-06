/// Author: Jack Beaumont
/// Date: 06/06/2024
/// Description: This file contains the Inspector widget which displays different panels 
/// based on the selected InspectorPanel type.
library;

import 'package:flutter/material.dart';
import 'inspector_cues.dart';
import 'inspector_panel_b.dart';
import 'inspector_panel_c.dart';
import '../../../domain/bloc/script_editor_bloc.dart';

class Inspector extends StatelessWidget {
  final InspectorPanel selectedInspector;

  /// Constructor for the Inspector class.
  /// 
  /// Parameters:
  /// - `selectedInspector`: The panel type to be displayed.
  const Inspector({super.key, required this.selectedInspector});

  @override
  Widget build(BuildContext context) {
    // Return the corresponding widget based on the selectedInspector value.
    switch (selectedInspector) {
      case InspectorPanel.show:
        return const InspectorPanelC();
      case InspectorPanel.cues:
        return const InspectorCues();
      case InspectorPanel.notes:
        return const InspectorPanelB();
      case InspectorPanel.comments:
        return const InspectorPanelC();
      default:
        // Log an error if no valid panel is selected.
        debugPrint('Error: No panel selected'); // Consider using a proper logging package for production code.
        return const Text('No panel selected');
    }
  }
}
