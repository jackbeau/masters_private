import 'package:flutter/material.dart';
import 'package:pdfrx/pdfrx.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../domain/bloc/pdf_bloc.dart';
import '../../domain/models/pdf_model.dart';
import '../../domain/models/pdf_extensions.dart'; // Import the extensions

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
  }

  void _onDocumentLoaded() {
    _extractText();
    _controller.removeListener(_onDocumentLoaded); // Prevent multiple calls
  }

  Future<void> _extractText() async {
    final document = _controller.document;
      for (int pageIndex = 0; pageIndex < document.pages.length; pageIndex++) {
        final page = document.pages[pageIndex];
        final pageText = await page.loadText();
        setState(() {
          _pageTexts[pageIndex] = pageText;
        });
      }
      _sendExtractedText();
  }

  void _sendExtractedText() {
  final jsonTexts = {
    'pages': _pageTexts.entries.map((entry) {
      final index = entry.key;
      final text = entry.value;
      return {
        'page_number': index + 1, // assuming index starts from 0 and needs to be 1-based
        ...text.toJson(), // spreading the rest of the text's JSON properties
      };
    }).toList(),
  };
    final pdfBloc = BlocProvider.of<PDFBloc>(context);
    pdfBloc.add(ExtractAndSendText(widget.pdf.filename, jsonTexts));
  }

  @override
  Widget build(BuildContext context) {
    return BlocListener<PDFBloc, PDFState>(
      listener: (context, state) {
        if (state is TextExtractionError) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Text extraction failed: ${state.message}')),
          );
        } else if (state is TextExtractionSuccess) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Text extraction succeeded')),
          );
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
  }
}
