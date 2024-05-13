import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';

class ScriptModeControl extends StatelessWidget {
  final Map<int, Widget> children;
  final int groupValue;
  final ValueChanged<int> onValueChanged;

  const ScriptModeControl({Key? key, required this.children, required this.groupValue, required this.onValueChanged}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return CupertinoSegmentedControl<int>(
      children: children,
      groupValue: groupValue,
      onValueChanged: onValueChanged,
      selectedColor: Theme.of(context).colorScheme.primary,
      borderColor: Theme.of(context).colorScheme.primary,
    );
  }
}