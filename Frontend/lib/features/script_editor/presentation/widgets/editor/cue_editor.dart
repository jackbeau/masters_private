import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:stage_assistant/features/script_editor/domain/models/cue.dart';
import '../../../domain/bloc/script_editor_bloc.dart';
import '../../../domain/bloc/cue_editor_bloc.dart';
import '../../../domain/models/tag.dart';
import '../../../data/repositories/annotations_repository.dart';

class TagController {
  TextEditingController cueController;
  TextEditingController descriptionController;

  TagController({String? cue, String? description})
      : cueController = TextEditingController(text: cue),
        descriptionController = TextEditingController(text: description);
}

class CueEditor extends StatefulWidget {
  final AnnotationsRepository annotationsRepository;

  const CueEditor({super.key, required this.annotationsRepository});

  @override
  CueEditorWidgetState createState() => CueEditorWidgetState();
}

class CueEditorWidgetState extends State<CueEditor> {
  final _formKey = GlobalKey<FormState>();
  late Cue _selectedCue; // the cue that is selected according to the script manager
  late List<TagController> _tagControllers;
  late TextEditingController _noteController;
  late TextEditingController _titleController;
  late TextEditingController _lineController;
  late TextEditingController _messageController;

  @override
  void initState() {
    super.initState();
    _tagControllers = [];
    _noteController = TextEditingController();
    _titleController = TextEditingController();
    _lineController = TextEditingController();
    _messageController = TextEditingController();
  }

  @override
  void dispose() {
    for (var tagController in _tagControllers) {
      tagController.cueController.dispose();
      tagController.descriptionController.dispose();
    }
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
        final selectedAnnotation = context.read<ScriptEditorBloc>().state.selectedAnnotation;
        final cueEditorBloc = CueEditorBloc(widget.annotationsRepository);
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
      child: BlocListener<ScriptEditorBloc, ScriptEditorState>(
        listener: (context, state) {
          if (state.selectedAnnotation is Cue) {
            final effectiveCue = (state.selectedAnnotation as Cue);
            _selectedCue = effectiveCue;
            _buildTagControllers(effectiveCue.tags);
            _titleController.text = effectiveCue.title;
            _noteController.text = effectiveCue.note;
            _lineController.text = effectiveCue.line;
            _messageController.text = effectiveCue.message;
            context.read<CueEditorBloc>().add(LoadCue(effectiveCue));
          }
        },
        child: BlocBuilder<CueEditorBloc, CueEditorState>(
          builder: (context, state) {
            if (state is CueEditorSuccess && state.cue is Cue) {
              _selectedCue = state.cue!;
              return Container(
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
                            context.read<ScriptEditorBloc>().add(EditorChanged(EditorPanel.none));
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
                                            if (index != _tagControllers.length - 1) const SizedBox(height: 12),  // Conditional spacing
                                          ],
                                        );
                                      }),
                                    ),
                                    IconButton(
                                      icon: Icon(Icons.add, color: Theme.of(context).colorScheme.onSurface),
                                      onPressed: () => _addNewTag(context),
                                    ),
                                  ],
                                ),
                              ),
                              const VerticalDivider(width: 24),
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
                                    const SizedBox(height: 8),
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
                              const VerticalDivider(width: 24),
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
                                    const SizedBox(height: 12),
                                    Switch(
                                      value: _selectedCue.autofire,
                                      onChanged: (bool value) {
                                        context.read<CueEditorBloc>().add(CueFieldUpdated("autofire", value));
                                      },
                                    ),
                                    const SizedBox(height: 16),
                                    CustomFormField(
                                      label: "Line",
                                      controller: _lineController,
                                      onChanged: (value) {
                                        context.read<CueEditorBloc>().add(CueFieldUpdated("line", value));
                                      },
                                    ),
                                    const SizedBox(height: 8),
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
                    ],
                  ),
                ),
              );
            } else if (state is CueEditorLoading) {
              return const Center(child: CircularProgressIndicator());
            } else {
              return const Center(child: Text('Something went wrong'));
            }
          },
        ),
      ),
    );
  }

  void _buildTagControllers(List<Tag> tags) {
    _tagControllers = tags.map((tag) {
      return TagController(
        cue: tag.cueName,
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
  }

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
              const SizedBox(height: 12),
              Wrap(
                spacing: 8.0,
                children: tagOptions.map((tag) { // build all tags
                  return ChoiceChip(
                    label: Text(tag.department),
                    labelStyle: const TextStyle(color: Colors.white),
                    selectedColor: tag.color,
                    backgroundColor: tag.color.withOpacity(0.3),
                    selected: _selectedCue.tags[index].type!.id == tag.id,
                    onSelected: (bool selected) {
                      context.read<CueEditorBloc>().add(UpdateTagDetail(index, "department", tag));
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: 12),
            ],
          ),
        ),
        const SizedBox(width: 8),
        Expanded(child: CustomFormField(
          label: "Cue",
          controller: tagController.cueController,
          onChanged: (value) {
            context.read<CueEditorBloc>().add(UpdateTagDetail(index, "cue", value));
          },
        )),
        const SizedBox(width: 8),
        Expanded(child: CustomFormField(
          label: "Description",
          controller: tagController.descriptionController,
          onChanged: (value) {
            context.read<CueEditorBloc>().add(UpdateTagDetail(index, "description", value));
          },
        )),
        const SizedBox(height: 10),
        Container(
          padding: const EdgeInsets.only(top: 14),
          alignment: Alignment.centerRight,
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

  const CustomFormField({
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
        const SizedBox(height: 4),
        TextField(
          controller: controller,
          onChanged: onChanged,
          decoration: const InputDecoration(
            border: OutlineInputBorder(),
          ),
        ),
      ],
    );
  }
}
