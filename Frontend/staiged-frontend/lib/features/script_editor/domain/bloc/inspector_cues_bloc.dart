import 'dart:async';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:staiged/features/script_editor/domain/models/annotation.dart';
import '../models/cue.dart'; // Update this path to wherever your Cue model is defined
import '../../data/repositories/annotations_repository.dart';

// Event definitions
abstract class InspectorCuesEvent {}
class LoadCues extends InspectorCuesEvent {}
class DeleteAnnotationEvent extends InspectorCuesEvent {
  final Cue cue;
  DeleteAnnotationEvent(this.cue);
}

// State definitions
abstract class InspectorCuesState {}
class InspectorCuesInitial extends InspectorCuesState {}
class InspectorCuesLoaded extends InspectorCuesState {
  final List<Cue> cues;
  InspectorCuesLoaded(this.cues);
}

// BLoC definition
class InspectorCuesBloc extends Bloc<InspectorCuesEvent, InspectorCuesState> {
  final AnnotationsRepository annotationsRepository;
  late StreamSubscription<List<Annotation>> _annotationsSubscription;

  InspectorCuesBloc(this.annotationsRepository) : super(InspectorCuesInitial()) {
    _fetchAnnotations();

    _annotationsSubscription = annotationsRepository.annotationsStream.listen((annotations) {
      final cues = annotations.whereType<Cue>().toList();
      emit(InspectorCuesLoaded(cues));
    });

    on<LoadCues>((event, emit) async {
      // No need to manually fetch annotations here as the stream subscription handles updates
    });

    on<DeleteAnnotationEvent>((event, emit) async {
      await annotationsRepository.removeAnnotation(event.cue);
      _fetchAnnotations();
    });
  }

  Future<void> _fetchAnnotations() async {
    await annotationsRepository.getAnnotations();
  }

  @override
  Future<void> close() {
    _annotationsSubscription.cancel();
    return super.close();
  }
}
