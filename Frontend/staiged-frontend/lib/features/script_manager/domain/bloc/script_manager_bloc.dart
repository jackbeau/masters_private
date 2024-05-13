import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pdfrx/pdfrx.dart';
import 'package:staiged/features/script_manager/domain/annotation_tool.dart';

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
class ToggleCameraView extends ScriptManagerEvent {}

enum Tool { none, new_cue }
enum Mode { edit, review, live }
enum InspectorPanel { show, cues, notes, comments }

abstract class ScriptManagerState {
  final PdfViewerController? pdfController;
  final InspectorPanel selectedInspector;
  final Mode mode;
  final Tool selectedTool;
  final bool isCameraVisible;

  ScriptManagerState({
    this.pdfController, 
    this.selectedInspector = InspectorPanel.cues, 
    this.mode = Mode.review, 
    this.isCameraVisible = false, 
    this.selectedTool = Tool.none
  });

  ScriptManagerState copyWith({
    PdfViewerController? pdfController,
    InspectorPanel? selectedInspector,
    Mode? mode,
    Tool? selectedTool,
    bool? isCameraVisible,
  });
}

class ScriptManagerInitial extends ScriptManagerState {
  @override
  ScriptManagerState copyWith({
    PdfViewerController? pdfController,
    InspectorPanel? selectedInspector,
    Mode? mode,
    Tool? selectedTool,
    bool? isCameraVisible,
  }) {
    return ScriptManagerInitial();
  }
}

class ScriptManagerLoaded extends ScriptManagerState {
  ScriptManagerLoaded(PdfViewerController controller, InspectorPanel selectedInspector, Mode mode, Tool selectedTool, {bool isCameraVisible = false})
      : super(pdfController: controller, selectedInspector: selectedInspector, mode: mode, selectedTool: selectedTool, isCameraVisible: isCameraVisible);

  @override
  ScriptManagerState copyWith({
    PdfViewerController? pdfController,
    InspectorPanel? selectedInspector,
    Mode? mode,
    Tool? selectedTool,
    bool? isCameraVisible,
  }) {
    return ScriptManagerLoaded(
      pdfController ?? this.pdfController!,
      selectedInspector ?? this.selectedInspector,
      mode ?? this.mode,
      selectedTool ?? this.selectedTool,
      isCameraVisible: isCameraVisible ?? this.isCameraVisible,
    );
  }
}

class ScriptManagerBloc extends Bloc<ScriptManagerEvent, ScriptManagerState> {
  ScriptManagerBloc() : super(ScriptManagerInitial()) {
    on<LoadPdf>((event, emit) => emit(ScriptManagerLoaded(PdfViewerController(), InspectorPanel.cues, Mode.review, Tool.none)));
    on<InspectorChanged>((event, emit) => emit(state.copyWith(selectedInspector: event.selectedInspector)));
    on<ModeChanged>((event, emit) => emit(state.copyWith(mode: event.mode, selectedTool: Tool.none)));
    on<ToolChanged>((event, emit) => emit(state.copyWith(selectedTool: event.selectedTool)));
    on<ToggleCameraView>((event, emit) => emit(state.copyWith(isCameraVisible: !state.isCameraVisible)));
  }
}
