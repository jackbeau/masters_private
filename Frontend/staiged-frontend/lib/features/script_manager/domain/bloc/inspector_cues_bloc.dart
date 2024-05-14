import 'package:flutter/material.dart';

import 'package:flutter_bloc/flutter_bloc.dart';
import '../cue.dart'; // Update this path to wherever your Cue model is defined
import '../../data/models/tag.dart';
import '../../data/models/cue_type.dart';

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

    var fs = TagType("FS", Colors.blue);
    var vfx = TagType("VFX", Colors.green);
    // Define some sample Tags
    var tags = [
      Tag("1", fs),
      // Tag("3", vfx),
      // Tag("5", vfx),
    ];

    on<LoadCues>((event, emit) {
      // Assume data is loaded from a repository or static list
      final cues = <Cue>[
        Cue(page: 1, pos: Offset(0, 0), type: goType, tags: tags, note: "A description of the cue",),
        Cue(page: 1, pos: Offset(0, 0), type: goType, tags: tags, note: "A description of the cue",),
        // Cue(id: "SFX 2", title: "Rain", description: "A description of the cue", actScene: "Act 1 Scene 3"),
        // Additional cues
      ];
      emit(InspectorPanelALoaded(cues));
    });
  }
}
