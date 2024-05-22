import 'dart:math';
import 'package:flutter/material.dart';
import '../models/cue_type.dart';
import '../models/tag.dart';
import '../models/annotation.dart';
import '../models/cue.dart';

class CueLabel extends Cue {
  static const double containerRadius = 2;
  static const double tagRadius = 2;
  static const double internalPaddingX = 3;
  static const double containerBorder = 1;
  static const double tagPagddingX = 1;

  final CueType type;
  final List<Tag> tags;
  String note;
  String title;
  bool autofire;
  String line;
  String message;

  CueLabel({
    required int page,
    required Offset pos,
    required this.type,
    required this.tags,
    this.note = "",
    this.title = "",
    this.autofire = false,
    this.line = "",
    this.message = "",
  }) : super(
          page: page,
          pos: pos,
        );

  @override
  CueLabel getEffectiveCueLabel() => this;

  CueLabel copyWith({
    int? page,
    Offset? pos,
    CueType? type,
    List<Tag>? tags,
    String? note,
    String? title,
    bool? autofire,
    String? line,
    String? message,
  }) {
    return CueLabel(
      page: page ?? this.page,
      pos: pos ?? this.pos,
      type: type ?? this.type,
      tags: tags ?? this.tags,
      note: note ?? this.note,
      title: title ?? this.title,
      autofire: autofire ?? this.autofire,
      line: line ?? this.line,
      message: message ?? this.message,
    );
  }

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
    if (annotation is CueLabel) {
      Size size = calculateSize();
      Path tempPath = Path()
        ..addRRect(RRect.fromRectAndRadius(
          Rect.fromCenter(center: pos, width: size.width + internalPaddingX, height: size.height + internalPaddingX),
          const Radius.circular(containerRadius),
        ));
      return tempPath.contains(interactionPosition);
    }
    return false;
  }

  void drawMarker(Canvas canvas, Offset pos) {
    Size size = calculateSize();
    final rectOverall = RRect.fromRectAndRadius(
      Rect.fromCenter(center: pos, width: size.width + containerBorder, height: size.height + containerBorder),
      const Radius.circular(internalPaddingX),
    );

    // Draw background for main text
    final paintOverall = Paint()..color = type.color;
    canvas.drawRRect(rectOverall, paintOverall);

    // Draw the border
    final borderPaint = Paint()
      ..color = Colors.black
      ..style = PaintingStyle.stroke
      ..strokeWidth = containerBorder;
    canvas.drawRRect(rectOverall, borderPaint);

    // Positioning calculations
    double offsetX = 3;
    TextPainter labelTypePainter;
    if (autofire == true) {
      labelTypePainter = createTextPainter("AUTO", labelStyle);
    } else {
      labelTypePainter = createTextPainter(type.text, labelStyle);
    }

    if (type.side == 'l') {
      labelTypePainter.paint(canvas, Offset(pos.dx - size.width / 2 + offsetX, pos.dy - labelTypePainter.height / 2));
      offsetX += labelTypePainter.width + 3;
    } else {
      labelTypePainter.paint(canvas, Offset(pos.dx + size.width / 2 - labelTypePainter.width - internalPaddingX * 2 + offsetX, pos.dy - labelTypePainter.height / 2));
      offsetX -= offsetX;
    }

    // Draw tags with their backgrounds
    for (var tag in tags) {
      if (tag.type != null) {
        final tagPainter = createTextPainter("${tag.type?.department} ${tag.cue_name}", labelStyle);
        final tagWidth = tagPainter.width + 6;
        final tagRect = RRect.fromRectAndRadius(
          Rect.fromLTWH(pos.dx - size.width / 2 + offsetX, pos.dy - size.height / 2, tagWidth, size.height),
          Radius.circular(tagRadius),
        );
        final paintTag = Paint()..color = tag.type!.color;
        canvas.drawRRect(tagRect, paintTag);
        tagPainter.paint(canvas, Offset(pos.dx - size.width / 2 + offsetX + internalPaddingX, pos.dy - tagPainter.height / 2));
        offsetX += tagWidth + tagPagddingX;
      }
    }
    final notePainter = createTextPainter(note, noteStyle, maxLines: 3, maxWidth: 120);
    notePainter.paint(canvas, Offset(pos.dx + size.width / 2 + 4, pos.dy + size.height / 2 - notePainter.height));
  }

  Size calculateSize() {
    double totalWidth = internalPaddingX * 2;
    double totalHeight = 0;

    TextPainter labelTypePainter;
    if (autofire == true) {
      labelTypePainter = createTextPainter("AUTO", labelStyle);
    } else {
      labelTypePainter = createTextPainter(type.text, labelStyle);
    }
    totalWidth += labelTypePainter.width;
    totalHeight = max(totalHeight, labelTypePainter.height);

    for (var tag in tags) {
      if (tag.type != null) {
        final tagPainter = createTextPainter("${tag.type?.department} ${tag.cue_name}", labelStyle);
        totalWidth += tagPainter.width + internalPaddingX * 2;
        totalHeight = max(totalHeight, tagPainter.height);
      }
    }

    totalWidth += (tags.length - 1) * tagPagddingX;
    totalHeight += 1;

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
