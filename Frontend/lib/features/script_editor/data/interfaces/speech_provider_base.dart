// lib/data/interfaces/speech_provider_base.dart
abstract class SpeechProviderBase {
  Future<String> startSpeechToLine();
  Future<String> stopSpeechToLine();
}
