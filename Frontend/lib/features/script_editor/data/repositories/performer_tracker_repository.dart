// lib/domain/repository/speech_repository.dart
import '../interfaces/performer_tracker_provider_base.dart';

class PerformerTrackerRepository{
  final PerformerTrackerProviderBase performerTrackerProvider;

  PerformerTrackerRepository({required this.performerTrackerProvider});

  Future<String> startPerformerTracker() async {
    return await performerTrackerProvider.startPerformerTracker();
  }

  Future<String> stopPerformerTracker() async {
    return await performerTrackerProvider.stopPerformerTracker();
  }
}
