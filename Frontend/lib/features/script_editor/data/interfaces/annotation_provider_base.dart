import '../../domain/models/annotation.dart';

abstract class AnnotationsProviderBase {
  Future<void> init();
  Future<List<Annotation>> fetchAnnotationsFromAPI();
  Future<void> addAnnotation(Annotation annotation);
  Future<void> updateAnnotation(Annotation annotation);
  Future<void> removeAnnotation(Annotation annotation);
  List<Annotation> getAnnotations();
}
