import 'package:flutter/material.dart';
import 'cue.dart';
import '../annotation.dart';

class CueMarker extends Cue {
  static const double radius = 10;
  static const double lineEndOffsetY = 8.5;
  static const Color defaultLineColor = Color.fromARGB(255, 0, 0, 0);
  static const Color circleColor = Color(0xFF0099FF);
  static final Paint linePaint = Paint()
    ..color = defaultLineColor
    ..isAntiAlias = true
    ..strokeWidth = 1;
  static final Paint circlePaint = Paint()
    ..color = circleColor
    ..isAntiAlias = true;

  Cue label;

  CueMarker(super.page, super.pos, super.type, super.tags, this.label);

  @override
  bool isInObject(Annotation annotation, Offset interactionPosition) {
    if (annotation is CueMarker) {
       Path tempPath = Path()
        ..addOval(Rect.fromCircle(
            center: pos, radius: 10));
      return tempPath.contains(interactionPosition);
    }
    return false;
  }

  @override
  void draw(Canvas canvas) {
    pos = Offset(pos.dx.roundToDouble(), pos.dy.roundToDouble());

    // Draw connection lines
    canvas.drawLine(
      label.pos + const Offset(0, lineEndOffsetY), 
      Offset(pos.dx, label.pos.dy + lineEndOffsetY),
      linePaint
    );
    canvas.drawLine(
      Offset(pos.dx, pos.dy + radius/2),
      Offset(pos.dx, label.pos.dy + lineEndOffsetY),
      linePaint
    );

    // Draw a circle at the cue marker position
    canvas.drawCircle(pos, radius, circlePaint);
  }
}
