import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:staiged/features/script_manager/data/models/annotation.dart';
import 'package:staiged/features/script_manager/domain/cue.dart';
import '../../../domain/bloc/script_manager_bloc.dart';
import '../../../domain/bloc/cue_editor_bloc.dart';
import '../../../data/models/tag.dart';

class TagController {
  UniqueKey? department;
  TextEditingController cueController;
  TextEditingController descriptionController;

  TagController({this.department, String? cue, String? description})
      : cueController = TextEditingController(text: cue),
        descriptionController = TextEditingController(text: description);
}

class CueEditor extends StatefulWidget {
  @override
  _CueEditorState createState() => _CueEditorState();
}

class _CueEditorState extends State<CueEditor> {
  final _formKey = GlobalKey<FormState>();
  late List<TagController> _tagControllers;
  late TextEditingController _noteController;
  late TextEditingController _titleController;
  late TextEditingController _lineController;
  late TextEditingController _messageController;
  bool _autofire = false;
  late List<Widget> _tagWidgets;

  @override
  void initState() {
    print("hi3");
    super.initState();
    _tagControllers = [];
    _noteController = TextEditingController();
    _titleController = TextEditingController();
    _lineController = TextEditingController();
    _messageController = TextEditingController();
    _tagWidgets = [];
  }

  @override
  void dispose() {
    _tagControllers.forEach((tagController) {
      tagController.cueController.dispose();
      tagController.descriptionController.dispose();
     });
    _noteController.dispose();
    _titleController.dispose();
    _lineController.dispose();
    _messageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return BlocProvider<CueEditorBloc>(
      create: (_) {
        // Fetch current selectedAnnotation value on first build
        print("hi");
        final selectedAnnotation = context.read<ScriptManagerBloc>().state.selectedAnnotation;
        final cueEditorBloc = CueEditorBloc();
        if (selectedAnnotation is Cue) {
          cueEditorBloc.add(LoadCue(selectedAnnotation));
          _buildTagControllers(selectedAnnotation.tags);
          _titleController.text = selectedAnnotation.title;
          _noteController.text = selectedAnnotation.note;
          _autofire = selectedAnnotation.autofire;
          _lineController.text = selectedAnnotation.line;
          _messageController.text = selectedAnnotation.message;

        }
        return cueEditorBloc;
      },
      child: BlocListener<ScriptManagerBloc, ScriptManagerState>(
        // Subscribe to subsequent updates
        listener: (context, state) {
            if (state.selectedAnnotation is Cue) {
              var cue = state.selectedAnnotation as Cue;
              _buildTagControllers(cue.tags);
              _titleController.text = cue.title;
              _noteController.text = cue.note;
              _autofire = cue.autofire;
              _lineController.text = cue.line;
              _messageController.text = cue.message;
              context.read<CueEditorBloc>().add(LoadCue(cue));
            }
        },
        child: BlocBuilder<CueEditorBloc, CueEditorState>(
          // Rebuild bloc on local bloc updates
          builder: (context, state) {
            if (state is CueEditorSuccess) {
            return  Container(
            color: Theme.of(context).colorScheme.surface,
            child: Form(
              key: _formKey,
              child: Stack(
                children: [
                  Positioned(
                    top: 8,
                    right: 8,
                    child: IconButton(
                      iconSize: 20,
                      icon: Icon(Icons.close, color: Theme.of(context).colorScheme.onSurface),
                      onPressed: () {
                        context.read<ScriptManagerBloc>().add(EditorChanged(EditorPanel.none));
                      },
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.all(24),
                    child: IntrinsicHeight(
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(
                            flex: 3,
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: <Widget>[
                                Column(
                                  children: List<Widget>.generate(_tagControllers.length, (index) {
                                    return Column(
                                      children: <Widget>[
                                        _buildTagWidget(_tagControllers[index]),
                                        if (index != _tagControllers.length - 1) SizedBox(height: 12),  // Conditional spacing
                                      ],
                                    );
                                  }),
                                ),
                                IconButton(
                                  // iconSize: 20,
                                  icon: Icon(Icons.add, color: Theme.of(context).colorScheme.onSurface),
                                  onPressed: () => _addNewTag(context),
                                ),
                                // TextFormField(
                                //   controller: _noteController,
                                //   // decoration: InputDecoration(labelText: 'Note'),
                                //   // onChanged: (value) => _updateCue(),
                                // ),
                              ],
                            ),
                          ),
                          // SizedBox(width: 8),
                          VerticalDivider(
                            width: 24,
                          ),
                          Expanded(
                            flex: 1,
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: <Widget>[
                                CustomFormField(
                                  label: "Title",
                                  field: "title",
                                  controller: _titleController,
                                ),
                                SizedBox(height: 8),
                                CustomFormField(
                                  label: "Note",
                                  field: "note",
                                  controller: _noteController,
                                ),
                              ],
                            ),
                          ),
                          VerticalDivider(
                            width: 24,
                          ),
                          Expanded(
                            flex: 1,
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: <Widget>[
                                Text(
                                  "Autofire",
                                  style: Theme.of(context).textTheme.titleSmall?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant),
                                  textAlign: TextAlign.left,
                                  ),
                                SizedBox(height: 12),
                                Switch(
                                  value: _autofire,
                                  onChanged: (bool value) {
                                    setState(() {
                                      _autofire = value;
                                    });
                                    _updateCue();
                                  },
                                ),
                                SizedBox(height: 16),
                                CustomFormField(
                                  label: "Line",
                                  field: "line",
                                  controller: _lineController,
                                ),
                                SizedBox(height: 8),
                                CustomFormField(
                                  label: "Message",
                                  field: "message",
                                  controller: _messageController,
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ]
              ),
            ));
            } else if (state is CueEditorLoading) {
              return Center(child: CircularProgressIndicator());
            } else {
              return Center(child: Text('Something went wrong'));
            }
          }
          ),
        ),
      );
    // );
  }

  void _buildTagControllers(List<Tag> tags) {
    _tagControllers = tags.map((tag) {
      return TagController(
        department: tag.id,
        cue: tag.cue_name,
        description: tag.description,
      );
    }).toList();
  }

  void _updateCue() {
    // if (_formKey.currentState!.validate()) {
    //   // Assuming a Cue instance can be updated
    //   final updatedCue = Cue(
    //     // dummy values for missing params, replace with actual
    //     1, Offset.zero, CueType(), [], 
    //     note: _noteController.text, 
    //     description: _descriptionController.text
    //   );
    //   context.read<CueBloc>().add(UpdateCue(updatedCue));
    // }
  }

void _addNewTag(BuildContext context) {
  setState(() {
    _tagControllers.add(TagController());
  });
}

void _removeTag(TagController tagController) {
  setState(() {
      _tagControllers.removeWhere((controller) => controller == tagController);
    });
  // context.read<CueEditorBloc>().add(RemoveTag(index));
}

void _updateTagInBloc(int index, String name, String description) {
  Tag updatedTag = Tag(name, TagType('Department', Colors.blue), description: description);
  context.read<CueEditorBloc>().add(UpdateTag(index, updatedTag));
}

Widget _buildTagWidget(TagController tagController) {
  return Row(
    children: [
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Department",
              style: Theme.of(context).textTheme.titleSmall?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant),
              textAlign: TextAlign.left,
            ),
            SizedBox(height: 12),
            Wrap(
              spacing: 8.0,
              children: tagOptions.map((tag) {
                return ChoiceChip(
                  label: Text(tag.department),
                  labelStyle: TextStyle(color: Colors.white),
                  selectedColor: tag.color,
                  backgroundColor: tag.color.withOpacity(0.3),
                  selected: tagController.department == tag.id,
                  onSelected: (bool selected) {
                    setState(() {
                      tagController.department = selected ? tag.id : null;
                    });
                  },
                );
              }).toList(),
            ),
            SizedBox(height: 12),
          ],
        ),
      ),
      SizedBox(width: 8),
      Expanded(child: CustomFormField(
        label: "Cue",
        field: "cue",
        controller: tagController.cueController,
      )),
      SizedBox(width: 8),
      Expanded(child: CustomFormField(
        label: "Description",
        field: "description",
        controller: tagController.descriptionController,
      )),
      SizedBox(height: 10),
      Container(
        padding: EdgeInsets.only(top:14),
        alignment: Alignment.centerRight, // Aligns the IconButton to the right and center vertically
        child: IconButton(
          icon: Icon(Icons.delete, color: Theme.of(context).colorScheme.onSurface),
          onPressed: () => _removeTag(tagController),
        ),
      ),
    ],
  );
}

}

class CustomFormField extends StatelessWidget {
  final String label;
  final String field;
  final TextEditingController controller;
  
  CustomFormField({
    required this.label,
    required this.field,
    required this.controller,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.titleSmall?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant),
        ),
        SizedBox(height: 4),
        TextField(
          controller: controller,
          onChanged: (value) {
            context.read<CueEditorBloc>().add(CueFieldUpdated(field, value));
          },
          decoration: InputDecoration(
            border: OutlineInputBorder(),
          ),
        ),
      ],
    );
  }
}

