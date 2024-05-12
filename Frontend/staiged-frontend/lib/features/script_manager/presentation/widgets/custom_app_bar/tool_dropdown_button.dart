import 'package:flutter/material.dart';

class ToolDropdownButton extends StatelessWidget {
  final IconData icon;
  final List<String> items;
  final Function(String) onSelect;

  const ToolDropdownButton({Key? key, required this.icon, required this.items, required this.onSelect}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return PopupMenuButton<String>(
      icon: Icon(icon, color: Colors.white),
      onSelected: onSelect,
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