import 'dart:async';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:staiged/features/script_manager/domain/models/annotation.dart';
import '../models/cue.dart'; // Update this path to wherever your Cue model is defined
import '../../data/repositories/annotations_repository.dart';

// Event definitions
abstract class InspectorCuesEvent {}
class LoadCues extends InspectorCuesEvent {}

// State definitions
abstract class InspectorCuesState {}
class InspectorCuesInitial extends InspectorCuesState {}
class InspectorCuesLoaded extends InspectorCuesState {
  final List<CueLabel> cues;
  InspectorCuesLoaded(this.cues);
}

// BLoC definition
class InspectorCuesBloc extends Bloc<InspectorCuesEvent, InspectorCuesState> {
  final AnnotationsRepository annotationsRepository;
  late StreamSubscription<List<Annotation>> _annotationsSubscription;

  InspectorCuesBloc(this.annotationsRepository) : super(InspectorCuesInitial()) {
    _fetchAnnotations();

    _annotationsSubscription = annotationsRepository.annotationsStream.listen((annotations) {
      final cues = annotations.whereType<CueLabel>().toList();
      emit(InspectorCuesLoaded(cues));
    });

    on<LoadCues>((event, emit) async {
      // No need to manually fetch annotations here as the stream subscription handles updates
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
