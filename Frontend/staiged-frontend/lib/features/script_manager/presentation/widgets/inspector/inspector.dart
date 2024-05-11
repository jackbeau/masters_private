import 'package:flutter/material.dart';
import 'inspector_panel_a.dart';
import 'inspector_panel_b.dart';
import 'inspector_panel_c.dart';

class Inspector extends StatelessWidget {
  final int selectedPanel;

  const Inspector({Key? key, required this.selectedPanel}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    switch (selectedPanel) {
      case 0:
        return InspectorPanelA();
      case 1:
        return const InspectorPanelB();
      case 2:
        return const InspectorPanelC();
      default:
        return Text('No panel selected');
    }
  }
}
