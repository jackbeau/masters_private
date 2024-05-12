import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pdfrx/pdfrx.dart';

abstract class AppBarEvent {}
class ZoomIn extends AppBarEvent {}
class ZoomOut extends AppBarEvent {}
class GoToPage extends AppBarEvent {
  final int pageNumber;
  GoToPage(this.pageNumber);
}
class InitializeAppBar extends AppBarEvent {
  final PdfViewerController controller;
  InitializeAppBar(this.controller);
}
abstract class AppBarState {
  final PdfViewerController controller;
  AppBarState(this.controller);
}
class AppBarInitial extends AppBarState {
  AppBarInitial(PdfViewerController controller) : super(controller);
}

class AppBarBloc extends Bloc<AppBarEvent, AppBarState> {
  AppBarBloc(PdfViewerController controller) : super(AppBarInitial(controller)) {
    on<ZoomIn>((event, emit) {
      state.controller.zoomUp();
      emit(AppBarInitial(state.controller));
    });
    on<ZoomOut>((event, emit) {
      state.controller.zoomDown();
      emit(AppBarInitial(state.controller));
    });
    on<GoToPage>((event, emit) {
      state.controller.goToPage(pageNumber: event.pageNumber);
      emit(AppBarInitial(state.controller));
    });
    on<InitializeAppBar>((event, emit) {
      emit(AppBarInitial(event.controller));
    });
  }
}
