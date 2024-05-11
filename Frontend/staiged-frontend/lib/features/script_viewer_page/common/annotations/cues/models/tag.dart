import 'package:flutter/material.dart';

class TagType {
  String name;
  Color color;

  TagType(this.name, this.color);
}

class Tag {
  String name;
  TagType type;

  Tag(this.name, this.type);
}