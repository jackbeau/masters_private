// lib/domain/bloc/sidebar_bloc.dart
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:intl/intl.dart';
import 'package:stage_assistant/features/script_editor/data/repositories/performer_tracker_repository.dart';
import '../../data/repositories/speech_repository.dart';
import '../models/act.dart';  // Assuming data model exists

abstract class SidebarEvent {}
class LoadActs extends SidebarEvent {}
class UpdateTime extends SidebarEvent {}
class StartSpeechToScriptPointer extends SidebarEvent {}
class StopSpeechToScriptPointer extends SidebarEvent {}
class StartPerformerTracker extends SidebarEvent {}
class StopPerformerTracker extends SidebarEvent {}

abstract class SidebarState {}
class SidebarInitial extends SidebarState {}
class SidebarLoaded extends SidebarState {
  final List<Act> acts;
  final String currentTime;
  final String message; // Add a message field

  SidebarLoaded(this.acts, this.currentTime, [this.message = '']);
}

class SidebarBloc extends Bloc<SidebarEvent, SidebarState> {
  final SpeechRepository speechRepository;
  final PerformerTrackerRepository performerTrackerRepository;

  SidebarBloc(this.speechRepository, this.performerTrackerRepository) : super(SidebarInitial()) {
    on<LoadActs>((event, emit) {
      final acts = <Act>[
        Act(title: 'Act I', scenes: ['Prologue', 'Scene 1', 'Scene 2']),
        Act(title: 'Act II', scenes: []),
        // More acts
      ];
      emit(SidebarLoaded(acts, _formatCurrentTime()));
    });

    on<UpdateTime>((event, emit) {
      if (state is SidebarLoaded) {
        emit(SidebarLoaded((state as SidebarLoaded).acts, _formatCurrentTime()));
      }
    });

    on<StartSpeechToScriptPointer>((event, emit) async {
      try {
        final message = await speechRepository.startSpeechToScriptPointer();
        if (state is SidebarLoaded) {
          emit(SidebarLoaded((state as SidebarLoaded).acts, (state as SidebarLoaded).currentTime, message));
        }
      } catch (e) {
        if (state is SidebarLoaded) {
          emit(SidebarLoaded((state as SidebarLoaded).acts, (state as SidebarLoaded).currentTime, 'Error: $e'));
        }
      }
    });

    on<StopSpeechToScriptPointer>((event, emit) async {
      try {
        final message = await speechRepository.stopSpeechToScriptPointer();
        if (state is SidebarLoaded) {
          emit(SidebarLoaded((state as SidebarLoaded).acts, (state as SidebarLoaded).currentTime, message));
        }
      } catch (e) {
        if (state is SidebarLoaded) {
          emit(SidebarLoaded((state as SidebarLoaded).acts, (state as SidebarLoaded).currentTime, 'Error: $e'));
        }
      }
    });

    on<StartPerformerTracker>((event, emit) async {
      try {
        final message = await performerTrackerRepository.startPerformerTracker();
        if (state is SidebarLoaded) {
          emit(SidebarLoaded((state as SidebarLoaded).acts, (state as SidebarLoaded).currentTime, message));
        }
      } catch (e) {
        if (state is SidebarLoaded) {
          emit(SidebarLoaded((state as SidebarLoaded).acts, (state as SidebarLoaded).currentTime, 'Error: $e'));
        }
      }
    });

    on<StopPerformerTracker>((event, emit) async {
      try {
        final message = await performerTrackerRepository.stopPerformerTracker();
        if (state is SidebarLoaded) {
          emit(SidebarLoaded((state as SidebarLoaded).acts, (state as SidebarLoaded).currentTime, message));
        }
      } catch (e) {
        if (state is SidebarLoaded) {
          emit(SidebarLoaded((state as SidebarLoaded).acts, (state as SidebarLoaded).currentTime, 'Error: $e'));
        }
      }
    });
  }

  String _formatCurrentTime() {
    return DateFormat('HH:mm:ss').format(DateTime.now());
  }
}
