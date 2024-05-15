import 'package:flutter/material.dart';
import 'package:staiged/features/script_manager/data/models/tag.dart';
import 'cue.dart';
import '../data/models/annotation.dart';

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

  final Cue label;


  CueMarker({
    required int page, 
    required Offset pos, 
    required dynamic type, 
    required List<Tag> tags,
    required this.label
  }) : super(
        page: page, 
        pos: pos, 
        type: type, 
        tags: tags,
      );

 @override
bool isInObject(Annotation annotation, Offset interactionPosition) {
  if (annotation is CueMarker) {
    Path tempPath = Path()
      ..addOval(Rect.fromCircle(
          center: annotation.pos, radius: 10));  // Use annotation.pos
    return tempPath.contains(interactionPosition);
  }
  return false;
}

@override
void draw(Canvas canvas) {
  Offset roundedPos = Offset(pos.dx.roundToDouble(), pos.dy.roundToDouble());

  // Draw connection lines
  canvas.drawLine(
    label.pos + const Offset(0, lineEndOffsetY), 
    Offset(roundedPos.dx, label.pos.dy + lineEndOffsetY),
    linePaint
  );
  canvas.drawLine(
    Offset(roundedPos.dx, roundedPos.dy + radius/2),
    Offset(roundedPos.dx, label.pos.dy + lineEndOffsetY),
    linePaint
  );

  // Draw a circle at the cue marker position
  canvas.drawCircle(roundedPos, radius, circlePaint);
}

}