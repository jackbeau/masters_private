import 'package:flutter/material.dart';

class TagType {
  String department;
  Color color;
  final UniqueKey id = UniqueKey();

  TagType(this.department, this.color);
}

class Tag {
  String cue_name;
  String description;
  TagType? type;
  final UniqueKey id = UniqueKey();

  Tag({this.cue_name="", this.type, this.description = ""});

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
}


var fs = TagType("FS", Colors.blue);
var vfx = TagType("VFX", Colors.green);
var lx = TagType("LX", Colors.yellow);
var sfx = TagType("SFX", Colors.orange);
var sm = TagType("VFX", Colors.red);

List<TagType> tagOptions = [fs, vfx, lx, sfx, sm];