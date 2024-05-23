part of 'script_canvas_bloc.dart';

final Map<Tool, dynamic> toolMap = {
  Tool.none: null,
  Tool.new_cue: NewCue(),
};

sealed class ScriptCanvasEvent {} // sealed ensured no subclasses can be defined outside of this file

final class ControllerUpdated extends ScriptCanvasEvent {
  ControllerUpdated();
}

final class PageTapDown extends ScriptCanvasEvent {
  final Offset position;
  final PdfPage page;
  final Rect pageRect;

  PageTapDown(this.position, this.page, this.pageRect);
}

final class PagePanStart extends ScriptCanvasEvent {
  final Offset position;
  final PdfPage page;
  final Rect pageRect;

  PagePanStart(this.position, this.page, this.pageRect);
}

class PagePanUpdate extends ScriptCanvasEvent {
  final Offset delta;
  final PdfPage page;
  final Rect pageRect;

  PagePanUpdate(this.delta, this.page, this.pageRect);
}

final class PagePanEnd extends ScriptCanvasEvent {}

class UpdateIndicator extends ScriptCanvasEvent {
  final double yAxis;

  UpdateIndicator(this.yAxis);
}