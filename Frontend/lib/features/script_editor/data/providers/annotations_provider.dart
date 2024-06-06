import 'dart:convert';
import 'dart:async';
import 'package:uuid/uuid.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:http/http.dart' as http;
import 'dart:math';

import '../interfaces/annotation_provider_base.dart';
import '../../domain/models/annotation.dart';
import '../../domain/models/cue.dart';

class AnnotationsProvider implements AnnotationsProviderBase {
  List<Annotation> _annotations = [];
  late String _nodeId;
  WebSocketChannel? _channel;
  List<Map<String, dynamic>> _changeQueue = [];
  final Set<String> _pendingChanges = {}; // Track pending changes
  int _reconnectAttempts = 0;
  final Random _random = Random();
  Function(List<Annotation>)? onAnnotationsUpdated;

  AnnotationsProvider({this.onAnnotationsUpdated});

  Timer? _debounceTimer;

  @override
  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _nodeId = prefs.getString('nodeId') ?? const Uuid().v4();
    if (_nodeId.isEmpty) {
      _nodeId = const Uuid().v4();
      await prefs.setString('nodeId', _nodeId);
    }
    await fetchAnnotationsFromAPI();
    await _loadLocalChanges();
    _initializeWebSocket();
    _syncChanges();
  }

  @override
  List<Annotation> getAnnotations() {
    return _annotations;
  }

  @override
  Future<void> addAnnotation(Annotation annotation) async {
    final changeId = const Uuid().v4();
    _annotations.add(annotation);
    _queueChange({
      'id': changeId,
      'type': 'add',
      'annotation': annotation.toJson(),
      'timestamp': DateTime.now().millisecondsSinceEpoch
    });
    _pendingChanges.add(changeId);
    _debounceSyncChanges();
  }

  @override
  Future<void> updateAnnotation(Annotation annotation) async {
    final changeId = const Uuid().v4();
    final index = _annotations.indexWhere((a) => a.id == annotation.id);
    if (index != -1) {
      _annotations[index] = annotation;
      _queueChange({
        'id': changeId,
        'type': 'update',
        'annotation': annotation.toJson(),
        'timestamp': DateTime.now().millisecondsSinceEpoch
      });
      _pendingChanges.add(changeId);
      _debounceSyncChanges();
    }
  }

  @override
  Future<void> removeAnnotation(Annotation annotation) async {
    final changeId = const Uuid().v4();
    _annotations.removeWhere((a) => a.id == annotation.id);
    _queueChange({
      'id': changeId,
      'type': 'delete',
      'annotation': annotation.toJson(),
      'timestamp': DateTime.now().millisecondsSinceEpoch
    });
    _pendingChanges.add(changeId);
    _debounceSyncChanges();
  }

  @override
  Future<List<Annotation>> fetchAnnotationsFromAPI() async {
    final response = await http.get(Uri.parse('http://localhost:4000/api/cues'));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      if (data != null && data.containsKey('annotations')) {
        final annotationsList = data['annotations'] as List<dynamic>;
        _annotations = annotationsList.map((item) => _createAnnotationFromJson(item)).toList();
      } else {
        _annotations = [];
      }
      return _annotations;
    } else {
      throw Exception('Failed to load annotations');
    }
  }

  void _applyRemoteAnnotations(List<dynamic> annotations) {
    _annotations = annotations.map((item) => _createAnnotationFromJson(item)).toList();
    // onAnnotationsUpdated?.call(_annotations);
  }

  void _applyRemoteChanges(List<dynamic> changes) {
    final now = DateTime.now().millisecondsSinceEpoch;
    for (var change in changes) {
      final changeId = change['id'];
      if (_pendingChanges.contains(changeId)) {
        // Remove from pending changes and skip processing
        _pendingChanges.remove(changeId);
        continue;
      }
      final timestamp = change['timestamp'] ?? now;
      switch (change['type']) {
        case 'add':
          final annotation = _createAnnotationFromJson(change['annotation']);
          if (_annotations.any((a) => a.id == annotation.id)) {
            final index = _annotations.indexWhere((a) => a.id == annotation.id);
            if (timestamp >= (_annotations[index].timestamp ?? 0)) {
              _annotations[index] = annotation;
              _annotations[index].timestamp = timestamp;
            }
          } else {
            annotation.timestamp = timestamp;
            _annotations.add(annotation);
          }
          break;
        case 'update':
          final index = _annotations.indexWhere((a) => a.id == change['annotation']['id']);
          if (index != -1 && timestamp >= (_annotations[index].timestamp ?? 0)) {
            _annotations[index] = _createAnnotationFromJson(change['annotation']);
            _annotations[index].timestamp = timestamp;
          }
          break;
        case 'delete':
          _annotations.removeWhere((a) => a.id == change['annotation']['id']);
          break;
      }
    }
    onAnnotationsUpdated?.call(_annotations);
  }

  void _queueChange(Map<String, dynamic> change) async {
    _changeQueue.add(change);
    final prefs = await SharedPreferences.getInstance();
    prefs.setString('changeQueue', jsonEncode(_changeQueue));
  }

  Future<void> _loadLocalChanges() async {
    final prefs = await SharedPreferences.getInstance();
    final savedQueue = prefs.getString('changeQueue');
    if (savedQueue != null) {
      _changeQueue = List<Map<String, dynamic>>.from(jsonDecode(savedQueue));
    } else {
      _changeQueue = [];
    }
  }

  void _syncChanges() async {
    if (_changeQueue.isEmpty) return;

    final changes = List<Map<String, dynamic>>.from(_changeQueue);
    _channel?.sink.add(jsonEncode({'changes': changes}));
    // Do not clear the change queue here. Wait for acknowledgment
  }

  void _debounceSyncChanges() {
    if (_debounceTimer?.isActive ?? false) _debounceTimer!.cancel();
    _debounceTimer = Timer(const Duration(milliseconds: 500), _syncChanges); // Increase debounce time
  }

  Annotation _createAnnotationFromJson(Map<String, dynamic> json) {
    return Cue.fromJson(json);
  }

  void _initializeWebSocket() {
    _channel = WebSocketChannel.connect(Uri.parse('ws://localhost:4000'));

    _syncChanges();

    _channel!.stream.listen((message) {
      final data = jsonDecode(message);
      if (data != null && data.containsKey('changes')) {
        _applyRemoteChanges(data['changes']);
      } else if (data != null && data.containsKey('annotations')) {
        _applyRemoteAnnotations(data['annotations']);
      } else if (data != null && data.containsKey('ack')) {
        _acknowledgeChanges(data['ack']);
      }
    }, onDone: _handleWebSocketDone, onError: _handleWebSocketError);
  }

  void _handleWebSocketDone() {
    _reconnect();
  }

  void _handleWebSocketError(error) {
    print('WebSocket error: $error');
    _reconnect();
  }

  void _reconnect() {
    _channel = null;
    _reconnectAttempts++;
    final delay = _calculateBackoff(_reconnectAttempts);
    Future.delayed(Duration(milliseconds: delay), () {
      print('Attempting to reconnect...');
      _initializeWebSocket();
    });
  }

  int _calculateBackoff(int attempts) {
    const minDelay = 1000; // 1 second
    const maxDelay = 30000; // 30 seconds
    final baseDelay = minDelay * pow(2, attempts).toInt();
    final jitter = _random.nextInt(1000); // Add up to 1 second of jitter
    return min(baseDelay + jitter, maxDelay);
  }

  void _acknowledgeChanges(List<dynamic> ackIds) async {
    for (var ackId in ackIds) {
      _pendingChanges.remove(ackId);
    }
    // Clear only acknowledged changes from the queue
    _changeQueue.removeWhere((change) => ackIds.contains(change['id']));
    final prefs = await SharedPreferences.getInstance();
    prefs.setString('changeQueue', jsonEncode(_changeQueue));
  }
}
