import 'package:flutter/material.dart';
import 'annotation.dart';
import "../repository/cue_label.dart";

export '../repository/cue_marker.dart';
export '../repository/cue_label.dart';

abstract class Cue extends Annotation {
  final int page;
  Offset pos;

  Cue({
    required this.page,
    required this.pos,
  });

  CueLabel getEffectiveCueLabel();

  @override
  bool isInObject(Annotation annotation, Offset interactionPosition);

  @override
  void draw(Canvas canvas);
}
