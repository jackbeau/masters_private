import 'package:flutter_bloc/flutter_bloc.dart';
import '../models/cue.dart'; 
import '../models/tag.dart';
import '../../data/repositories/annotations_repository.dart';

// Event definitions
abstract class CueEditorEvent {}
class LoadCue extends CueEditorEvent {
  final CueLabel? cue;
  LoadCue(this.cue);
}
class AddTag extends CueEditorEvent {
  final Tag tag;
  AddTag(this.tag);
}
class RemoveTag extends CueEditorEvent {
  final int index;
  RemoveTag(this.index);
}
class UpdateTag extends CueEditorEvent {
  final int index;
  final Tag updatedTag;
  UpdateTag(this.index, this.updatedTag);
}
class CueFieldUpdated extends CueEditorEvent {
  final String field;
  final dynamic value;
  CueFieldUpdated(this.field, this.value);
}
class UpdateTagDetail extends CueEditorEvent {
  final int index;
  final String detailKey;
  final dynamic detailValue;

  UpdateTagDetail(this.index, this.detailKey, this.detailValue);
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
  CueLabel? cueDraft;
  final AnnotationsRepository annotationsRepository;

  CueEditorBloc(this.annotationsRepository) : super(CueEditorInitial()) {

    on<LoadCue>((event, emit) {
      cueDraft = event.cue;
      if (cueDraft != null) {
        emit(CueEditorSuccess(cueDraft!));
      }
    });

    on<AddTag>((event, emit) {
      if (cueDraft == null) return;
      cueDraft!.tags.add(event.tag);
      annotationsRepository.updateAnnotation(cueDraft!);
      emit(CueEditorSuccess(cueDraft!));
    });

    on<RemoveTag>((event, emit) {
      if (cueDraft == null) return;
      cueDraft!.tags.removeAt(event.index);
      annotationsRepository.updateAnnotation(cueDraft!);
      emit(CueEditorSuccess(cueDraft!));
    });

    on<UpdateTagDetail>((event, emit) {
      if (cueDraft == null) return;
      Tag tagToUpdate = cueDraft!.tags[event.index];
      switch (event.detailKey) {
        case 'department':
          tagToUpdate = tagToUpdate.copyWith(type: event.detailValue as TagType?);
          break;
        case 'cue':
          tagToUpdate = tagToUpdate.copyWith(cue_name: event.detailValue as String);
          break;
        case 'description':
          tagToUpdate = tagToUpdate.copyWith(description: event.detailValue as String);
          break;
      }
      cueDraft!.tags[event.index] = tagToUpdate;
      annotationsRepository.updateAnnotation(cueDraft!);
      emit(CueEditorSuccess(cueDraft!));
    });

    on<CueFieldUpdated>((event, emit) {
      if (cueDraft == null) {
        emit(CueEditorError('No cue loaded to update'));
        return;
      }
      final updatedCue = applyFieldUpdate(cueDraft!, event.field, event.value);
      annotationsRepository.updateAnnotation(updatedCue);
      emit(CueEditorSuccess(updatedCue));
    });
  }

  CueLabel applyFieldUpdate(CueLabel cue, String field, dynamic value) {
    switch (field) {
      case 'note':
        cueDraft!.note = value;
        return cue.copyWith(note: value as String);
      case 'title':
        cueDraft!.title = value;
        return cue.copyWith(title: value as String);
      case 'autofire':
        cueDraft!.autofire = value;
        return cue.copyWith(autofire: value as bool);
      case 'line':
        cueDraft!.line = value;
        return cue.copyWith(line: value as String);
      case 'message':
        cueDraft!.message = value;
        return cue.copyWith(message: value as String);
      default:
        return cue;
    }
  }
}
