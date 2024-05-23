import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:staiged/features/script_editor/data/providers/annotations_provider.dart';
import '../../data/repositories/annotations_repository.dart';
import '../../data/providers/mqtt_service.dart';
import '../../data/repositories/mqtt_repository.dart';
import '../../domain/bloc/script_editor_bloc.dart';
import '../widgets/script_canvas.dart';
import '../widgets/inspector/inspector.dart';
import '../widgets/sidebar.dart';
import '../widgets/custom_toolbar/custom_toolbar.dart';
import '../widgets/camera_widget.dart';
import '../widgets/editor/cue_editor.dart';

class ScriptEditorPage extends StatefulWidget {
  const ScriptEditorPage({super.key});

  @override
  State<ScriptEditorPage> createState() => _ScriptEditorPageState();
}

class _ScriptEditorPageState extends State<ScriptEditorPage> {
  late final AnnotationsProvider _annotationsProvider;
  late final AnnotationsRepository _annotationsRepository;
  late final MqttService _mqttService;
  late final MqttRepository _mqttRepository;

  @override
  void initState() {
    super.initState();
    _annotationsProvider = AnnotationsProvider();
    _annotationsRepository = AnnotationsRepository(_annotationsProvider);
    _mqttService = MqttService();
    _mqttRepository = MqttRepository(_mqttService);
  }

  @override
  void dispose() {
    // _annotationsRepository.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MultiRepositoryProvider(
      providers: [
        RepositoryProvider.value(value: _annotationsRepository),
        RepositoryProvider.value(value: _mqttRepository),
      ],
      child: BlocProvider(
        create: (context) {
          return ScriptEditorBloc()..add(LoadPdf());
        },
        child: BlocBuilder<ScriptEditorBloc, ScriptEditorState>(
          builder: (context, state) {
            if (state is ScriptEditorLoaded && state.pdfController != null) {
              return Scaffold(
                appBar: const PreferredSize(
                  preferredSize: Size.fromHeight(60.0),
                  child: CustomToolbar(),
                ),
                body: buildBody(context, state),
              );
            } else {
              return const Scaffold(
                body: Center(child: CircularProgressIndicator()),
              );
            }
          },
        ),
      ),
    );
  }

  Widget buildBody(BuildContext context, ScriptEditorLoaded state) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return Column(
          children: [
            Expanded(
              child: Row(
                children: [
                  Sidebar(),
                  Expanded(
                    flex: 4,
                    child: ScriptCanvas(
                      controller: state.pdfController!,
                    ),
                  ),
                  SizedBox(
                    width: (constraints.maxWidth / 6).clamp(294, 400),
                    child: Column(
                      children: [
                        if (state.isCameraVisible)
                          LayoutBuilder(
                            builder: (context, camConstraints) => CameraWidget(width: camConstraints.maxWidth),
                          ),
                        Expanded(
                          child: Inspector(selectedInspector: state.selectedInspector),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            if (state.selectedEditor == EditorPanel.add_cue)
              CueEditor(annotationsRepository: _annotationsRepository),
          ],
        );
      },
    );
  }
}
