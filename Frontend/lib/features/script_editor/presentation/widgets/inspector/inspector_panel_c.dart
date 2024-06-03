import 'package:flutter/material.dart';

class InspectorPanelC extends StatelessWidget {
  const InspectorPanelC({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.red[100],
      child: const Center(
        child: Text(
          "Settings Panel",
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}
