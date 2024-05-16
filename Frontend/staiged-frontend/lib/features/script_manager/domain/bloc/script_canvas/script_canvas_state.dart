part of 'script_canvas_bloc.dart';

abstract class ScriptCanvasState {}

class ScriptCanvasInitial extends ScriptCanvasState {}

class ScriptCanvasReady extends ScriptCanvasState {
  final List<Annotation> annotations;
  ScriptCanvasReady(this.annotations);
}