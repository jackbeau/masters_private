import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';

abstract class Annotation {
  DateTime? timestamp;

  void draw(Canvas canvas);
  bool isInObject(Annotation annotation, Offset interactionPosition);
  final String id;

  Annotation() : id = const Uuid().v4();

  Annotation.withId(this.id);

  Map<String, dynamic> toJson() {
    return {
      'id': id,
    };
  }

  static Annotation fromJson(Map<String, dynamic> json) {
    throw UnimplementedError('fromJson() should be implemented in subclasses');
  }
}