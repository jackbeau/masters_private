import 'package:flutter/material.dart';

class InspectorPanelB extends StatelessWidget {
  const InspectorPanelB({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.green[100],
      child: Center(
        child: Text(
          "Tools Panel",
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}
