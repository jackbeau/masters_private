// lib/domain/bloc/sidebar_bloc.dart
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:intl/intl.dart';
import '../../data/repositories/speech_repository.dart';
import '../models/act.dart';  // Assuming data model exists

abstract class SidebarEvent {}
class LoadActs extends SidebarEvent {}
class UpdateTime extends SidebarEvent {}
class StartSpeechToLine extends SidebarEvent {}
class StopSpeechToLine extends SidebarEvent {}

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

  SidebarBloc(this.speechRepository) : super(SidebarInitial()) {
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

    on<StartSpeechToLine>((event, emit) async {
      try {
        final message = await speechRepository.startSpeechToLine();
        if (state is SidebarLoaded) {
          emit(SidebarLoaded((state as SidebarLoaded).acts, (state as SidebarLoaded).currentTime, message));
        }
      } catch (e) {
        if (state is SidebarLoaded) {
          emit(SidebarLoaded((state as SidebarLoaded).acts, (state as SidebarLoaded).currentTime, 'Error: $e'));
        }
      }
    });

    on<StopSpeechToLine>((event, emit) async {
      try {
        final message = await speechRepository.stopSpeechToLine();
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
