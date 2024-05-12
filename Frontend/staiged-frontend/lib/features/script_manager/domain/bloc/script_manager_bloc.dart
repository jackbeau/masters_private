import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pdfrx/pdfrx.dart';

abstract class ScriptManagerEvent {}
class LoadPdf extends ScriptManagerEvent {}
class SegmentChanged extends ScriptManagerEvent {
  final int selectedSegment;
  SegmentChanged(this.selectedSegment);
}
class ModeChanged extends ScriptManagerEvent {
  final Mode mode;
  ModeChanged(this.mode);
}

enum Mode { edit, review, live }

abstract class ScriptManagerState {
  final PdfViewerController? pdfController;
  final int segmentedControlValue;
  final Mode mode;

  ScriptManagerState({this.pdfController, this.segmentedControlValue = 0, this.mode = Mode.review});
}
class ScriptManagerInitial extends ScriptManagerState {}
class ScriptManagerLoaded extends ScriptManagerState {
  ScriptManagerLoaded(PdfViewerController controller, int segmentedControlValue, Mode mode)
      : super(pdfController: controller, segmentedControlValue: segmentedControlValue, mode: mode);
}

class ScriptManagerBloc extends Bloc<ScriptManagerEvent, ScriptManagerState> {
  ScriptManagerBloc() : super(ScriptManagerInitial()) {
    on<LoadPdf>((event, emit) {
      final controller = PdfViewerController();
      emit(ScriptManagerLoaded(controller, 0, Mode.review)); // Set default mode, mark as loaded once pdf is loaded
    });
    on<SegmentChanged>((event, emit) {
      if (state is ScriptManagerLoaded) {
        // Keep the previous mode and update only the segment
        emit(ScriptManagerLoaded((state as ScriptManagerLoaded).pdfController!, event.selectedSegment, state.mode));
      }
    });
    on<ModeChanged>((event, emit) {
      if (state is ScriptManagerLoaded) {
        print(event.mode);
        // Update only the mode, keeping other state aspects unchanged
        emit(ScriptManagerLoaded((state as ScriptManagerLoaded).pdfController!, state.segmentedControlValue, event.mode));
      }
    });
  }
}
