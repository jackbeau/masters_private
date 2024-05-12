import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pdfrx/pdfrx.dart';
import '../../domain/bloc/script_canvas_bloc.dart';

class ScriptCanvas extends StatefulWidget {
  final PdfViewerController controller;

  const ScriptCanvas({required this.controller, Key? key}) : super(key: key);

  @override
  State<ScriptCanvas> createState() => _ScriptCanvasState();
}

class _ScriptCanvasState extends State<ScriptCanvas> {
  late final ScriptCanvasBloc _bloc;

  @override
  void initState() {
    super.initState();
    _bloc = ScriptCanvasBloc(widget.controller);
    widget.controller.addListener(_onControllerUpdate);
  }

  void _onControllerUpdate() {
    _bloc.add(ControllerUpdated());
  }

  @override
  Widget build(BuildContext context) {
    return BlocProvider.value(
      value: _bloc,
      child: BlocBuilder<ScriptCanvasBloc, ScriptCanvasState>(
        builder: (context, state) {
          return Row(
            children: [
              Expanded(
                child: Stack(
                  children: [
                    PdfViewer.asset(
                      'assets/input.pdf',
                      controller: widget.controller,
                      params: _buildPdfViewerParams(state),
                    ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }

PdfViewerParams _buildPdfViewerParams(ScriptCanvasState state) {
  return PdfViewerParams(
      margin: 0,
      backgroundColor: Colors.black,
      enableTextSelection: true,
      maxScale: 8,
      pagePaintCallbacks: [
        if (state is ScriptCanvasReady)
          (Canvas canvas, Rect pageRect, PdfPage page) =>
              _drawAnnotations(canvas, pageRect, page, state.annotations),
      ],
      pageOverlaysBuilder: ((context, pageRect, page) => [
        Positioned.fill(  // Ensure the listener covers the whole overlay
          child: Stack(
            children: [
              Listener(
                onPointerMove: (details) => _bloc.add(PagePanUpdate(details.delta, page, pageRect)),
                onPointerUp: (details) => _bloc.add(PagePanEnd()),
                behavior: HitTestBehavior.translucent,
              ),
              GestureDetector(
            onTapDown: (details) => 
              _bloc.add(PageTapDown(details.localPosition, page, pageRect)),
            onPanStart: ((details) =>
              _bloc.add(PagePanStart(details.localPosition, page, pageRect))),
                behavior: HitTestBehavior.translucent,
              ),
            ],
          ),
        ),
      ]),
      viewerOverlayBuilder: (context, size) => _buildViewerOverlays());
}




  List<Widget> _buildViewerOverlays() {
    return [
      PdfViewerScrollThumb(
        controller: widget.controller,
        orientation: ScrollbarOrientation.right,
        thumbSize: const Size(40, 25),
        thumbBuilder: (context, thumbSize, pageNumber, controller) => Container(
          color: Colors.black,
          child: Center(
            child: Text(pageNumber.toString(),
                style: const TextStyle(color: Colors.white)),
          ),
        ),
      ),
      PdfViewerScrollThumb(
        controller: widget.controller,
        orientation: ScrollbarOrientation.bottom,
        thumbSize: const Size(80, 30),
        thumbBuilder: (context, thumbSize, pageNumber, controller) => Container(
          color: Colors.red,
        ),
      ),
    ];
  }

  void _drawAnnotations(Canvas canvas, Rect pageRect, PdfPage page, annotations) {
    canvas.saveLayer(pageRect, Paint());
    canvas.drawColor(Colors.transparent, BlendMode.src);
    for (final annotation in annotations) {
      annotation.draw(canvas);
    }
    canvas.restore();
  }

  @override
  void dispose() {
    widget.controller.removeListener(_onControllerUpdate);
    _bloc.close();
    super.dispose();
  }
}
