import 'dart:async';
import '../interfaces/annotation_provider_base.dart';
import '../../domain/models/annotation.dart';
import '../../domain/repository/cue_label.dart';
import '../../domain/models/cue_marker.dart';

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
    await annotationsProvider.addAnnotation(annotation); // Await the async operation
    final annotations = annotationsProvider.getAnnotations();
    _updateAnnotationsStream(annotations);
  }

  Future<void> updateAnnotation(Annotation annotation) async {
    await annotationsProvider.updateAnnotation(annotation); // Await the async operation
    final annotations = annotationsProvider.getAnnotations();
    _updateAnnotationsStream(annotations);
  }

  Future<void> removeAnnotation(Annotation annotation) async {
    await annotationsProvider.removeAnnotation(annotation); // Await the async operation
    final annotations = annotationsProvider.getAnnotations();
    _updateAnnotationsStream(annotations);
  }

  void _updateAnnotationsStream(List<Annotation> annotations) {
    _annotationsController.add(List.unmodifiable(annotations));
  }

  void dispose() {
    _annotationsController.close();
  }
}
