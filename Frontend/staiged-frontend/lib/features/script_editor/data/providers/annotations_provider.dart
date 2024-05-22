import '../interfaces/annotation_provider_base.dart';
import '../../domain/models/annotation.dart';

class AnnotationsProvider implements AnnotationsProviderBase {
  List<Annotation> _annotations = [];

  @override
  List<Annotation> getAnnotations() {
    return _annotations;
  }

  @override
  void addAnnotation(Annotation annotation) {
    _annotations.add(annotation);
  }

  @override
  void updateAnnotation(Annotation annotation) {
    final index = _annotations.indexWhere((a) => a.id == annotation.id);
    if (index != -1) {
      _annotations[index] = annotation;
    }
  }

  @override
  void removeAnnotation(Annotation annotation) {
    _annotations.removeWhere((a) => a.id == annotation.id);
  }

  @override
  Future<List<Annotation>> fetchAnnotationsFromAPI() async {
    // Call to API to fetch annotations
    return _annotations; // Replace with actual API call
  }
}
