import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pdfrx/pdfrx.dart';
import 'package:staiged/features/script_manager/domain/cue.dart';
import 'package:staiged/features/script_manager/domain/cue_marker.dart';
import '../../data/models/annotation.dart';
import '../annotation_tool.dart';
import '../../domain/pdf_utils.dart';
import 'package:collection/collection.dart';
import 'script_manager_bloc.dart';
import 'dart:async';
import '../annotation_interaction_handler.dart';
import 'cue_editor_bloc.dart';

final Map<Tool, dynamic> toolMap = {
  Tool.none: null,
  Tool.new_cue: NewCue(),
};

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
  final ScriptManagerBloc scriptManagerBloc;
  final List<Annotation> _annotations = [];
  late StreamSubscription scriptManagerSubscription;
  Annotation? selectedAnnotation;
  Tool? selectedTool;
  int tap = 0;
  bool isDown = false;
  Offset lastCentrePosition = const Offset(0, 0);
  Mode? selectedMode;

  ScriptCanvasBloc(
    this.controller,
    this.scriptManagerBloc,
    ) : super(ScriptCanvasInitial()) {
    // Initial selected tool
    selectedTool = scriptManagerBloc.state.selectedTool;
    selectedMode = scriptManagerBloc.state.mode;
    
    // Listen to changes in ScriptManagerBloc
    scriptManagerSubscription = scriptManagerBloc.stream.listen((state) {
      if (state is ScriptManagerLoaded) {
        selectedTool = state.selectedTool;
        // If mode changed, need to clear tool parameters
        if (selectedMode != state.mode) {
          isDown = false;
          selectedAnnotation = null;
          selectedMode = state.mode;
          tap = 0;
        }
      }
    });

    // To capture scroll events
    on<ControllerUpdated>((event, emit) {
      if (selectedMode != Mode.edit) {
        return;
      } else if (selectedTool == null) {
        return;
      }
      if (isDown) {
        Offset displacement = controller.centerPosition - lastCentrePosition;
        AnnotationInteractionHandler().move(displacement, selectedAnnotation!);
        lastCentrePosition = controller.centerPosition;
        // Emit a state if necessary to update the UI or handle additional logic.
        emit(ScriptCanvasReady(
            List.from(_annotations))); // Assuming you have a state like this
      }
    });

    on<PageTapDown>((event, emit) {
      if (selectedMode != Mode.edit) {
        return;
      } else if (selectedTool == Tool.none) {
        return;
      }
      Offset cursorPosition =
          pdfRescaleCoordinates(event.position, event.pageRect, event.page);
      var newAnnotation =
          _annotations.firstWhereOrNull((a) => a.isInObject(a, cursorPosition));

      if (newAnnotation == null) {
        if (toolMap[selectedTool].twoActions == false) {
          toolMap[selectedTool].tap(event.page, cursorPosition, _annotations);
        } else {
          if (tap == 0) {
            selectedAnnotation =
                toolMap[selectedTool].tap(event.page, cursorPosition, _annotations);
            tap = 1;
          } else {
            toolMap[selectedTool].tap2(
                event.page, cursorPosition, _annotations, selectedAnnotation!);
            scriptManagerBloc.add(EditorChanged(EditorPanel.add_cue));
            if (selectedAnnotation != null) {
              scriptManagerBloc.add(UpdateSelectedAnnotationEvent(selectedAnnotation));
            }
            
            selectedAnnotation = null;
            tap = 0;
          }
        }
        emit(ScriptCanvasReady(List.from(_annotations)));
      } else { // there already is an annotation here, so return the object to the scriptManager
        switch (newAnnotation ) {
          case Cue _:
          return scriptManagerBloc.add(UpdateSelectedAnnotationEvent(newAnnotation));
          case CueMarker _:
          return scriptManagerBloc.add(UpdateSelectedAnnotationEvent(newAnnotation));
        }
      }
    });

    on<PagePanStart>((event, emit) {
      if (selectedMode != Mode.edit) {
        return;
      } else if (tap == 0) {
        Offset cursorPos =
            pdfRescaleCoordinates(event.position, event.pageRect, event.page);
        selectedAnnotation =
            _annotations.firstWhereOrNull((a) => a.isInObject(a, cursorPos));
        if (selectedAnnotation != null) {
          AnnotationInteractionHandler().down(event.page, cursorPos, selectedAnnotation!);
          lastCentrePosition = controller.centerPosition;
          isDown = true;
        }
        emit(ScriptCanvasReady(List.from(_annotations)));
      }
    });

    on<PagePanUpdate>((event, emit) {
      if (selectedMode != Mode.edit) {
        return;
      } else if (isDown && tap == 0) {
        // Calculate the displacement, converting the delta from pixels to the PDF's point coordinate system.
        final pixelToPointX = event.page.width / event.pageRect.width;
        final pixelToPointY = event.page.height / event.pageRect.height;
        Offset displacement = Offset(
          event.delta.dx * pixelToPointX,
          event.delta.dy * pixelToPointY,
        );

        // Check if an annotation is selected and move it accordingly.
        if (selectedAnnotation != null) {
          AnnotationInteractionHandler().move(displacement, selectedAnnotation!,
              page: event.page, controller: controller);
          // If needed, emit a state to update the UI or handle additional logic.
          emit(ScriptCanvasReady(List.from(
              _annotations))); // Assuming you have a state like this for updating the UI
        }
      }
    });

    on<PagePanEnd>((event, emit) {
      if (selectedMode != Mode.edit) {
        return;
      } else if (tap == 0) {
        isDown = false;
        selectedAnnotation = null;
      }
      emit(ScriptCanvasReady(List.from(_annotations)));
    });
  @override
  Future<void> close() {
    scriptManagerSubscription.cancel();  // cancel subscription
    return super.close();
  }
  }
}
