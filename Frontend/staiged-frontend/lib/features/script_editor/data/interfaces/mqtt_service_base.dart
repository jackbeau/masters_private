abstract class MqttServiceBase {
  Future<void> connect();
  void subscribe(String topic, Function(String topic, Map<String, dynamic> payload) onMessage);
  void publish(String topic, String message);
}
