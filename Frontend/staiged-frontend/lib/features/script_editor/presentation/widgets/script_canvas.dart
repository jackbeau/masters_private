import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pdfrx/pdfrx.dart';
import 'package:staiged/features/script_editor/data/providers/annotations_provider.dart';
import 'package:staiged/features/script_editor/data/repositories/annotations_repository.dart';
import 'package:staiged/features/script_editor/domain/bloc/cue_editor_bloc.dart';
import '../../domain/bloc/script_canvas/script_canvas_bloc.dart';
import '../../domain/bloc/script_editor_bloc.dart';
import '../../data/repositories/mqtt_repository.dart';

class ScriptCanvas extends StatefulWidget {
  final PdfViewerController controller;

  const ScriptCanvas({required this.controller, Key? key}) : super(key: key);

  @override
  State<ScriptCanvas> createState() => _ScriptCanvasState();
}

class _ScriptCanvasState extends State<ScriptCanvas> {
  late final ScriptCanvasBloc _bloc;
  late Tool selectedTool;
  final Map<int, PdfPageText> _pageTexts = {};

  @override
  void initState() {
    super.initState();
    _bloc = ScriptCanvasBloc(
      widget.controller,
      BlocProvider.of<ScriptEditorBloc>(context),
      RepositoryProvider.of<AnnotationsRepository>(context),
      RepositoryProvider.of<MqttRepository>(context),
    );
    widget.controller.addListener(_onControllerUpdate);
    widget.controller.addListener(_extractText);

    // Retrieve the selected tool from ScriptEditorBloc state
    selectedTool = context.read<ScriptEditorBloc>().state.selectedTool;
  }

  void _onControllerUpdate() {
    _bloc.add(ControllerUpdated());
  }

  Future<void> _extractText() async {
    final document = widget.controller.document;
    if (document != null) {
      for (int pageIndex = 0; pageIndex < document.pages.length; pageIndex++) {
        final page = await document.pages[pageIndex];
        final pageText = await page.loadText();
        setState(() {
          _pageTexts[pageIndex] = pageText;
        });
      }
    }
  }

  // void _updateIndicator(int pageNumber, double yAxis) {
  //   _bloc.add(UpdateIndicator(pageNumber, yAxis));
  // }

  @override
  Widget build(BuildContext context) {
    return BlocProvider.value(
      value: _bloc,
      child: BlocBuilder<ScriptCanvasBloc, ScriptCanvasState>(
        builder: (context, state) {
          return BlocBuilder<ScriptEditorBloc, ScriptEditorState>(
            buildWhen: (previous, current) =>
                previous.selectedTool != current.selectedTool,
            builder: (context, managerState) {
              selectedTool = managerState.selectedTool; // Update selected tool whenever ScriptEditorState changes
              return Row(
                children: [
                  VerticalProgressIndicator(
                    yAxis: state is ScriptCanvasReady
                        ? state.indicatorYAxis
                        : 0.0,
                    colorAbove: Colors.red,
                    colorBelow: Colors.red.shade900,
                  ),
                  Expanded(
                    child: Stack(
                      children: [
                        PdfViewer.uri(
                          Uri.parse("http://localhost:4000/download/output_with_margin.pdf"),
                          controller: widget.controller,
                          params: _buildPdfViewerParams(state),
                        ),
                      ],
                    ),
                  ),
                ],
              );
            },
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
         _highlightSentences, // needs to be above to ensure this is painted on the right layer
        if (state is ScriptCanvasReady)
          (Canvas canvas, Rect pageRect, PdfPage page) =>
              _drawAnnotations(canvas, pageRect, page, state.annotations),
       
      ],
      pageOverlaysBuilder: (context, pageRect, page) => [
        Positioned.fill(
          child: Stack(
            children: [
              Listener(
                onPointerMove: (details) =>
                    _bloc.add(PagePanUpdate(details.delta, page, pageRect)),
                onPointerUp: (details) => _bloc.add(PagePanEnd()),
                behavior: HitTestBehavior.translucent,
              ),
              GestureDetector(
                onTapDown: (details) =>
                    _bloc.add(PageTapDown(details.localPosition, page, pageRect)),
                onPanStart: (details) =>
                    _bloc.add(PagePanStart(details.localPosition, page, pageRect)),
                behavior: HitTestBehavior.translucent,
              ),
            ],
          ),
        ),
      ],
      viewerOverlayBuilder: (context, size) => _buildViewerOverlays(),
    );
  }

  List<Widget> _buildViewerOverlays() {
    return [
      PdfViewerScrollThumb(
        controller: widget.controller,
        orientation: ScrollbarOrientation.right,
        thumbSize: const Size(40, 25),
        thumbBuilder: (context, thumbSize, pageNumber, controller) =>
            Container(
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
        thumbBuilder: (context, thumbSize, pageNumber, controller) =>
            Container(
          color: Colors.red,
        ),
      ),
    ];
  }

  void _highlightSentences(Canvas canvas, Rect pageRect, PdfPage page) {
    final pageIndex = page.pageNumber - 1;
    if (_pageTexts.containsKey(pageIndex)) {
      final pageText = _pageTexts[pageIndex]!;

      final paint = Paint()
        ..color = Colors.yellow.withAlpha(100)
        ..style = PaintingStyle.fill;
      for (final f in pageText.fragments) {
          canvas.drawRect(
            f.bounds.toRectInPageRect(page: page, pageRect: pageRect),
            paint,
          );
      }
    }
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
    widget.controller.removeListener(_extractText);
    _bloc.close();
    super.dispose();
  }
}

class VerticalProgressIndicator extends StatelessWidget {
  final double yAxis;
  final Color colorAbove;
  final Color colorBelow;

  const VerticalProgressIndicator({
    Key? key,
    required this.yAxis,
    required this.colorAbove,
    required this.colorBelow,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      size: Size(20, double.infinity),
      painter: _VerticalProgressIndicatorPainter(
        yAxis: yAxis,
        colorAbove: colorAbove,
        colorBelow: colorBelow,
      ),
    );
  }
}

class _VerticalProgressIndicatorPainter extends CustomPainter {
  final double yAxis;
  final Color colorAbove;
  final Color colorBelow;

  _VerticalProgressIndicatorPainter({
    required this.yAxis,
    required this.colorAbove,
    required this.colorBelow,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final double offsetY = yAxis;
    final Paint paintAbove = Paint()..color = colorAbove;
    final Paint paintBelow = Paint()..color = colorBelow;

    // Draw above line
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, offsetY), paintAbove);

    // Draw below line
    canvas.drawRect(Rect.fromLTWH(0, offsetY, size.width, size.height - offsetY), paintBelow);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return true;
  }
}
