import 'package:flutter/material.dart';
import 'inspector_cues.dart';
import 'inspector_panel_b.dart';
import 'inspector_panel_c.dart';
import '../../../domain/bloc/script_editor_bloc.dart';

class Inspector extends StatelessWidget {
  final InspectorPanel selectedInspector;

  const Inspector({super.key, required this.selectedInspector});

  @override
  Widget build(BuildContext context) {
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
        return const Text('No panel selected');
    }
  }
}
