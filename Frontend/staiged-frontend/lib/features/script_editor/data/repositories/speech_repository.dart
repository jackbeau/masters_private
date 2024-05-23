// lib/domain/repository/speech_repository.dart
import '../interfaces/speech_provider_base.dart';

class SpeechRepository {
  final SpeechProviderBase speechProvider;

  SpeechRepository({required this.speechProvider});

  Future<String> startSpeechToLine() async {
    return await speechProvider.startSpeechToLine();
  }

  Future<String> stopSpeechToLine() async {
    return await speechProvider.stopSpeechToLine();
  }
}
