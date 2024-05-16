import 'package:flutter/material.dart';
import 'package:pdfrx/pdfrx.dart';
import '../models/cue.dart'; 
import '../models/annotation.dart';
import '../models/tag.dart';
import '../models/cue_type.dart';
import 'cue_marker.dart';

class AnnotationInteractionHandler {
  AnnotationInteractionHandler() : super();

  Offset cursorOffset = const Offset(0, 0);

  void down(PdfPage page, Offset cursorPos, Annotation annotation) {
    if (annotation is Cue) {
      cursorOffset = (annotation.pos - cursorPos);
    }
  }

  Annotation? move(Offset delta, Annotation annotation, {PdfPage? page, PdfViewerController? controller}) {
    if (annotation is Cue) {
      if (page != null && controller != null) {
        Offset newOffset = _calculateNewOffset(annotation.pos, delta, page, controller);
        annotation.pos = newOffset;
      } else {
        annotation.pos += delta;
      }
      return annotation;
    }
    return null;
  }

  Offset _calculateNewOffset(Offset currentOffset, Offset delta, PdfPage page, PdfViewerController controller) {
    double newX = currentOffset.dx + delta.dx;
    double newY = currentOffset.dy + delta.dy;
    newX = newX.clamp(0, page.width);
    newY = newY.clamp(0, page.height * controller.pages.length);
    return Offset(newX, newY);
  }
}
