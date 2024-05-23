import 'package:flutter/material.dart';
import 'annotation.dart';

class CueMarker extends Annotation {
  static const double radius = 10;
  static const Color circleColor = Color(0xFF0099FF);
  static final Paint circlePaint = Paint()
    ..color = circleColor
    ..isAntiAlias = true;

  final int page;
  Offset pos;

  CueMarker({
    required this.page,
    required this.pos,
  }) : super();

  CueMarker.withId({
    required String id,
    required this.page,
    required this.pos,
  }) : super.withId(id);

  @override
  bool isInObject(Annotation annotation, Offset interactionPosition) {
    if (annotation is CueMarker) {
      Path tempPath = Path()
        ..addOval(Rect.fromCircle(center: annotation.pos, radius: radius)); // Use annotation.pos
      return tempPath.contains(interactionPosition);
    }
    return false;
  }

  @override
  void draw(Canvas canvas) {
    Offset roundedPos = Offset(pos.dx.roundToDouble(), pos.dy.roundToDouble());

    // Draw a circle at the cue marker position
    canvas.drawCircle(roundedPos, radius, circlePaint);
  }

  @override
  Map<String, dynamic> toJson() {
    final json = super.toJson();
    json.addAll({
      'page': page,
      'pos': {'dx': pos.dx, 'dy': pos.dy},
    });
    return json;
  }

  factory CueMarker.fromJson(Map<String, dynamic> json) {
    return CueMarker.withId(
      id: json['id'],
      page: json['page'],
      pos: Offset(json['pos']['dx'], json['pos']['dy']),
    );
  }
}
