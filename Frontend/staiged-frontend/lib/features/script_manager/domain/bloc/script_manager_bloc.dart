import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pdfrx/pdfrx.dart';

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
class ToggleCameraView extends ScriptManagerEvent {}

enum Mode { edit, review, live }
enum InspectorPanel { show, cues, notes, comments }

abstract class ScriptManagerState {
  final PdfViewerController? pdfController;
  final InspectorPanel selectedInspector;
  final Mode mode;
   final bool isCameraVisible;

  ScriptManagerState({this.pdfController, this.selectedInspector = InspectorPanel.cues, this.mode = Mode.review, this.isCameraVisible = false});
}

class ScriptManagerInitial extends ScriptManagerState {}
class ScriptManagerLoaded extends ScriptManagerState {
  ScriptManagerLoaded(PdfViewerController controller, InspectorPanel selectedInspector, Mode mode, {bool isCameraVisible = false})
      : super(pdfController: controller, selectedInspector: selectedInspector, mode: mode, isCameraVisible: isCameraVisible);
}

class ScriptManagerBloc extends Bloc<ScriptManagerEvent, ScriptManagerState> {
  ScriptManagerBloc() : super(ScriptManagerInitial()) {
    on<LoadPdf>((event, emit) {
      final controller = PdfViewerController();
      emit(ScriptManagerLoaded(controller, InspectorPanel.cues, Mode.review)); // Set default mode, mark as loaded once pdf is loaded
    });
    on<InspectorChanged>((event, emit) {
      if (state is ScriptManagerLoaded) {
        // Keep the previous mode and update only the segment
        emit(ScriptManagerLoaded((state as ScriptManagerLoaded).pdfController!, event.selectedInspector, state.mode, isCameraVisible: state.isCameraVisible));
      }
    });
    on<ModeChanged>((event, emit) {
      if (state is ScriptManagerLoaded) {
        print(event.mode);
        // Update only the mode, keeping other state aspects unchanged
        emit(ScriptManagerLoaded((state as ScriptManagerLoaded).pdfController!, state.selectedInspector, event.mode, isCameraVisible: state.isCameraVisible));
      }
    });
    on<ToggleCameraView>((event, emit) {
    if (state is ScriptManagerLoaded) {
      var currentState = state as ScriptManagerLoaded;
      emit(ScriptManagerLoaded(currentState.pdfController!, currentState.selectedInspector, currentState.mode, isCameraVisible: !currentState.isCameraVisible));
    }
  });
  }
}
