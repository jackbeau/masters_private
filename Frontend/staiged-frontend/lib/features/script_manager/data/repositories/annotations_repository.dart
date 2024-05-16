import 'dart:async';
import '../interfaces/annotation_provider_base.dart';
import '../../domain/models/annotation.dart';
import '../../domain/repository/cue_label.dart';
import '../../domain/repository/cue_marker.dart';


class AnnotationsRepository {
  final AnnotationsProviderBase annotationsProvider;
  final _annotationsController = StreamController<List<Annotation>>.broadcast();

  AnnotationsRepository(this.annotationsProvider);

  Stream<List<Annotation>> get annotationsStream => _annotationsController.stream;

  Future<void> getAnnotations() async {
    final annotations = await annotationsProvider.fetchAnnotationsFromAPI();
    _updateAnnotationsStream(annotations);
  }

  Future<void> addAnnotation(Annotation annotation) async {
    annotationsProvider.addAnnotation(annotation);
    final annotations = annotationsProvider.getAnnotations();
    _updateAnnotationsStream(annotations);
  }

  Future<void> updateAnnotation(Annotation annotation) async {
    annotationsProvider.updateAnnotation(annotation);
    final annotations = annotationsProvider.getAnnotations();
    _updateAnnotationsStream(annotations);
  }

  Future<void> removeAnnotation(Annotation annotation) async {
    annotationsProvider.removeAnnotation(annotation);
    final annotations = annotationsProvider.getAnnotations();
    _updateAnnotationsStream(annotations);
  }

  Future<void> removeCueLabelAndMarkers(CueLabel cueLabel) async {
    // Remove the CueLabel
    annotationsProvider.removeAnnotation(cueLabel);

    // Remove associated CueMarkers
    final annotations = annotationsProvider.getAnnotations();
    for (var annotation in annotations) {
      if (annotation is CueMarker && annotation.label == cueLabel) {
        annotationsProvider.removeAnnotation(annotation);
      }
    }

    // Refresh the annotations stream
    final updatedAnnotations = annotationsProvider.getAnnotations();
    _updateAnnotationsStream(updatedAnnotations);
  }

  void _updateAnnotationsStream(List<Annotation> annotations) {
    _annotationsController.add(List.unmodifiable(annotations));
  }

  void dispose() {
    _annotationsController.close();
  }
}
