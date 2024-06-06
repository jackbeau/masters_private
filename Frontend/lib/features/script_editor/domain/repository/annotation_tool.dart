/// Annotation Tool Implementation
///
/// Author: Jack Beaumont
/// Date: 06/06/2024
library;

import 'package:flutter/material.dart';
import 'package:pdfrx/pdfrx.dart';
import '../models/cue.dart';
import '../models/annotation.dart';
import '../models/tag.dart';
import '../models/cue_type.dart';
import '../models/cue_marker.dart';
import 'package:logging/logging.dart';

// Initialize the logger
final _logger = Logger('AnnotationTool');

/// Abstract base class for annotation tools.
abstract class AnnotationToolBase {
  final bool twoActions;

  AnnotationToolBase(this.twoActions);

  Offset cursorOffset = const Offset(0, 0);

  /// Method to handle the first tap action.
  ///
  /// [page] The PDF page where the tap occurred.
  /// [coordinates] The coordinates of the tap.
  /// Returns an [Annotation] if a new annotation is created, otherwise null.
  Annotation? tap(PdfPage page, Offset coordinates);

  /// Method to handle the second tap action.
  ///
  /// [page] The PDF page where the tap occurred.
  /// [coordinates] The coordinates of the tap.
  /// [annotation] The existing annotation to be modified.
  /// Returns an [Annotation] if the annotation is updated, otherwise null.
  Annotation? tap2(PdfPage page, Offset coordinates, Annotation annotation);
}

/// Class for creating a new cue annotation.
class NewCue extends AnnotationToolBase {
  NewCue() : super(true);

  /// Handles the first tap to create a new cue.
  ///
  /// [page] The PDF page where the tap occurred.
  /// [coordinates] The coordinates of the tap.
  /// Returns a [Cue] if a new cue is created, otherwise null.
  @override
  Annotation? tap(PdfPage page, Offset coordinates) {
    _logger.info(
        'Creating a new cue at page ${page.pageNumber} at position $coordinates');

    // Define some sample Tags
    var tags = [
      Tag(cueName: "1", type: fs),
      Tag(cueName: "3", type: vfx),
      Tag(cueName: "5", type: vfx),
    ];

    Cue newCue = Cue(
        page: page.pageNumber,
        pos: coordinates,
        type: goType,
        tags: tags,
        note: "on clap");
    return newCue;
  }

  /// Handles the second tap to modify an existing cue.
  ///
  /// [page] The PDF page where the tap occurred.
  /// [coordinates] The coordinates of the tap.
  /// [annotation] The existing annotation to be modified.
  /// Returns an [Annotation] if the annotation is updated, otherwise null.
  @override
  Annotation? tap2(PdfPage page, Offset coordinates, Annotation annotation) {
    _logger.info(
        'Modifying an existing cue at page ${page.pageNumber} at position $coordinates');

    // Provide an existing label and add a connected marker cue
    if (annotation is Cue) {
      // Inherit types and tags from the first cue
      CueMarker newMarker = CueMarker(page: page.pageNumber, pos: coordinates);
      annotation.marker = newMarker;
      return annotation;
    }
    return null;
  }
}
