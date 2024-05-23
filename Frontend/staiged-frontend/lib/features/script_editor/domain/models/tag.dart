import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';

class TagType {
  String department;
  Color color;
  final String id;

  TagType(this.department, this.color) : id = Uuid().v4();

  TagType.withId(this.id, this.department, this.color);

  Map<String, dynamic> toJson() {
    return {
       'id': id,
      'department': department,
      'color': color.value,
    };
  }

  factory TagType.fromJson(Map<String, dynamic> json) {
    return TagType.withId(
      json['id'],
      json['department'],
      Color(json['color'])
    );
  }
}

class Tag {
  String cue_name;
  String description;
  TagType? type;
  final String id;

  Tag({this.cue_name="", this.type, this.description = ""}) : id = Uuid().v4();
  Tag.withId({required this.id, this.cue_name="", this.type, this.description = ""});

  Tag copyWith({
    String? cue_name,
    String? description,
    TagType? type,
  }) {
    return Tag(
      cue_name: cue_name ?? this.cue_name,
      type: type ?? this.type,
      description: description ?? this.description,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'cue_name': cue_name,
      'description': description,
      'type': type?.toJson(),
    };
  }

  factory Tag.fromJson(Map<String, dynamic> json) {
    return Tag.withId(
      id: json['id'],
      cue_name: json['cue_name'],
      description: json['description'],
      type: json['type'] != null ? TagType.fromJson(json['type']) : null,
    );
  }
}


var fs = TagType.withId("8af46c8a-e38b-4525-a8c2-3c4b988d753", "FS", Colors.blue);
var vfx = TagType.withId("8af46c8a-e38b-45b5-a8c2-3c4b988d753", "VFX", Colors.green);
var lx = TagType.withId("8af46c8a-d38b-45b5-a8c2-3c4b988d753", "LX", Colors.yellow);
var sfx = TagType.withId("8af43c8a-e38b-45b5-a8c2-3c4b988d753", "SFX", Colors.orange);
var sm = TagType.withId("8af46c8a-e37b-45b5-a8c2-3c4b988d753", "VFX", Colors.red);

List<TagType> tagOptions = [fs, vfx, lx, sfx, sm];