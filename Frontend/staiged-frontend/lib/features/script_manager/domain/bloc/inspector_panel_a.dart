import 'package:flutter_bloc/flutter_bloc.dart';
import '../../data/models/cue.dart';

abstract class InspectorPanelAEvent {}
class LoadCues extends InspectorPanelAEvent {}

abstract class InspectorPanelAState {}
class InspectorPanelAInitial extends InspectorPanelAState {}
class InspectorPanelALoaded extends InspectorPanelAState {
  final List<Cue> cues;
  InspectorPanelALoaded(this.cues);
}

class InspectorPanelABloc extends Bloc<InspectorPanelAEvent, InspectorPanelAState> {
  InspectorPanelABloc() : super(InspectorPanelAInitial()) {
    on<LoadCues>((event, emit) {
      // Assume data is loaded from a repository or static list
      final cues = <Cue>[
        Cue(id: "SFX 1", title: "Thunder", description: "A description of the cue", actScene: "Act 1 Scene 3"),
        Cue(id: "SFX 2", title: "Rain", description: "A description of the cue", actScene: "Act 1 Scene 3"),
        // Additional cues
      ];
      emit(InspectorPanelALoaded(cues));
    });
  }
}
