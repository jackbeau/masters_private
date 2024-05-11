import 'package:flutter/material.dart';
import 'package:pdfrx/pdfrx.dart';
import 'cue.dart'; 
import '../data/models/annotation.dart';
import '../data/models/tag.dart';
import '../data/models/cue_type.dart';
import 'cue_marker.dart';

abstract class Tool {
  final bool twoActions;
  Tool(this.twoActions);

  Offset cursorOffset = const Offset(0, 0);

  tap(PdfPage page, Offset coordinates, List<Annotation> annotations) {}
  void tap2(PdfPage page, Offset coordinates, List<Annotation> annotations, Annotation annotation) {}
  void down(PdfPage page, Offset cursorPos, Annotation annotation) {}
  void move(Offset delta, Annotation annotation, {PdfPage? page, PdfViewerController? controller}) {}
}

class NewCue extends Tool {
  NewCue() : super(true);

  @override
  tap(PdfPage page, Offset coordinates, List<Annotation> annotations) {
    // Define a new CueType for demonstration


    var fs = TagType("FS", Colors.blue);
    var vfx = TagType("VFX", Colors.green);
    // Define some sample Tags
    var tags = [
      Tag("1", fs),
      Tag("3", vfx),
      Tag("5", vfx),
    ];

    Cue newCue = Cue(page.pageNumber, coordinates, goType, tags);
    annotations.add(newCue);
    return newCue;
  }

  @override
  void tap2(PdfPage page, Offset coordinates, List<Annotation> annotations, Annotation annotation) {
    if (annotation is Cue) {
      // Inherit types and tags from the first cue
      CueMarker newCue = CueMarker(page.pageNumber, coordinates, annotation.type, annotation.tags, annotation);
      annotations.add(newCue);
    }
  }

  @override
  void down(PdfPage page, Offset cursorPos, Annotation annotation) {
    if (annotation is Cue) {
      cursorOffset = (annotation.pos - cursorPos);
    }
  }

  @override
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
