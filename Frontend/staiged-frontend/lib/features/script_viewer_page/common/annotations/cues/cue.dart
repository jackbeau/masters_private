import 'dart:math';
import 'package:flutter/material.dart';
import 'models/cue_type.dart';
import 'models/tag.dart';
import '../annotation.dart';

class Cue extends Annotation {
  static const double containerRadius = 2;
  static const double tagRadius = 2;
  static const double internalPaddingX = 3;
  static const double containerBorder = 1;
  static const double tagPagddingX = 1;
  final UniqueKey id = UniqueKey();
  final int page;
  Offset pos;
  final CueType type;
  final List<Tag> tags;
  String note;

  Cue(this.page, this.pos, this.type, this.tags, {this.note = "Loewm ispum dolor set amiet time we test some lomg stuff"});

  static const TextStyle labelStyle = TextStyle(
    fontSize: 12,
    decoration: TextDecoration.none,
    fontStyle: FontStyle.normal,
    fontWeight: FontWeight.w500,
    height: 16 / 13,
    letterSpacing: 0.15,
    color: Colors.white,
  );

  static const TextStyle noteStyle = TextStyle(
    fontSize: 12,
    decoration: TextDecoration.none,
    fontStyle: FontStyle.normal,
    fontWeight: FontWeight.w500,
    height: 16 / 13,
    letterSpacing: 0.15,
    color: Colors.black,
  );

  @override
  void draw(Canvas canvas) {
    pos = Offset(pos.dx.roundToDouble(), pos.dy.roundToDouble());
    drawMarker(canvas, pos);
  }

  @override
  bool isInObject(Annotation annotation, Offset interactionPosition) {
    if (annotation is Cue) {
      Size size = calculateSize();
      Path tempPath = Path()
        ..addRRect(RRect.fromRectAndRadius(
          Rect.fromCenter(center:pos, width:size.width+internalPaddingX, height:size.height+internalPaddingX),
          const Radius.circular(containerRadius)));
      return tempPath.contains(interactionPosition);
    }
    return false;
  }

  void drawMarker(Canvas canvas, Offset pos) {
    Size size = calculateSize();
    final rectOverall = RRect.fromRectAndRadius(
      Rect.fromCenter(center: pos, width: size.width+containerBorder, height: size.height+containerBorder),
      const Radius.circular(internalPaddingX),
    );

    // Draw background for main text
    final paintOverall = Paint()..color = type.color;  // Use a consistent color variable like Colors.black instead of Color.fromARGB
    canvas.drawRRect(rectOverall, paintOverall);

    // Draw the border
    final borderPaint = Paint()
      ..color = Colors.black
      ..style = PaintingStyle.stroke  // Set the paint to stroke
      ..strokeWidth = containerBorder;  // Width of the border
    canvas.drawRRect(rectOverall, borderPaint);

    // Positioning calculations
    double offsetX = 3;
    final labelTypePainter = createTextPainter(type.text, labelStyle);
    
    if (type.side == 'l') {
      labelTypePainter.paint(canvas, Offset(pos.dx - size.width / 2 + offsetX, pos.dy - labelTypePainter.height / 2));
      offsetX += labelTypePainter.width + 3;  // Start from right-most tag if side is 'r'
    }
    else {
      labelTypePainter.paint(canvas, Offset(pos.dx + size.width/2 - labelTypePainter.width - internalPaddingX*2 + offsetX, pos.dy - labelTypePainter.height / 2));
      offsetX -= offsetX;
    }

    // Draw tags with their backgrounds
    for (var tag in tags) {
      final tagPainter = createTextPainter("${tag.type.name} ${tag.name}", labelStyle);
      final tagWidth = tagPainter.width + 6; // additional padding for tags
      final tagRect = RRect.fromRectAndRadius(
        Rect.fromLTWH(pos.dx - size.width / 2 + offsetX, pos.dy - size.height / 2, tagWidth, size.height),
        Radius.circular(tagRadius),
      );
      final paintTag = Paint()..color = tag.type.color;
      canvas.drawRRect(tagRect, paintTag);
      tagPainter.paint(canvas, Offset(pos.dx - size.width / 2 + offsetX + internalPaddingX, pos.dy - tagPainter.height / 2));
      offsetX += tagWidth + tagPagddingX; // Space between tags
    }
    final notePainter = createTextPainter(note, noteStyle, maxLines: 3, maxWidth: 120);
    notePainter.paint(canvas, Offset(pos.dx + size.width / 2 + 4, pos.dy + size.height/2 - notePainter.height ));
  }

  Size calculateSize() {
    double totalWidth = internalPaddingX * 2; // Start with padding for the main text
    double totalHeight = 0;

    final labelTypePainter = createTextPainter(type.text, labelStyle);
    totalWidth += labelTypePainter.width;
    totalHeight = max(totalHeight, labelTypePainter.height);

    for (var tag in tags) {
      final tagPainter = createTextPainter("${tag.type.name} ${tag.name}", labelStyle);
      totalWidth += tagPainter.width + internalPaddingX * 2; // Add padding for each tag
      totalHeight = max(totalHeight, tagPainter.height);
    }

    totalWidth += (tags.length - 1) * tagPagddingX; // Add space between tags
    totalHeight += 1; // Small adjustment for padding

    return Size(totalWidth, totalHeight);
  }

  TextPainter createTextPainter(String text, TextStyle style, {int maxLines = 1, double maxWidth = double.infinity}) {
    return TextPainter(
      text: TextSpan(text: text, style: style),
      maxLines: maxLines,
      textDirection: TextDirection.ltr,
    )..layout(minWidth: 0, maxWidth: maxWidth);
  }
}