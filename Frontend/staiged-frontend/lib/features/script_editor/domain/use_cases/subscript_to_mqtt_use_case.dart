import '../../data/repositories/mqtt_repository.dart';

class SubscribeToMqttUseCase {
  final MqttRepository repository;

  SubscribeToMqttUseCase(this.repository);

  Future<void> execute(String topic, Function(String topic, Map<String, dynamic> payload) onMessage) async {
    repository.subscribe(topic, onMessage);
  }
}
