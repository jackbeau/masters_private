/// Author: Jack Beaumont
/// Date: 06/06/2024
/// Description: This file contains the implementation of the PDFViewer widget,
/// which is responsible for displaying PDF files and extracting text from them.
library;

import 'package:flutter/material.dart';
import 'package:pdfrx/pdfrx.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:logging/logging.dart'; // Import logging package
import '../../domain/bloc/pdf_bloc.dart';
import '../../domain/entities/pdf_model.dart';
import '../../domain/entities/pdf_extensions.dart'; // Import the extensions

// Initialize logger
final _logger = Logger('PDFViewer');

/// A widget that displays a PDF file and extracts text from it.
class PDFViewer extends StatefulWidget {
  final PDFModel pdf;

  const PDFViewer({required this.pdf, super.key});

  @override
  PDFViewerState createState() => PDFViewerState();
}

class PDFViewerState extends State<PDFViewer> {
  late PdfViewerController _controller;
  final Map<int, PdfPageText> _pageTexts = {};

  @override
  void initState() {
    super.initState();
    _controller = PdfViewerController();
    _controller.addListener(_onDocumentLoaded);
    _logger.info('PDFViewer initialized');
  }

  /// Callback when the PDF document is loaded.
  void _onDocumentLoaded() {
    _extractText();
    _controller.removeListener(_onDocumentLoaded); // Prevent multiple calls
    _logger.info('Document loaded and listener removed');
  }

  /// Extracts text from each page of the PDF document.
  Future<void> _extractText() async {
    final document = _controller.document;
    for (int pageIndex = 0; pageIndex < document.pages.length; pageIndex++) {
      final page = document.pages[pageIndex];
      final pageText = await page.loadText();
      setState(() {
        _pageTexts[pageIndex] = pageText;
      });
      _logger.info('Extracted text from page $pageIndex');
    }
    _sendExtractedText();
  }

  /// Sends the extracted text to the PDFBloc for further processing.
  void _sendExtractedText() {
    final jsonTexts = {
      'pages': _pageTexts.entries.map((entry) {
        final index = entry.key;
        final text = entry.value;
        return {
          'page_number':
              index + 1, // assuming index starts from 0 and needs to be 1-based
          ...text.toJson(), // spreading the rest of the text's JSON properties
        };
      }).toList(),
    };
    final pdfBloc = BlocProvider.of<PDFBloc>(context);
    pdfBloc.add(ExtractAndSendText(widget.pdf.filename, jsonTexts));
    _logger.info('Extracted text sent to PDFBloc');
  }

  @override
  Widget build(BuildContext context) {
    return BlocListener<PDFBloc, PDFState>(
      listener: (context, state) {
        if (state is TextExtractionError) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Text extraction failed: ${state.message}')),
          );
          _logger.severe('Text extraction failed: ${state.message}');
        } else if (state is TextExtractionSuccess) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Text extraction succeeded')),
          );
          _logger.info('Text extraction succeeded');
        }
      },
      child: SizedBox(
        height: 500, // Set a fixed height for the PdfViewer
        child: PdfViewer.uri(
          Uri.parse(widget.pdf.filepath),
          controller: _controller,
          params: PdfViewerParams(
            enableTextSelection: true,
            pageOverlaysBuilder: (context, pageRect, page) {
              return [
                Align(
                  alignment: Alignment.bottomCenter,
                  child: Text(
                    page.pageNumber.toString(),
                    style: const TextStyle(color: Colors.red),
                  ),
                ),
              ];
            },
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _controller.removeListener(_onDocumentLoaded);
    super.dispose();
    _logger.info('PDFViewer disposed');
  }
}
