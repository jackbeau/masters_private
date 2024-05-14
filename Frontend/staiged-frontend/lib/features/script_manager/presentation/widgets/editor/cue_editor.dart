import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:staiged/features/script_manager/data/models/annotation.dart';
import 'package:staiged/features/script_manager/domain/cue.dart';
import '../../../domain/bloc/script_manager_bloc.dart';
import '../../../domain/bloc/cue_editor_bloc.dart';

// import 'package:your_project_path/bloc/cue_bloc.dart';
// import '../data/models/cue.dart';

class CueEditor extends StatefulWidget {
  @override
  _CueEditorState createState() => _CueEditorState();
}

class _CueEditorState extends State<CueEditor> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _cueController;
  late TextEditingController _descriptionController;
  late TextEditingController _noteController;
  late TextEditingController _titleController;
  late TextEditingController _lineController;
  late TextEditingController _messageController;
  bool _autofire = false;
  String? _selectedDepartment;


  final List<Map<String, dynamic>> _departments = [
    {'name': 'HR', 'color': Colors.red},
    {'name': 'Finance', 'color': Colors.green},
    {'name': 'IT', 'color': Colors.blue},
    {'name': 'Marketing', 'color': Colors.orange},
  ];

  @override
  void initState() {
    super.initState();
    _cueController = TextEditingController();
    _descriptionController = TextEditingController();
    _noteController = TextEditingController();
    _titleController = TextEditingController();
    _lineController = TextEditingController();
    _messageController = TextEditingController();
  }

  @override
  void dispose() {
    _cueController.dispose();
    _descriptionController.dispose();
    _noteController.dispose();
    _titleController.dispose();
    _lineController.dispose();
    _messageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
      return BlocProvider<CueEditorBloc>(
        create: (_) => CueEditorBloc(),
        child: BlocListener<ScriptManagerBloc, ScriptManagerState>(
          listener: (context, state) {
            if (state.selectedAnnotation is Cue) {
              var cue = state.selectedAnnotation as Cue;
            _noteController.text = cue.note ?? '';
            // _descriptionController.text = cue.description ?? '';
            _titleController.text = cue.title ?? '';
            _lineController.text = cue.line ?? '';
            _messageController.text = cue.message ?? '';
            _autofire = cue.autofire;
            context.read<CueEditorBloc>().add(LoadCue(cue));
            }
            print(state.selectedAnnotation);
          },
          child: Container(
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
                        print("Close");
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
                                Row(
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
                                            children: _departments.map((department) {
                                              return ChoiceChip(
                                                label: Text(department['name']),
                                                labelStyle: TextStyle(color: Colors.white),
                                                selectedColor: department['color'],
                                                backgroundColor: department['color'].withOpacity(0.3),
                                                selected: _selectedDepartment == department['name'],
                                                onSelected: (bool selected) {
                                                  setState(() {
                                                    _selectedDepartment = selected ? department['name'] : null;
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
                                      controller: _cueController,
                                    )),
                                    SizedBox(width: 8),
                                    Expanded(child: CustomFormField(
                                      label: "Description",
                                      field: "description",
                                      controller: _descriptionController,
                                    )),
                                  ],
                                ),
                                IconButton(
                                  // iconSize: 20,
                                  icon: Icon(Icons.add, color: Theme.of(context).colorScheme.onSurface),
                                  onPressed: () {
                                    print("Add");
                                  },
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
            ),
          ),
        ),
      );
    // );
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
