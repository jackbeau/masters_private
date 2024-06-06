// Author: Jack Beaumont
// Date: 06/06/2024
//
// This file contains extensions for PdfPageTextFragment and PdfPageText 
// to convert their properties to JSON format.

import 'package:pdfrx/pdfrx.dart';
import 'package:logging/logging.dart';

final Logger _logger = Logger('PdfExtensions');

extension PdfPageTextFragmentExtension on PdfPageTextFragment {
  /// Converts a [PdfPageTextFragment] to a JSON map.
  /// 
  /// Returns a map with the properties of the fragment.
  Map<String, dynamic> toJson() {
    _logger.fine('Converting PdfPageTextFragment to JSON');
    return {
      'bounds': {
        'bottom': bounds.bottom,
        'height': bounds.height,
        'left': bounds.left,
        'right': bounds.right,
        'top': bounds.top,
        'width': bounds.width,
      },
      'charRects': charRects?.map((rect) => {
            'bottom': rect.bottom,
            'height': rect.height,
            'left': rect.left,
            'right': rect.right,
            'top': rect.top,
            'width': rect.width,
          }).toList(),
      'end': end,
      'index': index,
      'length': length,
      'text': text,
    };
  }
}

extension PdfPageTextExtension on PdfPageText {
  /// Converts a [PdfPageText] to a JSON map.
  /// 
  /// Returns a map with the properties of the page text.
  Map<String, dynamic> toJson() {
    _logger.fine('Converting PdfPageText to JSON');
    return {
      'fullText': fullText,
      'pageNumber': pageNumber,
      'fragments': fragments.map((fragment) => fragment.toJson()).toList(),
    };
  }
}
