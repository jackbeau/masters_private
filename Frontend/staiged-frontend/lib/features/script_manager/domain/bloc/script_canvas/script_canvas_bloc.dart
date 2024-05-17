import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pdfrx/pdfrx.dart';
import 'package:staiged/features/script_manager/data/providers/annotations_provider.dart';
import 'package:staiged/features/script_manager/domain/models/cue.dart';
import 'package:staiged/features/script_manager/domain/repository/cue_marker.dart';
import '../../models/annotation.dart';
import '../../repository/annotation_tool.dart';
import '../../repository/pdf_utils.dart';
import '../../../data/repositories/annotations_repository.dart';
import 'package:collection/collection.dart';
import '../script_manager_bloc.dart';
import 'dart:async';
import '../../repository/annotation_interaction_handler.dart';
import '../cue_editor_bloc.dart';

part 'script_canvas_event.dart';
part 'script_canvas_state.dart';

class ScriptCanvasBloc extends Bloc<ScriptCanvasEvent, ScriptCanvasState> {
  final PdfViewerController controller;
  final ScriptManagerBloc scriptManagerBloc;
  List<Annotation> _annotations = [];
  final AnnotationsRepository _annotationsRepository;

  late StreamSubscription scriptManagerSubscription;
  late StreamSubscription annotationsSubscription;

  Annotation? selectedAnnotation;
  Tool? selectedTool;
  int tap = 0;
  bool isDown = false;
  Offset lastCentrePosition = const Offset(0, 0);
  Mode? selectedMode;

  Future<void> _fetchAnnotations() async {
    await _annotationsRepository.getAnnotations();
    emit(ScriptCanvasReady(List.from(_annotations)));
  }

  ScriptCanvasBloc(
    this.controller,
    this.scriptManagerBloc,
    this._annotationsRepository,
  ) : super(ScriptCanvasInitial()) {
    selectedTool = scriptManagerBloc.state.selectedTool;
    selectedMode = scriptManagerBloc.state.mode;

    _fetchAnnotations();

    annotationsSubscription = _annotationsRepository.annotationsStream.listen((annotations) {
      _annotations = annotations;
      emit(ScriptCanvasReady(List.from(_annotations), indicatorYAxis: state is ScriptCanvasReady ? (state as ScriptCanvasReady).indicatorYAxis : 0.0));
    });

    scriptManagerSubscription = scriptManagerBloc.stream.listen((state) {
      if (state is ScriptManagerLoaded) {
        selectedTool = state.selectedTool;
        if (selectedMode != state.mode) {
          isDown = false;
          selectedAnnotation = null;
          selectedMode = state.mode;
          tap = 0;
        }
      }
    });

    on<ControllerUpdated>((event, emit) {
      _updateIndicatorPosition(emit);
      
      if (selectedMode != Mode.edit) return;
      if (selectedTool == null) return;

      if (isDown) {
        Offset displacement = controller.centerPosition - lastCentrePosition;
        var updatedAnnotation = AnnotationInteractionHandler().move(displacement, selectedAnnotation!);
        if (updatedAnnotation != null) {
          _annotationsRepository.updateAnnotation(updatedAnnotation);
        }
        lastCentrePosition = controller.centerPosition;
        emit(ScriptCanvasReady(List.from(_annotations), indicatorYAxis: state is ScriptCanvasReady ? (state as ScriptCanvasReady).indicatorYAxis : 0.0));
      }
    });

    on<PageTapDown>((event, emit) {
      if (selectedMode != Mode.edit) return;
      if (selectedTool == Tool.none) return;

      Offset cursorPosition = pdfRescaleCoordinates(event.position, event.pageRect, event.page);
      var newAnnotation = _annotations.firstWhereOrNull((a) => a.isInObject(a, cursorPosition));

      if (newAnnotation == null) {
        if (toolMap[selectedTool].twoActions == false) {
          var newAnnotation = toolMap[selectedTool].tap(event.page, cursorPosition);
          if (newAnnotation != null) {
            _annotationsRepository.addAnnotation(newAnnotation);
          }
        } else {
          if (tap == 0) {
            selectedAnnotation = toolMap[selectedTool].tap(event.page, cursorPosition);
            tap = 1;
            if (selectedAnnotation != null) {
              _annotationsRepository.addAnnotation(selectedAnnotation!);
            }
          } else {
            var newAnnotation = toolMap[selectedTool].tap2(event.page, cursorPosition, selectedAnnotation!);
            if (newAnnotation != null) {
              _annotationsRepository.addAnnotation(newAnnotation);
              scriptManagerBloc.add(EditorChanged(EditorPanel.add_cue));
              scriptManagerBloc.add(UpdateSelectedAnnotationEvent(selectedAnnotation));
            }
            selectedAnnotation = null;
            tap = 0;
          }
        }
        emit(ScriptCanvasReady(List.from(_annotations), indicatorYAxis: state is ScriptCanvasReady ? (state as ScriptCanvasReady).indicatorYAxis : 0.0));
      } else {
        switch (newAnnotation) {
          case CueMarker _:
            scriptManagerBloc.add(EditorChanged(EditorPanel.add_cue));
            return scriptManagerBloc.add(UpdateSelectedAnnotationEvent(newAnnotation.label));
          case Cue _:
            scriptManagerBloc.add(EditorChanged(EditorPanel.add_cue));
            return scriptManagerBloc.add(UpdateSelectedAnnotationEvent(newAnnotation));
        }
      }
    });

    on<PagePanStart>((event, emit) {
      if (selectedMode != Mode.edit) return;
      if (tap != 0) return;

      Offset cursorPos = pdfRescaleCoordinates(event.position, event.pageRect, event.page);
      selectedAnnotation = _annotations.firstWhereOrNull((a) => a.isInObject(a, cursorPos));
      if (selectedAnnotation != null) {
        AnnotationInteractionHandler().down(event.page, cursorPos, selectedAnnotation!);
        lastCentrePosition = controller.centerPosition;
        isDown = true;
      }
      emit(ScriptCanvasReady(List.from(_annotations), indicatorYAxis: state is ScriptCanvasReady ? (state as ScriptCanvasReady).indicatorYAxis : 0.0));
    });

    on<PagePanUpdate>((event, emit) {
      if (selectedMode != Mode.edit) return;
      if (!isDown || tap != 0) return;

      final pixelToPointX = event.page.width / event.pageRect.width;
      final pixelToPointY = event.page.height / event.pageRect.height;
      Offset displacement = Offset(
        event.delta.dx * pixelToPointX,
        event.delta.dy * pixelToPointY,
      );

      if (selectedAnnotation != null) {
        var updatedAnnotation = AnnotationInteractionHandler().move(displacement, selectedAnnotation!, page: event.page, controller: controller);
        if (updatedAnnotation != null) {
          _annotationsRepository.updateAnnotation(updatedAnnotation);
        }
      }
      emit(ScriptCanvasReady(List.from(_annotations), indicatorYAxis: state is ScriptCanvasReady ? (state as ScriptCanvasReady).indicatorYAxis : 0.0));
    });

    on<PagePanEnd>((event, emit) {
      if (selectedMode != Mode.edit) return;
      if (tap != 0) return;

      isDown = false;
      selectedAnnotation = null;
      emit(ScriptCanvasReady(List.from(_annotations), indicatorYAxis: state is ScriptCanvasReady ? (state as ScriptCanvasReady).indicatorYAxis : 0.0));
    });

    on<UpdateIndicator>((event, emit) {
      emit(ScriptCanvasReady(List.from(_annotations), indicatorYAxis: event.yAxis));
    });
  }

  void _updateIndicatorPosition(Emitter<ScriptCanvasState> emit) {
    const pointerPage = 1;
    double pointerY = 200;

    final viewRect = controller.visibleRect;
    final allRect = controller.documentSize;

    if (allRect.height <= viewRect.height) return;

    double distanceToPointer = pointerY;
    for (var i = 1; i < pointerPage; i++) {
      distanceToPointer += controller.pages[i].height;
    }

    final yPosition = (distanceToPointer + controller.value.y) / viewRect.height;

    final vh = viewRect.height * controller.currentZoom;
    final distance = yPosition * vh;

    emit(ScriptCanvasReady(
      List.from(_annotations),
      indicatorYAxis: distance,
    ));
  }

  @override
  Future<void> close() {
    scriptManagerSubscription.cancel();
    annotationsSubscription.cancel();
    return super.close();
  }
}
