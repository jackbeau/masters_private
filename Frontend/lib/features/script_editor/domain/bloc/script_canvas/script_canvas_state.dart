part of 'script_canvas_bloc.dart';

abstract class ScriptCanvasState {}

class ScriptCanvasInitial extends ScriptCanvasState {}

class ScriptCanvasReady extends ScriptCanvasState {
  final List<Annotation> annotations;
  final double indicatorYAxis;

  ScriptCanvasReady(
      this.annotations, {
        this.indicatorYAxis = 0,
      });
}