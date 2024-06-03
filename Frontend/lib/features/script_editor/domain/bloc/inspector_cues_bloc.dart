import 'dart:async';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:stage_assistant/features/script_editor/domain/models/annotation.dart';
import '../models/cue.dart'; // Update this path to wherever your Cue model is defined
import '../../data/repositories/annotations_repository.dart';

// Event definitions
abstract class InspectorCuesEvent {}
class LoadCues extends InspectorCuesEvent {}
class DeleteAnnotationEvent extends InspectorCuesEvent {
  final Cue cue;
  DeleteAnnotationEvent(this.cue);
}

class _AnnotationsUpdated extends InspectorCuesEvent {
  final List<Annotation> annotations;
  _AnnotationsUpdated(this.annotations);
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
    _annotationsSubscription = annotationsRepository.annotationsStream.listen((annotations) {
      add(_AnnotationsUpdated(annotations));
    });

    on<LoadCues>((event, emit) async {
      // No need to manually fetch annotations here as the stream subscription handles updates
    });

    on<DeleteAnnotationEvent>((event, emit) async {
      await annotationsRepository.removeAnnotation(event.cue);
      // _fetchAnnotations();
    });

    on<_AnnotationsUpdated>((event, emit) {
      final cues = event.annotations.whereType<Cue>().toList();
      emit(InspectorCuesLoaded(cues));
    });

    _fetchAnnotations();
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
