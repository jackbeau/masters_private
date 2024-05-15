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
  TextEditingController cueController;
  TextEditingController descriptionController;

  TagController({String? cue, String? description})
      : cueController = TextEditingController(text: cue),
        descriptionController = TextEditingController(text: description);
}

class CueEditor extends StatefulWidget {
  @override
  _CueEditorState createState() => _CueEditorState();
}

class _CueEditorState extends State<CueEditor> {
  final _formKey = GlobalKey<FormState>();
  late Cue _selectedCue; // the cue that is selected according to the script manager
  late List<TagController> _tagControllers;
  late TextEditingController _noteController;
  late TextEditingController _titleController;
  late TextEditingController _lineController;
  late TextEditingController _messageController;


  @override
  void initState() {
    print("hi3");
    super.initState();
    _tagControllers = [];
    _noteController = TextEditingController();
    _titleController = TextEditingController();
    _lineController = TextEditingController();
    _messageController = TextEditingController();
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
        print("1");
        final selectedAnnotation = context.read<ScriptManagerBloc>().state.selectedAnnotation;
        final cueEditorBloc = CueEditorBloc();
        if (selectedAnnotation is Cue) {
          _selectedCue = selectedAnnotation;
          cueEditorBloc.add(LoadCue(selectedAnnotation));
          _buildTagControllers(selectedAnnotation.tags);
          _titleController.text = selectedAnnotation.title;
          _noteController.text = selectedAnnotation.note;
          _lineController.text = selectedAnnotation.line;
          _messageController.text = selectedAnnotation.message;

        }
        return cueEditorBloc;
      },
      child: BlocListener<ScriptManagerBloc, ScriptManagerState>(
        // Subscribe to subsequent updates
        listener: (context, state) {
          print("w");
            if (state.selectedAnnotation is Cue) {
              _selectedCue = state.selectedAnnotation as Cue;
              _buildTagControllers(_selectedCue.tags);
              _titleController.text = _selectedCue.title;
              _noteController.text = _selectedCue.note;
              _lineController.text = _selectedCue.line;
              _messageController.text = _selectedCue.message;
              context.read<CueEditorBloc>().add(LoadCue(_selectedCue));
            }
        },
        child: BlocBuilder<CueEditorBloc, CueEditorState>(
          // Rebuild bloc on local bloc updates
          builder: (context, state) {
            if (state is CueEditorSuccess && state.cue is Cue) {
              print("3");
              _selectedCue = state.cue!; // null check
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
                                        _buildTagWidget(context, _tagControllers[index], index),
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
                                  controller: _titleController,
                                  onChanged: (value) {
                                    context.read<CueEditorBloc>().add(CueFieldUpdated("title", value));
                                  },
                                ),
                                SizedBox(height: 8),
                                CustomFormField(
                                  label: "Note",
                                  controller: _noteController,
                                  onChanged: (value) {
                                    context.read<CueEditorBloc>().add(CueFieldUpdated("note", value));
                                  },
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
                                  value: _selectedCue.autofire,
                                  onChanged: (bool value) {
                                    print(value);
                                    context.read<CueEditorBloc>().add(CueFieldUpdated("autofire", value));
                                  },
                                ),
                                SizedBox(height: 16),
                                CustomFormField(
                                  label: "Line",
                                  controller: _lineController,
                                  onChanged: (value) {
                                    context.read<CueEditorBloc>().add(CueFieldUpdated("line", value));
                                  },
                                ),
                                SizedBox(height: 8),
                                CustomFormField(
                                  label: "Message",
                                  controller: _messageController,
                                  onChanged: (value) {
                                    context.read<CueEditorBloc>().add(CueFieldUpdated("message", value));
                                  },
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
  }

  void _buildTagControllers(List<Tag> tags) {
    _tagControllers = tags.map((tag) {
      return TagController(
        cue: tag.cue_name,
        description: tag.description,
      );
    }).toList();
  }

void _addNewTag(BuildContext context) {
  _tagControllers.add(TagController());
  context.read<CueEditorBloc>().add(AddTag(Tag()));
}

void _removeTag(BuildContext context, TagController tagController, int index) {
    _tagControllers.removeWhere((controller) => controller == tagController);
    context.read<CueEditorBloc>().add(RemoveTag(index));
  // context.read<CueEditorBloc>().add(RemoveTag(index));
}

// void _updateTagInBloc(int index, String name, String description) {
//   Tag updatedTag = Tag(name, TagType('Department', Colors.blue), description: description);
//   context.read<CueEditorBloc>().add(UpdateTag(index, updatedTag));
// }

Widget _buildTagWidget(BuildContext context, TagController tagController, int index) {
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
              children: tagOptions.map((tag) { // build all tags
                return ChoiceChip(
                  label: Text(tag.department),
                  labelStyle: TextStyle(color: Colors.white),
                  selectedColor: tag.color,
                  backgroundColor: tag.color.withOpacity(0.3),
                  selected: _selectedCue.tags[index].type == tag,
                  onSelected: (bool selected) {
                    print(tag.id);
                    context.read<CueEditorBloc>().add(UpdateTagDetail(index, "department", tag));
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
        controller: tagController.cueController,
        onChanged: (value) {
          // Dispatch an UpdateTagDetail event specifically for the cue field
          context.read<CueEditorBloc>().add(UpdateTagDetail(index, "cue", value));
        },
      )),
      SizedBox(width: 8),
      Expanded(child: CustomFormField(
        label: "Description",
        controller: tagController.descriptionController,
        onChanged: (value) {
          // Dispatch an UpdateTagDetail event specifically for the description field
          context.read<CueEditorBloc>().add(UpdateTagDetail(index, "description", value));
        },
      )),
      SizedBox(height: 10),
      Container(
        padding: EdgeInsets.only(top:14),
        alignment: Alignment.centerRight, // Aligns the IconButton to the right and center vertically
        child: IconButton(
          icon: Icon(Icons.delete, color: Theme.of(context).colorScheme.onSurface),
          onPressed: () => _removeTag(context, tagController, index),
        ),
      ),
    ],
  );
}

}


class CustomFormField extends StatelessWidget {
  final String label;
  final TextEditingController controller;
  final Function(String) onChanged;

  CustomFormField({
    required this.label,
    required this.controller,
    required this.onChanged,
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
          onChanged: onChanged, // Use the passed callback
          decoration: InputDecoration(
            border: OutlineInputBorder(),
          ),
        ),
      ],
    );
  }
}