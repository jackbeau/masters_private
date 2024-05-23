import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import '../interfaces/annotation_provider_base.dart';
import '../../domain/models/annotation.dart';
import '../../domain/repository/cue_marker.dart';
import '../../domain/repository/cue_label.dart';

class AnnotationsProvider with ChangeNotifier implements AnnotationsProviderBase {
  List<Annotation> _annotations = [];

  @override
  List<Annotation> getAnnotations() {
    return _annotations;
  }

  @override
  Future<void> addAnnotation(Annotation annotation) async {
    final response = await http.post(
      Uri.parse('http://localhost:4000/api/cues'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(annotation.toJson()),
    );
    if (response.statusCode == 201) {
      final Map<String, dynamic> responseBody = jsonDecode(response.body);
      final newAnnotation = _createAnnotationFromJson(responseBody);
      _annotations.add(newAnnotation);
      notifyListeners(); // Notify listeners immediately after adding
    } else {
      throw Exception('Failed to add annotation');
    }
  }

  @override
  Future<void> updateAnnotation(Annotation annotation) async {
    final response = await http.put(
      Uri.parse('http://localhost:4000/api/cues/${annotation.id}'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(annotation.toJson()),
    );
    if (response.statusCode == 200) {
      final Map<String, dynamic> responseBody = jsonDecode(response.body);
      final updatedAnnotation = _createAnnotationFromJson(responseBody);
      final index = _annotations.indexWhere((a) => a.id == annotation.id);
      if (index != -1) {
        _annotations[index] = updatedAnnotation;
        notifyListeners(); // Notify listeners immediately after updating
      }
    } else {
      throw Exception('Failed to update annotation');
    }
  }

  @override
  Future<void> removeAnnotation(Annotation annotation) async {
    final response = await http.delete(
      Uri.parse('http://localhost:4000/api/cues/${annotation.id}'),
    );
    if (response.statusCode == 200) {
      _annotations.removeWhere((a) => a.id == annotation.id);
      notifyListeners(); // Notify listeners immediately after removing
    } else {
      throw Exception('Failed to delete annotation');
    }
  }

  @override
  Future<List<Annotation>> fetchAnnotationsFromAPI() async {
    final response = await http.get(Uri.parse('http://localhost:4000/api/cues'));
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      _annotations = data.map((item) => _createAnnotationFromJson(item)).toList();
      notifyListeners(); // Notify listeners after fetching data
      return _annotations;
    } else {
      throw Exception('Failed to load annotations');
    }
  }

  Annotation _createAnnotationFromJson(Map<String, dynamic> json) {
    if (json.containsKey('type')) {
      return CueLabel.fromJson(json);
    } else {
      return CueMarker.fromJson(json);
    }
  }
}
