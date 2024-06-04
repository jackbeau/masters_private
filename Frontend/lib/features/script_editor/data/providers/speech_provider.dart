// lib/data/providers/speech_provider.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../interfaces/speech_provider_base.dart';

class SpeechProvider implements SpeechProviderBase {
  final String baseUrl;

  SpeechProvider({required this.baseUrl});

  @override
  Future<String> startSpeechToLine() async {
    final response = await http.post(Uri.parse('$baseUrl/speech-to-line/start'));
    if (response.statusCode == 200) {
      final Map<String, dynamic> responseBody = jsonDecode(response.body);
      return responseBody['message'];
    } else {
      throw Exception('Failed to start SpeechToLine process');
    }
  }

  @override
  Future<String> stopSpeechToLine() async {
    final response = await http.post(Uri.parse('$baseUrl/speech-to-line/stop'));
    if (response.statusCode == 200) {
      final Map<String, dynamic> responseBody = jsonDecode(response.body);
      return responseBody['message'];
    } else {
      throw Exception('Failed to stop SpeechToLine process');
    }
  }
}
