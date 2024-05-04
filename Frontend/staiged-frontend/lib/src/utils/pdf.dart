import 'package:flutter/material.dart';
import 'package:pdfrx/pdfrx.dart';
  
pdfRescaleCoordinates(Offset position, Rect pageRect, PdfPage page) {
  final pixelToPointX = page.width / pageRect.width;
  final pixelToPointY = page.height / pageRect.height;
  Offset clickPosition = Offset(
    position.dx * pixelToPointX,
    position.dy * pixelToPointY + (page.pageNumber-1)*page.height
  );
  return clickPosition;
}