import 'dart:async';
import '../interfaces/annotation_provider_base.dart';
import '../providers/annotations_provider.dart';
import '../../domain/models/annotation.dart';

class AnnotationsRepository {
  final AnnotationsProviderBase annotationsProvider;
  final _annotationsController = StreamController<List<Annotation>>.broadcast();

  AnnotationsRepository(this.annotationsProvider) {
    if (annotationsProvider is AnnotationsProvider) {
      (annotationsProvider as AnnotationsProvider).onAnnotationsUpdated = _updateAnnotationsStream;
    }
  }

  Stream<List<Annotation>> get annotationsStream => _annotationsController.stream;

  Future<void> initialize() async {
    await annotationsProvider.init();
    await getAnnotations();
  }

  Future<void> getAnnotations() async {
    final annotations = await annotationsProvider.fetchAnnotationsFromAPI();
    _updateAnnotationsStream(annotations);
  }

  Future<void> addAnnotation(Annotation annotation) async {
    await annotationsProvider.addAnnotation(annotation);
    _updateAnnotationsStream(annotationsProvider.getAnnotations());
  }

  Future<void> updateAnnotation(Annotation annotation) async {
    await annotationsProvider.updateAnnotation(annotation);
    _updateAnnotationsStream(annotationsProvider.getAnnotations());
  }

  Future<void> removeAnnotation(Annotation annotation) async {
    await annotationsProvider.removeAnnotation(annotation);
    _updateAnnotationsStream(annotationsProvider.getAnnotations());
  }

  void _updateAnnotationsStream(List<Annotation> annotations) {
    _annotationsController.add(List.unmodifiable(annotations));
  }

  void dispose() {
    _annotationsController.close();
  }
}
