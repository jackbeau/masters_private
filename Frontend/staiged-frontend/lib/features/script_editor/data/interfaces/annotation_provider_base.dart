import '../../domain/models/annotation.dart';

abstract class AnnotationsProviderBase {
  List<Annotation> getAnnotations();

  Future<void> addAnnotation(Annotation annotation);

  Future<void> updateAnnotation(Annotation annotation);

  Future<void> removeAnnotation(Annotation annotation);

  Future<List<Annotation>> fetchAnnotationsFromAPI();
}
