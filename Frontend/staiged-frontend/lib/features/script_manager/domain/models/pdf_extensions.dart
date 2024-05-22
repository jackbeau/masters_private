import 'package:pdfrx/pdfrx.dart';

extension PdfPageTextFragmentExtension on PdfPageTextFragment {
  Map<String, dynamic> toJson() {
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
  Map<String, dynamic> toJson() {
    return {
      'fullText': fullText,
      'pageNumber': pageNumber,
      'fragments': fragments.map((fragment) => fragment.toJson()).toList(),
    };
  }
}
