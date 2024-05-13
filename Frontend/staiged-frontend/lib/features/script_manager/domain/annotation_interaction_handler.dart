import 'package:flutter/material.dart';
import 'package:pdfrx/pdfrx.dart';
import 'cue.dart'; 
import '../data/models/annotation.dart';
import '../data/models/tag.dart';
import '../data/models/cue_type.dart';
import 'cue_marker.dart';

class AnnotationInteractionHandler {
  AnnotationInteractionHandler() : super();

  Offset cursorOffset = const Offset(0, 0);

  void down(PdfPage page, Offset cursorPos, Annotation annotation) {
    if (annotation is Cue) {
      cursorOffset = (annotation.pos - cursorPos);
    }
  }

  void move(Offset delta, Annotation annotation, {PdfPage? page, PdfViewerController? controller}) {
    if (annotation is Cue) {
      if (page != null && controller != null) {
        Offset newOffset = _calculateNewOffset(annotation.pos, delta, page, controller);
        annotation.pos = newOffset;
      } else {
        annotation.pos += delta;
      }
    }
  }

  Offset _calculateNewOffset(Offset currentOffset, Offset delta, PdfPage page, PdfViewerController controller) {
    double newX = currentOffset.dx + delta.dx;
    double newY = currentOffset.dy + delta.dy;
    newX = newX.clamp(0, page.width);
    newY = newY.clamp(0, page.height * controller.pages.length);
    return Offset(newX, newY);
  }
}
