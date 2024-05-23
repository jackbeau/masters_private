import 'package:flutter/material.dart';
import 'annotation.dart';
import '../repository/cue_label.dart';

export '../repository/cue_marker.dart';
export '../repository/cue_label.dart';

abstract class Cue extends Annotation {
  final int page;
  Offset pos;

  Cue({
    required this.page,
    required this.pos,
  }) : super();

  Cue.withId({
    required String id,
    required this.page,
    required this.pos,
  }) : super.withId(id);

  CueLabel getEffectiveCueLabel();

  @override
  bool isInObject(Annotation annotation, Offset interactionPosition);

  @override
  void draw(Canvas canvas);

  @override
  Map<String, dynamic> toJson() {
    final json = super.toJson();
    json.addAll({
      'page': page,
      'pos': {'dx': pos.dx, 'dy': pos.dy},
    });
    return json;
  }

  static Cue fromJson(Map<String, dynamic> json) {
    throw UnimplementedError('fromJson() should be implemented in subclasses');
  }
}
