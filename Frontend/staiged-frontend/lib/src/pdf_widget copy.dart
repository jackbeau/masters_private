import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:pdfrx/pdfrx.dart';
import 'package:pdfx/pdfx.dart';

class HomePage extends StatefulWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int totalPageCount = 0, currentPage = 1;
  final controller = PdfViewerController();

  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Hi",
          style: TextStyle(
            color: Colors.white,
          ),
        ),
        backgroundColor: Colors.black,
      ),
      body: _buildUI(),
    );
  }

  Widget _buildUI() {
    return Column(
      children: [
        Row(
          mainAxisSize: MainAxisSize.max,
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Text("Total Pages: ${totalPageCount}"),
            IconButton(
              onPressed: () {
                controller.goToPage(pageNumber: 10);
                // pdfControllerPinch.previousPage(
                //   duration: Duration(milliseconds: 500),
                //   curve: Curves.linear,
                // );
              },
              icon: Icon(
                Icons.arrow_back,
              ),
            ),
            Text("Current Page: ${currentPage}"),
            IconButton(
              onPressed: () {
                // pdfControllerPinch.nextPage(
                //   duration: Duration(milliseconds: 500),
                //   curve: Curves.linear,
                // );
              },
              icon: Icon(
                Icons.arrow_forward,
              ),
            ),
          ],
        ),
        Expanded(
          child: _pdfContainer(),
        ),
      ],
    );
  }

  Widget _pdfContainer() {
    int totalPageCount = 10; // Example total page count
    int currentPage = 5; // Example current page

    return Row(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        SizedBox(
          width: 20, // Arbitrary width for progress indicator
          child: Container(
            color: Colors.blue, // Arbitrary color
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: List.generate(
                totalPageCount,
                (index) => Container(
                  width: double.infinity,
                  height: 2, // Arbitrary height
                  color: index + 1 == currentPage ? Colors.white : Colors.transparent, // Highlight current page
                ),
              ),
            ),
          ),
        ),
        Expanded(
          child: Container(
            color: Colors.grey.withOpacity(0.3), // Placeholder color for PDF viewer
            child: Center(
              child: PdfViewer.asset(
                "assets/input.pdf",
                controller: controller,
                params: const PdfViewerParams(
                  margin: 0,
                  backgroundColor: Colors.black,
                  enableTextSelection: true,
                ),
              )
            ),
          ),
        ),
      ],
    );
  }
}

void main() {
  runApp(MaterialApp(
    home: HomePage(),
  ));
}
