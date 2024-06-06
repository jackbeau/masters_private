// Author: Jack Beaumont
// Date: 06/06/2024

import 'package:flutter/material.dart';
import 'package:logging/logging.dart';

// Initialize logger
final Logger _logger = Logger('ToolDropdownButton');

/// A stateless widget that displays a dropdown button with a list of items.
///
/// The [ToolDropdownButton] takes an icon, a list of items, and a callback
/// function that is triggered when an item is selected.
///
/// Parameters:
/// - [icon]: The icon to be displayed for the dropdown button.
/// - [items]: The list of string items to display in the dropdown menu.
/// - [onSelect]: A callback function that is called with the selected item.
class ToolDropdownButton extends StatelessWidget {
  final IconData icon;
  final List<String> items;
  final Function(String) onSelect;

  /// Creates a [ToolDropdownButton].
  ///
  /// The [icon], [items], and [onSelect] parameters must not be null.
  const ToolDropdownButton({
    super.key, 
    required this.icon, 
    required this.items, 
    required this.onSelect,
  });

  /// Builds the widget.
  ///
  /// Returns a [PopupMenuButton] widget that displays the icon and list of items.
  @override
  Widget build(BuildContext context) {
    return PopupMenuButton<String>(
      icon: Icon(icon, color: Colors.white),
      onSelected: (String choice) {
        _logger.info('Selected item: $choice');
        onSelect(choice);
      },
      itemBuilder: (BuildContext context) {
        return items.map((String choice) {
          return PopupMenuItem<String>(
            value: choice,
            child: Text(choice),
          );
        }).toList();
      },
    );
  }
}
