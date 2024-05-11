import 'dart:html';

import 'package:flutter/material.dart';
import 'package:pdfrx/pdfrx.dart';
import '../../../script_viewer_page/common/annotations/annotation.dart';
import '../../../script_viewer_page/common/tools/tools.dart';
import 'package:collection/collection.dart';
import '../../../script_viewer_page/script_canvas/utils.dart';

class ScriptCanvas extends StatefulWidget {
  final PdfViewerController controller;
  
  const ScriptCanvas({required this.controller, super.key});

  @override
  State<ScriptCanvas> createState() => _ViewerState();
}

class _ViewerState extends State<ScriptCanvas> {
  final documentRef = ValueNotifier<PdfDocumentRef?>(null);
  final showLeftPane = ValueNotifier<bool>(false);
  final outline = ValueNotifier<List<PdfOutlineNode>?>(null);
  late final textSearcher = PdfTextSearcher(widget.controller)..addListener(_update);
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
    widget.controller.addListener(onControllerUpdate);
  }

  void onControllerUpdate() {
    // widget.controller.setZoom(widget.controller.centerPosition, widget.controller.coverScale);
    if (isDown) {
      setState(() {
        selectedTool?.move(widget.controller.centerPosition-lastCentrePosition, selectedAnnotation!);
        lastCentrePosition = widget.controller.centerPosition;
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Row(
        children: [
          Expanded(
            child: Stack(
              children: [
                PdfViewer.asset(
                  'assets/input.pdf',
                  controller: widget.controller,
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
                        controller: widget.controller,
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
                        controller: widget.controller,
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
      );
  }

    void _tap(TapDownDetails details, Rect pageRect, PdfPage page) {
      Offset cursorPosition = pdfRescaleCoordinates(details.localPosition, pageRect, page);
      var newAnnotation = _annotations.firstWhereOrNull((a) => a.isInObject(a, cursorPosition));

      if (newAnnotation == null) {
        setState(() {
          if (selectedTool?.twoActions == false) {
            selectedTool?.tap(page, cursorPosition, _annotations);
          } else {
            if (tap == 0) {
              print(0);
              selectedAnnotation = selectedTool?.tap(page, cursorPosition, _annotations);
              tap = 1;
            } else {
              print(selectedAnnotation);
              selectedTool?.tap2(page, cursorPosition, _annotations, selectedAnnotation!);
              selectedAnnotation = null;
              tap = 0;
            }
          }
        });
      }
      print("this");
    }


  void _down(DragStartDetails details, Rect pageRect, PdfPage page) {
    if (tap == 0) {
      setState(() {
        isDown = true;
        Offset cursorPos = pdfRescaleCoordinates(details.localPosition, pageRect, page);

        selectedAnnotation = _annotations.firstWhereOrNull((a) => a.isInObject(a, cursorPos));
        if (selectedAnnotation != null) {
          selectedTool?.down(page, cursorPos, selectedAnnotation!);
          lastCentrePosition = widget.controller.centerPosition;
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
          selectedTool?.move(displacement, selectedAnnotation!, page: page, controller: widget.controller);
        }
      });
    }
  }

  void _drawCues(Canvas canvas, Rect pageRect, PdfPage page) {
    canvas.saveLayer(pageRect, Paint());
    canvas.drawColor(Colors.transparent, BlendMode.src);
    for (final annotation in _annotations) {
      annotation.draw(canvas);
    }
    canvas.restore();
  }
}