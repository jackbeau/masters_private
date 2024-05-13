import 'package:flutter/material.dart';
import 'inspector_panel_a.dart';
import 'inspector_panel_b.dart';
import 'inspector_panel_c.dart';
import '../../../domain/bloc/script_manager_bloc.dart';

class Inspector extends StatelessWidget {
  final InspectorPanel selectedInspector;

  const Inspector({Key? key, required this.selectedInspector}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    switch (selectedInspector) {
      case InspectorPanel.show:
        return InspectorPanelA();
      case InspectorPanel.cues:
        return const InspectorPanelB();
      case InspectorPanel.notes:
        return const InspectorPanelC();
      case InspectorPanel.comments:
        return const InspectorPanelC();
      default:
        return Text('No panel selected');
    }
  }
}
