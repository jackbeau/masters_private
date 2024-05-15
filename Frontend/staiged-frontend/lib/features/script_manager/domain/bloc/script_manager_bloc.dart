import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pdfrx/pdfrx.dart';
import 'package:staiged/features/script_manager/data/models/annotation.dart';
import 'package:staiged/features/script_manager/domain/annotation_tool.dart';
import '../cue.dart';

abstract class ScriptManagerEvent {}

class LoadPdf extends ScriptManagerEvent {}

class InspectorChanged extends ScriptManagerEvent {
  final InspectorPanel selectedInspector;
  InspectorChanged(this.selectedInspector);
}

class ModeChanged extends ScriptManagerEvent {
  final Mode mode;
  ModeChanged(this.mode);
}

class ToolChanged extends ScriptManagerEvent {
  final Tool selectedTool;
  ToolChanged(this.selectedTool);
}

class EditorChanged extends ScriptManagerEvent {
  final EditorPanel selectedEditor;
  EditorChanged(this.selectedEditor);
}

class ToggleCameraView extends ScriptManagerEvent {}

class UpdateSelectedAnnotationEvent extends ScriptManagerEvent {
  final Annotation? selectedAnnotation;
  UpdateSelectedAnnotationEvent(this.selectedAnnotation);
}

enum Tool { none, new_cue }
enum Mode { edit, review, live }
enum InspectorPanel { show, cues, notes, comments }
enum EditorPanel { none, add_cue }

abstract class ScriptManagerState {
  final PdfViewerController? pdfController;
  final InspectorPanel selectedInspector;
  final EditorPanel selectedEditor;
  final Mode mode;
  final Tool selectedTool;
  final bool isCameraVisible;
  final Annotation? selectedAnnotation;

  ScriptManagerState({
    this.pdfController,
    this.selectedInspector = InspectorPanel.cues,
    this.selectedEditor = EditorPanel.none,
    this.mode = Mode.review,
    this.isCameraVisible = false,
    this.selectedTool = Tool.none,
    this.selectedAnnotation,
  });

  ScriptManagerState copyWith({
    PdfViewerController? pdfController,
    InspectorPanel? selectedInspector,
    EditorPanel? selectedEditor,
    Mode? mode,
    Tool? selectedTool,
    bool? isCameraVisible,
    Annotation? selectedAnnotation,
  });
}

class ScriptManagerInitial extends ScriptManagerState {
  @override
  ScriptManagerState copyWith({
    PdfViewerController? pdfController,
    InspectorPanel? selectedInspector,
    EditorPanel? selectedEditor,
    Mode? mode,
    Tool? selectedTool,
    bool? isCameraVisible,
    Annotation? selectedAnnotation,
  }) {
    return ScriptManagerInitial();
  }
}

class ScriptManagerLoaded extends ScriptManagerState {
  ScriptManagerLoaded(PdfViewerController controller, InspectorPanel selectedInspector, EditorPanel selectedEditor, Mode mode, Tool selectedTool, {super.isCameraVisible, Annotation? selectedAnnotation})
      : super(pdfController: controller, selectedInspector: selectedInspector, selectedEditor: selectedEditor, mode: mode, selectedTool: selectedTool, selectedAnnotation: selectedAnnotation);

  @override
  ScriptManagerState copyWith({
    PdfViewerController? pdfController,
    InspectorPanel? selectedInspector,
    EditorPanel? selectedEditor,
    Mode? mode,
    Tool? selectedTool,
    bool? isCameraVisible,
    Annotation? selectedAnnotation,
  }) {
    return ScriptManagerLoaded(
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

class ScriptManagerBloc extends Bloc<ScriptManagerEvent, ScriptManagerState> {
  ScriptManagerBloc() : super(ScriptManagerInitial()) {
    on<LoadPdf>((event, emit) => emit(ScriptManagerLoaded(PdfViewerController(), InspectorPanel.cues, EditorPanel.none, Mode.review, Tool.none)));
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