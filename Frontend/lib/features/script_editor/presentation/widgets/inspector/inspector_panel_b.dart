/// 
/// Author: Jack Beaumont
/// Date: 06/06/2024
/// 
/// This file contains the definition for the InspectorPanelB widget,
/// which is a simple tools panel with centered text.
/// 
library;

import 'package:flutter/material.dart';
import 'package:logging/logging.dart';

/// A stateless widget that represents a tools panel with centered text.
class InspectorPanelB extends StatelessWidget {
  const InspectorPanelB({super.key});

  /// Builds the widget tree for the InspectorPanelB.
  /// 
  /// This widget displays a container with a light green background color
  /// and a centered text "Tools Panel".
  /// 
  /// - Parameter context: The build context.
  /// - Returns: A widget tree with a green container and centered text.
  @override
  Widget build(BuildContext context) {
    // Logger instance
    final log = Logger('InspectorPanelB');

    // Logging the build method call
    log.info('Building InspectorPanelB widget');

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
