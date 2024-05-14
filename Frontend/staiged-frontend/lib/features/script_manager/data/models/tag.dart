import 'package:flutter/material.dart';

class TagType {
  String department;
  Color color;

  TagType(this.department, this.color);
}

class Tag {
  String cue_name;
  String description;
  TagType type;

  Tag(this.cue_name, this.type, {this.description = ""});
}