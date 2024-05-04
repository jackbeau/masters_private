import 'package:flutter/material.dart';
import 'package:pdfrx/pdfrx.dart';
import 'cues.dart';

abstract class Tool {
  bool twoActions = false;
  Tool(this.twoActions);

  Offset cursorOffset = const Offset(0, 0);

  tap(PdfPage page, Offset coordinates, List<Annotation> annotations) {}
  void tap2(PdfPage page, Offset coordinates, List<Annotation> annotations, Annotation annotation) {}
  void down(PdfPage page, Offset cursorPos, Annotation annotation) {}
  void move(Offset delta, Annotation annotation, {PdfPage? page, PdfViewerController? controller}) {}
}

class NewCue extends Tool {
  // final bool twoActions = true; // uses two click actions to add cue label and marker separately
  NewCue() : super(true);

  @override
  tap(PdfPage page, Offset coordinates, List<Annotation> annotations) {
    Cue newCue = Cue(page.pageNumber, coordinates);
    annotations.add(newCue);
    return newCue;
  }

  @override
  void tap2(PdfPage page, Offset coordinates, List<Annotation> annotations, Annotation annotation) {
    if (annotation is Cue) {
      CueMarker newCue = CueMarker(page.pageNumber, coordinates, annotation);
      annotations.add(newCue);
    }
  }

  @override
  void down(PdfPage page, Offset cursorPos, Annotation annotation) {
    if (annotation is Cue) {
      cursorOffset = (annotation.pos-cursorPos);
    }
  }

  @override
  void move(Offset delta, Annotation annotation, {PdfPage? page, PdfViewerController? controller}) {
    if (annotation is Cue) {
      if (page != null) {
        Offset newOffset = _calculateNewOffset(annotation.pos, delta, page, controller!);
        annotation.pos = newOffset;
      } else {
        annotation.pos += delta;
      }
    }
  }

  _calculateNewOffset(Offset currentOffset, Offset delta, PdfPage page, PdfViewerController controller) {
    double newX = currentOffset.dx + delta.dx;
    double newY = currentOffset.dy + delta.dy;
    newX = newX.clamp(0, page.width);
    newY = newY.clamp(0, page.height * controller.pages.length);
    return Offset(newX, newY);
  }
}