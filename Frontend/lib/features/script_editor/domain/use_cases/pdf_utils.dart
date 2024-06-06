// Author: Jack Beaumont
// Date: 06/06/2024

import 'package:flutter/material.dart';
import 'package:pdfrx/pdfrx.dart';
import 'package:logging/logging.dart';

// Set up logging
final Logger logger = Logger('PDFRescaleCoordinates');

/// Rescales the coordinates from pixel to point dimensions and returns the new offset position.
///
/// This function converts a given position in pixel dimensions to point dimensions based on the
/// dimensions of the PDF page and the display rectangle.
///
/// Parameters:
/// - [position]: The original position in pixel dimensions (Offset).
/// - [pageRect]: The rectangle representing the display area of the PDF page (Rect).
/// - [page]: The PDF page object (PdfPage).
///
/// Returns:
/// - The rescaled position in point dimensions as an Offset.
Offset pdfRescaleCoordinates(Offset position, Rect pageRect, PdfPage page) {
  logger.info('Rescaling coordinates from pixel to point dimensions.');

  // Calculate conversion factors
  final double pixelToPointX = page.width / pageRect.width;
  final double pixelToPointY = page.height / pageRect.height;

  // Convert position
  Offset clickPosition = Offset(position.dx * pixelToPointX,
      position.dy * pixelToPointY + (page.pageNumber - 1) * page.height);

  logger
      .info('Original position: $position, Rescaled position: $clickPosition');
  return clickPosition;
}
