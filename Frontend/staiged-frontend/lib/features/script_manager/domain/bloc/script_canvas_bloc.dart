import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pdfrx/pdfrx.dart';
import '../../data/models/annotation.dart';
import '../tools.dart';
import '../../domain/pdf_utils.dart';
import 'package:collection/collection.dart';

abstract class ScriptCanvasEvent {}

class ControllerUpdated extends ScriptCanvasEvent {
  ControllerUpdated();
}

class PageTapDown extends ScriptCanvasEvent {
  final Offset position;
  final PdfPage page;
  final Rect pageRect;

  PageTapDown(this.position, this.page, this.pageRect);
}

class PagePanStart extends ScriptCanvasEvent {
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

class PagePanEnd extends ScriptCanvasEvent {}

abstract class ScriptCanvasState {}

class ScriptCanvasInitial extends ScriptCanvasState {}

class ScriptCanvasReady extends ScriptCanvasState {
  final List<Annotation> annotations;
  ScriptCanvasReady(this.annotations);
}

class AnnotationSelectedState extends ScriptCanvasState {
  final Annotation selectedAnnotation;
  final bool isDown;

  AnnotationSelectedState(this.selectedAnnotation, this.isDown);
}

class ScriptCanvasBloc extends Bloc<ScriptCanvasEvent, ScriptCanvasState> {
  final PdfViewerController controller;
  final List<Annotation> _annotations = [];
  Tool? selectedTool = NewCue();
  Annotation? selectedAnnotation;
  int tap = 0;
  bool isDown = false;
  Offset lastCentrePosition = const Offset(0, 0);

  ScriptCanvasBloc(this.controller) : super(ScriptCanvasInitial()) {
    // To capture scroll events
    on<ControllerUpdated>((event, emit) {
      if (isDown) {
        Offset displacement = controller.centerPosition - lastCentrePosition;
        selectedTool?.move(displacement, selectedAnnotation!);
        lastCentrePosition = controller.centerPosition;
        // Emit a state if necessary to update the UI or handle additional logic.
        emit(ScriptCanvasReady(
            List.from(_annotations))); // Assuming you have a state like this
      }
    });

    on<PageTapDown>((event, emit) {
      Offset cursorPosition =
          pdfRescaleCoordinates(event.position, event.pageRect, event.page);
      var newAnnotation =
          _annotations.firstWhereOrNull((a) => a.isInObject(a, cursorPosition));

      if (newAnnotation == null) {
        if (selectedTool?.twoActions == false) {
          selectedTool?.tap(event.page, cursorPosition, _annotations);
        } else {
          if (tap == 0) {
            selectedAnnotation =
                selectedTool?.tap(event.page, cursorPosition, _annotations);
            tap = 1;
          } else {
            selectedTool?.tap2(
                event.page, cursorPosition, _annotations, selectedAnnotation!);
            selectedAnnotation = null;
            tap = 0;
          }
        }
        emit(ScriptCanvasReady(List.from(_annotations)));
      }
    });

    on<PagePanStart>((event, emit) {
      if (tap == 0) {
        Offset cursorPos =
            pdfRescaleCoordinates(event.position, event.pageRect, event.page);
        selectedAnnotation =
            _annotations.firstWhereOrNull((a) => a.isInObject(a, cursorPos));
        if (selectedAnnotation != null) {
          selectedTool?.down(event.page, cursorPos, selectedAnnotation!);
          lastCentrePosition = controller.centerPosition;
          isDown = true;
        }
        emit(ScriptCanvasReady(List.from(_annotations)));
      }
    });

    on<PagePanUpdate>((event, emit) {
      if (isDown && tap == 0) {
        // Calculate the displacement, converting the delta from pixels to the PDF's point coordinate system.
        final pixelToPointX = event.page.width / event.pageRect.width;
        final pixelToPointY = event.page.height / event.pageRect.height;
        Offset displacement = Offset(
          event.delta.dx * pixelToPointX,
          event.delta.dy * pixelToPointY,
        );

        // Check if an annotation is selected and move it accordingly.
        if (selectedAnnotation != null) {
          selectedTool?.move(displacement, selectedAnnotation!,
              page: event.page, controller: controller);
          // If needed, emit a state to update the UI or handle additional logic.
          emit(ScriptCanvasReady(List.from(
              _annotations))); // Assuming you have a state like this for updating the UI
        }
      }
    });

    on<PagePanEnd>((event, emit) {
      if (tap == 0) {
        isDown = false;
        selectedAnnotation = null;
      }
      emit(ScriptCanvasReady(List.from(_annotations)));
    });
  }
}
