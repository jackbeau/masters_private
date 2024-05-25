import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pdfrx/pdfrx.dart';
import 'package:staiged/features/script_editor/domain/models/cue.dart';
import '../../models/annotation.dart';
import '../../repository/annotation_tool.dart';
import '../../repository/pdf_utils.dart';
import '../../../data/repositories/annotations_repository.dart';
import 'package:collection/collection.dart';
import '../script_editor_bloc.dart';
import 'dart:async';
import '../../repository/annotation_interaction_handler.dart';
import '../../../data/repositories/mqtt_repository.dart';

part 'script_canvas_event.dart';
part 'script_canvas_state.dart';

class ScriptCanvasBloc extends Bloc<ScriptCanvasEvent, ScriptCanvasState> {
  final PdfViewerController controller;
  final ScriptEditorBloc scriptEditorBloc;
  List<Annotation> _annotations = [];
  final AnnotationsRepository _annotationsRepository;
  final MqttRepository mqttRepository;

  late StreamSubscription scriptEditorSubscription;
  late StreamSubscription annotationsSubscription;

  Annotation? selectedAnnotation;
  Annotation? affectedAnnotation;
  Tool? selectedTool;
  int tap = 0;
  bool isDown = false;
  Offset lastCentrePosition = const Offset(0, 0);
  Mode? selectedMode;
  int pointerPage = 0;
  double pointerY = 1;

  Future<void> _fetchAnnotations() async {
    await _annotationsRepository.getAnnotations();
    emit(ScriptCanvasReady(List.from(_annotations)));
  }

  ScriptCanvasBloc(
    this.controller,
    this.scriptEditorBloc,
    this._annotationsRepository,
    this.mqttRepository,
  ) : super(ScriptCanvasInitial()) {
    selectedTool = scriptEditorBloc.state.selectedTool;
    selectedMode = scriptEditorBloc.state.mode;

    _fetchAnnotations();

    annotationsSubscription = _annotationsRepository.annotationsStream.listen((annotations) {
      _annotations = annotations;
      emit(ScriptCanvasReady(List.from(_annotations), indicatorYAxis: state is ScriptCanvasReady ? (state as ScriptCanvasReady).indicatorYAxis : 0.0));
    });

    scriptEditorSubscription = scriptEditorBloc.stream.listen((state) {
      if (state is ScriptEditorLoaded) {
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
      _updateIndicatorPosition();
      
      if (selectedMode != Mode.edit) return;
      if (selectedTool == null) return;

      if (isDown) {
        Offset displacement = controller.centerPosition - lastCentrePosition;
        var updatedAnnotation = AnnotationInteractionHandler().move(displacement, selectedAnnotation!, affectedAnnotation!);
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
          if (selectedAnnotation is Cue) {
            var updatedAnnotation = toolMap[selectedTool].tap2(event.page, cursorPosition, selectedAnnotation!);
            if (updatedAnnotation != null) {
              _annotationsRepository.updateAnnotation(updatedAnnotation);
              scriptEditorBloc.add(EditorChanged(EditorPanel.add_cue));
              scriptEditorBloc.add(UpdateSelectedAnnotationEvent(updatedAnnotation));
            }
          }
          selectedAnnotation = null;
          tap = 0;
        }
      }
      emit(ScriptCanvasReady(List.from(_annotations), indicatorYAxis: state is ScriptCanvasReady ? (state as ScriptCanvasReady).indicatorYAxis : 0.0));
    } else {
      switch (newAnnotation) {
        case Cue _:
          scriptEditorBloc.add(EditorChanged(EditorPanel.add_cue));
          return scriptEditorBloc.add(UpdateSelectedAnnotationEvent(newAnnotation));
      }
    }
  });

    on<PagePanStart>((event, emit) {
      if (selectedMode != Mode.edit) return;
      if (tap != 0) return;

      Offset cursorPos = pdfRescaleCoordinates(event.position, event.pageRect, event.page);
      selectedAnnotation = _annotations.firstWhereOrNull((a) => a.isInObject(a, cursorPos));

      // If the annotation is a Cue, check if the interaction is with its marker
      if (selectedAnnotation is Cue) {
        Cue cue = selectedAnnotation as Cue;
        if (cue.marker != null && cue.marker!.isInObject(cue.marker!, cursorPos)) {
          affectedAnnotation = cue.marker;
        } else {
          affectedAnnotation = cue;
        }
      }
      
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

      if (selectedAnnotation != null && affectedAnnotation != null) {
        var updatedAnnotation = AnnotationInteractionHandler().move(displacement, selectedAnnotation!, affectedAnnotation!, page: event.page, controller: controller);
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
      affectedAnnotation = null;
      emit(ScriptCanvasReady(List.from(_annotations), indicatorYAxis: state is ScriptCanvasReady ? (state as ScriptCanvasReady).indicatorYAxis : 0.0));
    });

    on<UpdateIndicator>((event, emit) {
      emit(ScriptCanvasReady(List.from(_annotations), indicatorYAxis: event.yAxis));
    });
    _initializeMqtt();
  }

  

  void _initializeMqtt() async {
    await mqttRepository.connect();
    mqttRepository.subscribe('local_server/tracker/position', (topic, payload) {
      pointerPage = payload['page_number'];
      pointerY = payload['y_coordinate'];
      _updateIndicatorPosition();
    });
  }

  void _updateIndicatorPosition() {
    try {
    final viewRect = controller.visibleRect;
  } catch (e) {
    // Handle any unexpected errors
    return;
  }
    final viewRect = controller.visibleRect;
    final allRect = controller.documentSize;

    if (allRect.height <= viewRect.height) return;

    double distanceToPointer = controller.pages[pointerPage].height- pointerY;
    for (var i = 1; i < pointerPage; i++) {
      distanceToPointer += controller.pages[i].height;
    }

    final yPosition = (distanceToPointer + controller.value.y) / viewRect.height;

    final vh = viewRect.height * controller.currentZoom;
    final distance = yPosition * vh;

    add(UpdateIndicator(distance));
  }

  @override
  Future<void> close() {
    scriptEditorSubscription.cancel();
    annotationsSubscription.cancel();
    return super.close();
  }
}
