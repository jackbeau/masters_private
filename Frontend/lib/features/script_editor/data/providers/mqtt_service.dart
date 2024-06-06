import 'dart:convert';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_browser_client.dart';
import '../interfaces/mqtt_service_base.dart';
import 'package:flutter/foundation.dart';

class MqttService implements MqttServiceBase {
  final String broker = 'ws://0.0.0.0/mqtt';
  final int port = 8000;
  final String clientId = 'flutter_client';

  late MqttBrowserClient client;

  MqttService() {
    client = MqttBrowserClient(broker, clientId);
    client.port = port;
    client.keepAlivePeriod = 60;
    client.onDisconnected = onDisconnected;
    client.onConnected = onConnected;
    client.onSubscribed = onSubscribed;
    client.logging(on: false);
  }

  @override
  Future<void> connect() async {
    try {
      await client.connect();
    } on Exception {
      // debugPrint('Exception: $e');
      client.disconnect();
    }

    client.updates!.listen((List<MqttReceivedMessage<MqttMessage>> c) {
      final MqttPublishMessage message = c[0].payload as MqttPublishMessage;
      final payload = MqttPublishPayload.bytesToStringAsString(message.payload.message);

      // Handle the received message
      final data = jsonDecode(payload);
      final topic = c[0].topic;
      _onMessage?.call(topic, data);
    });
  }

  @override
  void subscribe(String topic, Function(String topic, Map<String, dynamic> payload) onMessage) {
    client.subscribe(topic, MqttQos.atMostOnce);
    _onMessage = onMessage;
  }

  @override
  void publish(String topic, String message) {
    final builder = MqttClientPayloadBuilder();
    builder.addString(message);
    client.publishMessage(topic, MqttQos.atMostOnce, builder.payload!);
  }

  void onConnected() {
    debugPrint('Connected to MQTT broker');
  }

  void onDisconnected() {
    debugPrint('Disconnected from MQTT broker');
  }

  void onSubscribed(String topic) {
    debugPrint('Subscribed to $topic');
  }

  Function(String topic, Map<String, dynamic> payload)? _onMessage;
}
