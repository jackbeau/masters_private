import '../../domain/models/annotation.dart';

abstract class AnnotationsProviderBase {
  List<Annotation> getAnnotations();
  void addAnnotation(Annotation annotation);
  void updateAnnotation(Annotation annotation);
  void removeAnnotation(Annotation annotation);
  Future<List<Annotation>> fetchAnnotationsFromAPI();
}