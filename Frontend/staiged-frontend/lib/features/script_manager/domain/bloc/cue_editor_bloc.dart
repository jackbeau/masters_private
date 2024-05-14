import 'package:flutter_bloc/flutter_bloc.dart';
import '../cue.dart'; // Update this path to the actual location of your Cue model.
import '../../data/models/tag.dart'; // Update this path to the actual location of your Cue model.

// Event definitions
abstract class CueEditorEvent {}
class LoadCue extends CueEditorEvent {
  final Cue? cue;
  LoadCue(this.cue);
}
class CueFieldUpdated extends CueEditorEvent {
  final String field;
  final dynamic value;
  CueFieldUpdated(this.field, this.value);
}
class SubmitCue extends CueEditorEvent {}

// State definitions
abstract class CueEditorState {}
class CueEditorInitial extends CueEditorState {}
class CueEditorLoading extends CueEditorState {}
class CueEditorSuccess extends CueEditorState {
  final Cue? cue;
  CueEditorSuccess(this.cue);
}
class CueEditorError extends CueEditorState {
  final String error;
  CueEditorError(this.error);
}

// BLoC definition
class CueEditorBloc extends Bloc<CueEditorEvent, CueEditorState> {
  Cue? cueDraft;



  CueEditorBloc() : super(CueEditorInitial()) {

    on<LoadCue>((event, emit) {
      if (event.cue != null) {
      cueDraft = event.cue;  // Set the draft to the loaded Cue
      emit(CueEditorSuccess(cueDraft!));  // Emit success with the loaded cue
      }

    });

    on<CueFieldUpdated>((event, emit) {
      if (cueDraft == null) {
        emit(CueEditorError('No cue loaded to update'));
        return;
      }
      final updatedCue = applyFieldUpdate(cueDraft!, event.field, event.value);
      emit(CueEditorSuccess(cueDraft!)); // Emit success with updated draft
      print(updatedCue);
      // Todo, sent to network and update UI
    });

    // on<SubmitCue>(async (event, emit) {
    //   emit(CueEditorLoading());
    //   try {
    //     // Simulate sending data to the server or use an actual repository method
    //     // Assuming success if no exceptions
    //     emit(CueEditorSuccess(cueDraft));
    //   } catch (e) {
    //     emit(CueEditorError(e.toString()));
    //   }
    // });
  }

  Cue applyFieldUpdate(Cue cue, String field, dynamic value) {
    switch (field) {
      case 'tags':
        return cue.copyWith(tags: value as List<Tag>);
      case 'note':
        return cue.copyWith(note: value as String);
      case 'title':
        return cue.copyWith(title: value as String);
      case 'autofire':
        return cue.copyWith(autofire: value as bool);
      case 'line':
        return cue.copyWith(line: value as String);
      case 'message':
        return cue.copyWith(message: value as String);
      default:
        return cue; // No field matched
    }
  }
}
