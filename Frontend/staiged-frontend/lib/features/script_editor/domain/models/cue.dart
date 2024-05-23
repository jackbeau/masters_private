import 'dart:math';
import 'package:flutter/material.dart';
import 'annotation.dart';
import 'cue_type.dart';
import 'tag.dart';
import 'cue_marker.dart';

class Cue extends Annotation {
  static const double containerRadius = 2;
  static const double tagRadius = 2;
  static const double internalPaddingX = 3;
  static const double containerBorder = 1;
  static const double tagPaddingX = 1;
  static const double markerRadius = 10;
  static const double lineEndOffsetY = 8.5;
  static const Color defaultLineColor = Color.fromARGB(255, 0, 0, 0);
  static final Paint linePaint = Paint()
    ..color = defaultLineColor
    ..isAntiAlias = true
    ..strokeWidth = 1;

  final int page;
  Offset pos;
  final CueType type;
  final List<Tag> tags;
  String note;
  String title;
  bool autofire;
  String line;
  String message;
  CueMarker? marker; // Optional CueMarker field

  Cue({
    required this.page,
    required this.pos,
    required this.type,
    required this.tags,
    this.note = "",
    this.title = "",
    this.autofire = false,
    this.line = "",
    this.message = "",
    this.marker,
  }) : super();

  Cue.withId({
    required String id,
    required this.page,
    required this.pos,
    required this.type,
    required this.tags,
    this.note = "",
    this.title = "",
    this.autofire = false,
    this.line = "",
    this.message = "",
    this.marker,
  }) : super.withId(id);

  Cue copyWith({
    int? page,
    Offset? pos,
    CueType? type,
    List<Tag>? tags,
    String? note,
    String? title,
    bool? autofire,
    String? line,
    String? message,
    CueMarker? marker,
  }) {
    return Cue.withId(
      id: id,
      page: page ?? this.page,
      pos: pos ?? this.pos,
      type: type ?? this.type,
      tags: tags ?? this.tags,
      note: note ?? this.note,
      title: title ?? this.title,
      autofire: autofire ?? this.autofire,
      line: line ?? this.line,
      message: message ?? this.message,
      marker: marker ?? this.marker,
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
    drawLabel(canvas, pos);

    if (marker != null) {
      drawMarkerConnectionLines(canvas, marker!.pos);
      marker!.draw(canvas);
    }
  }

  void drawLabel(Canvas canvas, Offset pos) {
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
    if (autofire) {
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
        offsetX += tagWidth + tagPaddingX;
      }
    }
    final notePainter = createTextPainter(note, noteStyle, maxLines: 3, maxWidth: 120);
    notePainter.paint(canvas, Offset(pos.dx + size.width / 2 + 4, pos.dy + size.height / 2 - notePainter.height));
  }

  void drawMarkerConnectionLines(Canvas canvas, Offset markerPos) {
    Offset roundedMarkerPos = Offset(markerPos.dx.roundToDouble(), markerPos.dy.roundToDouble());
    Offset roundedCuePos = Offset(pos.dx.roundToDouble(), pos.dy.roundToDouble());

    // Draw connection lines
    canvas.drawLine(
      roundedCuePos + const Offset(0, lineEndOffsetY),
      Offset(roundedMarkerPos.dx, roundedCuePos.dy + lineEndOffsetY),
      linePaint,
    );
    canvas.drawLine(
      Offset(roundedMarkerPos.dx, roundedMarkerPos.dy + markerRadius / 2),
      Offset(roundedMarkerPos.dx, roundedCuePos.dy + lineEndOffsetY),
      linePaint,
    );
  }

  @override
  bool isInObject(Annotation annotation, Offset interactionPosition) {
    Size size = calculateSize();
    Path cuePath = Path()
      ..addRRect(RRect.fromRectAndRadius(
        Rect.fromCenter(center: pos, width: size.width + internalPaddingX, height: size.height + internalPaddingX),
        const Radius.circular(containerRadius),
      ));
    if (cuePath.contains(interactionPosition)) {
      return true;
    }
    if (marker != null && marker!.isInObject(marker!, interactionPosition)) {
      return true;
    }
    return false;
  }


  Size calculateSize() {
    double totalWidth = internalPaddingX * 2;
    double totalHeight = 0;

    TextPainter labelTypePainter;
    if (autofire) {
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

    totalWidth += (tags.length - 1) * tagPaddingX;
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

  @override
  Map<String, dynamic> toJson() {
    final json = super.toJson();
    json.addAll({
      'page': page,
      'pos': {'dx': pos.dx, 'dy': pos.dy},
      'type': type.toJson(),
      'tags': tags.map((tag) => tag.toJson()).toList(),
      'note': note,
      'title': title,
      'autofire': autofire,
      'line': line,
      'message': message,
      'marker': marker?.toJson(),
    });
    return json;
  }

  factory Cue.fromJson(Map<String, dynamic> json) {
    return Cue.withId(
      id: json['id'],
      page: json['page'],
      pos: Offset(json['pos']['dx'], json['pos']['dy']),
      type: CueType.fromJson(json['type']),
      tags: (json['tags'] as List).map((tag) => Tag.fromJson(tag)).toList(),
      note: json['note'] ?? '',
      title: json['title'] ?? '',
      autofire: json['autofire'] ?? false,
      line: json['line'] ?? '',
      message: json['message'] ?? '',
      marker: json['marker'] != null ? CueMarker.fromJson(json['marker']) : null,
    );
  }
}
