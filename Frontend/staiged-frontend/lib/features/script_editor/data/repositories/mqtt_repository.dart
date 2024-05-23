import '../interfaces/mqtt_service_base.dart';

class MqttRepository {
  final MqttServiceBase mqttService;

  MqttRepository(this.mqttService);

  Future<void> connect() async {
    await mqttService.connect();
  }

  void subscribe(String topic, Function(String topic, Map<String, dynamic> payload) onMessage) {
    mqttService.subscribe(topic, onMessage);
  }

  void publish(String topic, String message) {
    mqttService.publish(topic, message);
  }
}
