import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pdfrx/pdfrx.dart';
import 'package:staiged/features/script_editor/domain/models/annotation.dart';
import 'package:staiged/features/script_editor/domain/repository/annotation_tool.dart';
import '../models/cue.dart';

abstract class ScriptEditorEvent {}

class LoadPdf extends ScriptEditorEvent {}

class InspectorChanged extends ScriptEditorEvent {
  final InspectorPanel selectedInspector;
  InspectorChanged(this.selectedInspector);
}

class ModeChanged extends ScriptEditorEvent {
  final Mode mode;
  ModeChanged(this.mode);
}

class ToolChanged extends ScriptEditorEvent {
  final Tool selectedTool;
  ToolChanged(this.selectedTool);
}

class EditorChanged extends ScriptEditorEvent {
  final EditorPanel selectedEditor;
  EditorChanged(this.selectedEditor);
}

class ToggleCameraView extends ScriptEditorEvent {}

class UpdateSelectedAnnotationEvent extends ScriptEditorEvent {
  final Annotation? selectedAnnotation;
  UpdateSelectedAnnotationEvent(this.selectedAnnotation);
}

enum Tool { none, new_cue }
enum Mode { edit, review, live }
enum InspectorPanel { show, cues, notes, comments }
enum EditorPanel { none, add_cue }

abstract class ScriptEditorState {
  final PdfViewerController? pdfController;
  final InspectorPanel selectedInspector;
  final EditorPanel selectedEditor;
  final Mode mode;
  final Tool selectedTool;
  final bool isCameraVisible;
  final Annotation? selectedAnnotation;

  ScriptEditorState({
    this.pdfController,
    this.selectedInspector = InspectorPanel.cues,
    this.selectedEditor = EditorPanel.none,
    this.mode = Mode.review,
    this.isCameraVisible = false,
    this.selectedTool = Tool.none,
    this.selectedAnnotation,
  });

  ScriptEditorState copyWith({
    PdfViewerController? pdfController,
    InspectorPanel? selectedInspector,
    EditorPanel? selectedEditor,
    Mode? mode,
    Tool? selectedTool,
    bool? isCameraVisible,
    Annotation? selectedAnnotation,
  });
}

class ScriptEditorInitial extends ScriptEditorState {
  @override
  ScriptEditorState copyWith({
    PdfViewerController? pdfController,
    InspectorPanel? selectedInspector,
    EditorPanel? selectedEditor,
    Mode? mode,
    Tool? selectedTool,
    bool? isCameraVisible,
    Annotation? selectedAnnotation,
  }) {
    return ScriptEditorInitial();
  }
}

class ScriptEditorLoaded extends ScriptEditorState {
  ScriptEditorLoaded(PdfViewerController controller, InspectorPanel selectedInspector, EditorPanel selectedEditor, Mode mode, Tool selectedTool, {super.isCameraVisible, Annotation? selectedAnnotation})
      : super(pdfController: controller, selectedInspector: selectedInspector, selectedEditor: selectedEditor, mode: mode, selectedTool: selectedTool, selectedAnnotation: selectedAnnotation);

  @override
  ScriptEditorState copyWith({
    PdfViewerController? pdfController,
    InspectorPanel? selectedInspector,
    EditorPanel? selectedEditor,
    Mode? mode,
    Tool? selectedTool,
    bool? isCameraVisible,
    Annotation? selectedAnnotation,
  }) {
    return ScriptEditorLoaded(
      pdfController ?? this.pdfController!,
      selectedInspector ?? this.selectedInspector,
      selectedEditor ?? this.selectedEditor,
      mode ?? this.mode,
      selectedTool ?? this.selectedTool,
      isCameraVisible: isCameraVisible ?? this.isCameraVisible,
      selectedAnnotation: selectedAnnotation ?? this.selectedAnnotation,
    );
  }
}

class ScriptEditorBloc extends Bloc<ScriptEditorEvent, ScriptEditorState> {
  ScriptEditorBloc() : super(ScriptEditorInitial()) {
    on<LoadPdf>((event, emit) => emit(ScriptEditorLoaded(PdfViewerController(), InspectorPanel.cues, EditorPanel.none, Mode.review, Tool.none)));
    on<InspectorChanged>((event, emit) => emit(state.copyWith(selectedInspector: event.selectedInspector)));
    on<EditorChanged>((event, emit) => emit(state.copyWith(selectedEditor: event.selectedEditor)));
    on<ModeChanged>((event, emit) => emit(state.copyWith(mode: event.mode, selectedTool: Tool.none)));
    on<ToolChanged>((event, emit) => emit(state.copyWith(selectedTool: event.selectedTool)));
    on<ToggleCameraView>((event, emit) {
      emit(state.copyWith(isCameraVisible: !state.isCameraVisible));
    });
    on<UpdateSelectedAnnotationEvent>((event, emit) {
      emit(state.copyWith(selectedAnnotation: event.selectedAnnotation));
    });
  }
}