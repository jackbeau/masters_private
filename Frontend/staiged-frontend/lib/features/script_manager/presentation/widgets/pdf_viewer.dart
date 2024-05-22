import 'package:flutter/material.dart';
import 'package:pdfrx/pdfrx.dart';
import '../../domain/models/pdf_model.dart';

class PDFViewer extends StatefulWidget {
  final PDFModel pdf;

  const PDFViewer({required this.pdf, Key? key}) : super(key: key);

  @override
  _PDFViewerState createState() => _PDFViewerState();
}

class _PDFViewerState extends State<PDFViewer> {
  late PdfViewerController _controller;

  @override
  void initState() {
    super.initState();
    _controller = PdfViewerController();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
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
    );
  }

  @override
  void dispose() {
    super.dispose();
  }
}