import 'dart:html';

import 'package:flutter/material.dart';
import 'package:pdfrx/pdfrx.dart';
import 'cues.dart';
import 'tools.dart';
import 'package:collection/collection.dart';
import 'utils/pdf.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage>{
  final documentRef = ValueNotifier<PdfDocumentRef?>(null);
  final controller = PdfViewerController();
  final showLeftPane = ValueNotifier<bool>(false);
  final outline = ValueNotifier<List<PdfOutlineNode>?>(null);
  late final textSearcher = PdfTextSearcher(controller)..addListener(_update);
  final List<Annotation> _annotations = [];
  bool isDown = false;
  Annotation ?selectedAnnotation;
  Offset lastCentrePosition = const Offset(0, 0);
  Tool ?selectedTool = NewCue();
  int tap = 0;

  void _update() {
    if (mounted) {
      setState(() {});
    }
  }

  @override
  void initState() {
    super.initState();
    controller.addListener(onControllerUpdate);
  }

  void onControllerUpdate() {
    // controller.setZoom(controller.centerPosition, controller.coverScale);
    if (isDown) {
      setState(() {
        selectedTool?.move(controller.centerPosition-lastCentrePosition, selectedAnnotation!);
        lastCentrePosition = controller.centerPosition;
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.menu),
          onPressed: () {
            showLeftPane.value = !showLeftPane.value;
          },
        ),
        title: const Text('Pdfrx example'),
        actions: [
          IconButton(
            icon: const Icon(Icons.zoom_in),
            onPressed: () => controller.zoomUp(),
          ),
          IconButton(
            icon: const Icon(Icons.zoom_out),
            onPressed: () => controller.zoomDown(),
          ),
          IconButton(
            icon: const Icon(Icons.first_page),
            onPressed: () => controller.goToPage(pageNumber: 1),
          ),
          IconButton(
            icon: const Icon(Icons.last_page),
            onPressed: () =>
                controller.goToPage(pageNumber: controller.pages.length),
          ),
        ],
      ),
      body: Row(
        children: [
          Expanded(
            child: Stack(
              children: [
                PdfViewer.asset(
                  'assets/input.pdf',
                  controller: controller,
                  params: PdfViewerParams(
                    margin: 0,
                    backgroundColor: Colors.black,
                    enableTextSelection: true,
                    maxScale: 8,
                    pagePaintCallbacks: [_drawCues],
                    pageOverlaysBuilder: ((context, pageRect, page) => [
                      SizedBox.expand(
                        child: GestureDetector(
                          onPanUpdate: (details) {
                            _move(details, pageRect, page);
                          },
                          onTapDown: (details) {
                            _tap(details, pageRect, page);
                          },
                          onPanStart: ((details) => _down(
                            details, pageRect, page
                          )),
                          onPanEnd: ((details) => _up()),
                        )
                      ),
                    ]),
                    viewerOverlayBuilder: (context, size) => [
                      // Show vertical scroll thumb on the right; it has page number on it
                      PdfViewerScrollThumb(
                        controller: controller,
                        orientation: ScrollbarOrientation.right,
                        thumbSize: const Size(40, 25),
                        thumbBuilder:
                            (context, thumbSize, pageNumber, controller) =>
                                Container(
                          color: Colors.black,
                          child: Center(
                            child: Text(
                              pageNumber.toString(),
                              style: const TextStyle(color: Colors.white),
                            ),
                          ),
                        ),
                      ),
                      // Just a simple horizontal scroll thumb on the bottom
                      PdfViewerScrollThumb(
                        controller: controller,
                        orientation: ScrollbarOrientation.bottom,
                        thumbSize: const Size(80, 30),
                        thumbBuilder:
                            (context, thumbSize, pageNumber, controller) =>
                                Container(
                          color: Colors.red,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }


  bool isInObject(Annotation annotation, Offset interactionPosition) {
    if (annotation is Cue) {
      Path tempPath = Path()
        ..addOval(Rect.fromCircle(
            center: annotation.pos, radius: annotation.radius));
      return tempPath.contains(interactionPosition);
    }

    return false;
  }

  void _tap(TapDownDetails details, Rect pageRect, PdfPage page) {
    Offset cursorPosition = pdfRescaleCoordinates(details.localPosition, pageRect, page);

    if (_annotations.firstWhereOrNull((a) => isInObject(a, cursorPosition)) == null) {
      if (selectedTool?.twoActions == false) {
        selectedTool?.tap(page, cursorPosition, _annotations);
      }
      else {
        if (tap == 0) {
          print(0);
          selectedAnnotation = selectedTool?.tap(page, cursorPosition, _annotations);
          tap = 1;
        }
        else {
          print(selectedAnnotation);
          selectedTool?.tap2(page, cursorPosition, _annotations, selectedAnnotation!);
          selectedAnnotation = null;
          tap = 0;
        }
      }
    }
    setState(() {});
  }

  void _down(DragStartDetails details, Rect pageRect, PdfPage page) {
    if (tap == 0) {
      setState(() {
        isDown = true;
        Offset cursorPos = pdfRescaleCoordinates(details.localPosition, pageRect, page);

        selectedAnnotation = _annotations.firstWhereOrNull((a) => isInObject(a, cursorPos));
        if (selectedAnnotation != null) {
          selectedTool?.down(page, cursorPos, selectedAnnotation!);
          lastCentrePosition = controller.centerPosition;
        }
      });
    }
  }

  void _up() {
    if (tap == 0) {
      setState(() {
        isDown = false;
        selectedAnnotation = null;
      });
    }
  }

  void _move(DragUpdateDetails details, Rect pageRect, PdfPage page) {
    if (isDown && (tap == 0)) {
      setState(() {
        final pixelToPointX = page.width / pageRect.width;
        final pixelToPointY = page.height / pageRect.height;
        Offset displacement = Offset(
          details.delta.dx * pixelToPointX,
          details.delta.dy * pixelToPointY,
        );
        if (selectedAnnotation != null) {
          selectedTool?.move(displacement, selectedAnnotation!, page: page, controller: controller);
        }
      });
    }
  }

  void _drawCues(Canvas canvas, Rect pageRect, PdfPage page) {
    for (final annotation in _annotations) {
      annotation.draw(canvas);
    }
  }
}