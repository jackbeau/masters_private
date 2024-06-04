import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:stage_assistant/features/script_editor/data/interfaces/performer_tracker_provider_base.dart';
import 'package:stage_assistant/features/script_editor/data/providers/annotations_provider.dart';
import 'package:stage_assistant/features/script_editor/data/providers/speech_provider.dart';
import 'package:stage_assistant/features/script_editor/data/repositories/speech_repository.dart';
import 'package:stage_assistant/features/script_editor/data/providers/performer_tracker_provider.dart';
import 'package:stage_assistant/features/script_editor/data/repositories/performer_tracker_repository.dart';
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
  late final SpeechProvider _speechProvider;
  late final SpeechRepository _speechRepository;
  late final PerformerTrackerProvider _performerTrackerProvider;
  late final PerformerTrackerRepository _performerTrackerRepository;
  late final Future<void> _initialization;

  @override
  void initState() {
    super.initState();
    _annotationsProvider = AnnotationsProvider();
    _annotationsRepository = AnnotationsRepository(_annotationsProvider);
    _mqttService = MqttService();
    _mqttRepository = MqttRepository(_mqttService);
    _speechProvider = SpeechProvider(baseUrl: 'http://localhost:4000');
    _speechRepository = SpeechRepository(speechProvider: _speechProvider);
    _performerTrackerProvider = PerformerTrackerProvider(baseUrl: 'http://localhost:4000');
    _performerTrackerRepository = PerformerTrackerRepository(performerTrackerProvider: _performerTrackerProvider);

    // Initialize annotationsRepository
    _initialization = _annotationsRepository.initialize();
  }

  @override
  void dispose() {
    _annotationsRepository.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder(
      future: _initialization,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.done) {
          return MultiRepositoryProvider(
            providers: [
              RepositoryProvider.value(value: _annotationsRepository),
              RepositoryProvider.value(value: _mqttRepository),
              RepositoryProvider.value(value: _speechRepository),
              RepositoryProvider.value(value: _performerTrackerRepository),
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
        } else {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
      },
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
                  const Sidebar(),
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
            if (state.selectedEditor == EditorPanel.addCue)
              CueEditor(annotationsRepository: _annotationsRepository),
          ],
        );
      },
    );
  }
}
