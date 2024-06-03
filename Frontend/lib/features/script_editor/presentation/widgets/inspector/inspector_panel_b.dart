import 'package:flutter/material.dart';

class InspectorPanelB extends StatelessWidget {
  const InspectorPanelB({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.green[100],
      child: const Center(
        child: Text(
          "Tools Panel",
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}
