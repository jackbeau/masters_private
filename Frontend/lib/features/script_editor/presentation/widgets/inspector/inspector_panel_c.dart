/// 
/// Author: Jack Beaumont
/// Date: 06/06/2024
/// 
/// This file contains the definition for the InspectorPanelC widget,
/// which is a simple settings panel with centered text.
/// 
library;

import 'package:flutter/material.dart';
import 'package:logging/logging.dart';

/// A stateless widget that represents a settings panel with centered text.
class InspectorPanelC extends StatelessWidget {
  const InspectorPanelC({super.key});

  /// Builds the widget tree for the InspectorPanelC.
  /// 
  /// This widget displays a container with a light red background color
  /// and a centered text "Settings Panel".
  /// 
  /// - Parameter context: The build context.
  /// - Returns: A widget tree with a red container and centered text.
  @override
  Widget build(BuildContext context) {
    // Logger instance
    final log = Logger('InspectorPanelC');

    // Logging the build method call
    log.info('Building InspectorPanelC widget');

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
