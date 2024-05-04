import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:pdfx/pdfx.dart';

class PDFScreen extends StatefulWidget {
  const PDFScreen({super.key});

  @override
  State<PDFScreen> createState() => _PDFScreenState();
}

String url = 'assets/input.pdf';

class _PDFScreenState extends State<PDFScreen> {

  final _pdfController = PdfController(
    document: PdfDocument.openAsset(url),
  );

  Future loadPdf() async {
    try {
      await rootBundle.load(url);
    } catch (e) {
      debugPrint(e.toString());
    }
  }

  @override
  void initState() {
    super.initState();
    loadPdf();
  }

   @override
  void dispose() {
    _pdfController.dispose();
    super.dispose();
  }


  @override
  Widget build(BuildContext context) {
    Widget loaderWidget = const Center(
        child: CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
            ),
          );
    return Scaffold(
      body: SafeArea(
          child: Container(
            color: Colors.grey,
            height: MediaQuery.of(context).size.height,
            child: _pdfController == null
                ? loaderWidget
                : PdfView(
                  controller: _pdfController),
          )),
    );
  }
}