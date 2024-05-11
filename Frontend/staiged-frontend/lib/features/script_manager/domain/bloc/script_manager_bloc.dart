import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pdfrx/pdfrx.dart';

abstract class ScriptManagerEvent {}
class LoadPdf extends ScriptManagerEvent {}
class SegmentChanged extends ScriptManagerEvent {
  final int selectedSegment;
  SegmentChanged(this.selectedSegment);
}

abstract class ScriptManagerState {}
class ScriptManagerInitial extends ScriptManagerState {}
class ScriptManagerLoaded extends ScriptManagerState {
  final PdfViewerController pdfController;
  final int segmentedControlValue;

  ScriptManagerLoaded(this.pdfController, this.segmentedControlValue);
}
class ScriptManagerBloc extends Bloc<ScriptManagerEvent, ScriptManagerState> {
  ScriptManagerBloc() : super(ScriptManagerInitial()) {
    on<LoadPdf>((event, emit) {
      final controller = PdfViewerController();
      emit(ScriptManagerLoaded(controller, 0));
    });
    on<SegmentChanged>((event, emit) {
      if (state is ScriptManagerLoaded) {
        emit(ScriptManagerLoaded((state as ScriptManagerLoaded).pdfController, event.selectedSegment));
      }
    });
  }
}
