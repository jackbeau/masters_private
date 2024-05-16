import 'dart:async';
import '../interfaces/annotation_provider_base.dart';
import '../../domain/models/annotation.dart';

class AnnotationsRepository {
  final AnnotationsProviderBase annotationsProvider;
  final _annotationsController = StreamController<List<Annotation>>.broadcast();
  List<Annotation> _annotations = [];

  AnnotationsRepository(this.annotationsProvider);

  Stream<List<Annotation>> get annotationsStream => _annotationsController.stream;

  Future<void> getAnnotations() async {
    _annotations = await annotationsProvider.fetchAnnotationsFromAPI();
    _annotationsController.add(_annotations);
  }

  void addAnnotation(Annotation annotation) {
    annotationsProvider.addAnnotation(annotation);
    _annotations.add(annotation);
    _annotationsController.add(_annotations);
  }

  void updateAnnotation(Annotation annotation) {
    annotationsProvider.updateAnnotation(annotation);
    final index = _annotations.indexWhere((a) => a.id == annotation.id);
    if (index != -1) {
      _annotations[index] = annotation;
    }
    _annotationsController.add(_annotations);
  }


  void removeAnnotation(Annotation annotation) {
    annotationsProvider.removeAnnotation(annotation);
    _annotations.removeWhere((a) => a.id == annotation.id);
    _annotationsController.add(_annotations);
  }

  void dispose() {
    _annotationsController.close();
  }
}
