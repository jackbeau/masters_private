// lib/data/providers/speech_provider.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../interfaces/speech_provider_base.dart';

class SpeechProvider implements SpeechProviderBase {
  final String baseUrl;

  SpeechProvider({required this.baseUrl});

  @override
  Future<String> startSpeechToScriptPointer() async {
    final response = await http.post(Uri.parse('$baseUrl/speech-to-script-pointer/start'));
    if (response.statusCode == 200) {
      final Map<String, dynamic> responseBody = jsonDecode(response.body);
      return responseBody['message'];
    } else {
      throw Exception('Failed to start SpeechToScriptPointer process');
    }
  }

  @override
  Future<String> stopSpeechToScriptPointer() async {
    final response = await http.post(Uri.parse('$baseUrl/speech-to-script-pointer/stop'));
    if (response.statusCode == 200) {
      final Map<String, dynamic> responseBody = jsonDecode(response.body);
      return responseBody['message'];
    } else {
      throw Exception('Failed to stop SpeechToScriptPointer process');
    }
  }
}
