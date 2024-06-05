// lib/domain/repository/speech_repository.dart
import '../interfaces/speech_provider_base.dart';

class SpeechRepository {
  final SpeechProviderBase speechProvider;

  SpeechRepository({required this.speechProvider});

  Future<String> startSpeechToScriptPointer() async {
    return await speechProvider.startSpeechToScriptPointer();
  }

  Future<String> stopSpeechToScriptPointer() async {
    return await speechProvider.stopSpeechToScriptPointer();
  }
}
