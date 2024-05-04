import 'package:flutter/material.dart';
import 'package:pdfrx/pdfrx.dart';

abstract class Annotation {
  void draw(Canvas canvas) {}
}


class Cue extends Annotation {
  final UniqueKey id = UniqueKey();
  final int page;
  Offset pos;
  final double radius = 10;

  Cue(this.page, this.pos);

  @override
  void draw(Canvas canvas) {
    canvas.drawCircle(
      pos,
      10, 
      Paint()..color = const Color(0xFF0099FF)
    );
  }
}

class CueMarker extends Cue {
  Cue label;
  CueMarker(super.page, super.pos, this.label);

@override
  void draw(Canvas canvas) {
    canvas.drawCircle(
      label.pos,
      10, 
      Paint()..color = const Color(0xFF0099FF)
    );
    canvas.drawLine(
      label.pos + const Offset(0, 10), 
      Offset(pos!.dx, label.pos.dy+10),
      Paint()..color = const Color.fromARGB(255, 0, 0, 0)
    );
    canvas.drawLine(
      Offset(pos!.dx, pos!.dy+10),
      Offset(pos!.dx, label.pos.dy+10),
      Paint()..color = const Color.fromARGB(255, 0, 0, 0)
    );
    canvas.drawCircle(
      pos!,
      10, 
      Paint()..color = const Color(0xFF0099FF)
    );
    paint(canvas, const Size(300, 300));
  }
}

void paint(Canvas canvas, Size size) {
  const textStyle = TextStyle(
    color: Colors.black,
    fontSize: 12,
  );
  const textSpan = TextSpan(
    text: 'Hello, world.',
    style: textStyle,
  );
  final textPainter = TextPainter(
    text: textSpan,
    textDirection: TextDirection.ltr,
  );
  textPainter.layout(
    minWidth: 0,
    maxWidth: size.width,
  );
  final xCenter = (size.width - textPainter.width) / 2;
  final yCenter = (size.height - textPainter.height) / 2;
  final offset = Offset(xCenter, yCenter);
  textPainter.paint(canvas, offset);
}