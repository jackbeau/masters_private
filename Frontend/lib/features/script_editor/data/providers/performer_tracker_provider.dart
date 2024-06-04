// lib/data/providers/speech_provider.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../interfaces/performer_tracker_provider_base.dart';

class PerformerTrackerProvider implements PerformerTrackerProviderBase {
  final String baseUrl;

  PerformerTrackerProvider({required this.baseUrl});

  @override
  Future<String> startPerformerTracker() async {
    final response = await http.post(Uri.parse('$baseUrl/performer-tracker/start'));
    if (response.statusCode == 200) {
      final Map<String, dynamic> responseBody = jsonDecode(response.body);
      return responseBody['message'];
    } else {
      throw Exception('Failed to start Performer Tracker process');
    }
  }

  @override
  Future<String> stopPerformerTracker() async {
    final response = await http.post(Uri.parse('$baseUrl/performer-tracker/stop'));
    if (response.statusCode == 200) {
      final Map<String, dynamic> responseBody = jsonDecode(response.body);
      return responseBody['message'];
    } else {
      throw Exception('Failed to stop Performer Tracker process');
    }
  }
}
