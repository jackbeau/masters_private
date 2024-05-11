import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:intl/intl.dart';
import '../../data/models/act.dart';  // Assuming data model exists

abstract class SidebarEvent {}
class LoadActs extends SidebarEvent {}
class UpdateTime extends SidebarEvent {}

abstract class SidebarState {}
class SidebarInitial extends SidebarState {}
class SidebarLoaded extends SidebarState {
  final List<Act> acts;
  final String currentTime;
  SidebarLoaded(this.acts, this.currentTime);
}

class SidebarBloc extends Bloc<SidebarEvent, SidebarState> {
  SidebarBloc() : super(SidebarInitial()) {
    on<LoadActs>((event, emit) {
      // Load acts data from a repository or static list
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
  }

  String _formatCurrentTime() {
    return DateFormat('HH:mm:ss').format(DateTime.now());
  }
}
