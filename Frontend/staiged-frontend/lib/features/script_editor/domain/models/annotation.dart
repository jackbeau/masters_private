import 'package:flutter/material.dart';

abstract class Annotation {
  void draw(Canvas canvas);
  bool isInObject(Annotation annotation, Offset interactionPosition);
  final UniqueKey id = UniqueKey();
} 