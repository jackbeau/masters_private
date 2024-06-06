// Author: Jack Beaumont
// Date: 06/06/2024
// Description: This file defines the ScriptModeControl widget, a custom CupertinoSegmentedControl 
//              used for script mode selection in the application.

import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'package:logging/logging.dart';

// Initialize the logger
final Logger _logger = Logger('ScriptModeControl');

class ScriptModeControl extends StatelessWidget {
  final Map<int, Widget> children;
  final int groupValue;
  final ValueChanged<int> onValueChanged;

  /// Constructs a ScriptModeControl widget.
  /// 
  /// Parameters:
  /// - [children]: A map of integers to Widgets representing the segments.
  /// - [groupValue]: The currently selected segment.
  /// - [onValueChanged]: A callback triggered when the selected segment changes.
  const ScriptModeControl({
    super.key, 
    required this.children, 
    required this.groupValue, 
    required this.onValueChanged,
  });

  @override
  Widget build(BuildContext context) {
    _logger.info('Building ScriptModeControl widget');

    return CupertinoSegmentedControl<int>(
      children: children,
      groupValue: groupValue,
      onValueChanged: (int newValue) {
        _logger.info('Segment changed to $newValue');
        onValueChanged(newValue);
      },
      selectedColor: Theme.of(context).colorScheme.primary,
      borderColor: Theme.of(context).colorScheme.primary,
    );
  }
}
