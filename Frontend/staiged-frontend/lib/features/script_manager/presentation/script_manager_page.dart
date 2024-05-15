import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../domain/bloc/script_manager_bloc.dart';
import '../domain/bloc/app_bar_bloc.dart';
import 'widgets/script_canvas.dart';
import 'widgets/inspector/inspector.dart';
import 'widgets/sidebar.dart';
import 'widgets/custom_toolbar/custom_toolbar.dart';
import 'widgets/camera_widget.dart';
import 'widgets/editor/cue_editor.dart';

class ScriptManagerPage extends StatefulWidget {
  const ScriptManagerPage({Key? key}) : super(key: key);

  @override
  _ScriptManagerPageState createState() => _ScriptManagerPageState();
}

class _ScriptManagerPageState extends State<ScriptManagerPage> {
  late ScriptManagerBloc _scriptManagerBloc;

  @override
  void initState() {
    super.initState();
    _scriptManagerBloc = ScriptManagerBloc()..add(LoadPdf());
  }

  @override
  void dispose() {
    _scriptManagerBloc.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return BlocProvider<ScriptManagerBloc>(
      create: (_) => _scriptManagerBloc,
      child: BlocBuilder<ScriptManagerBloc, ScriptManagerState>(
        builder: (context, state) {
          if (state is ScriptManagerLoaded && state.pdfController != null) {
            return Scaffold(
              appBar: PreferredSize(
                preferredSize: const Size.fromHeight(60.0),
                child: CustomToolbar(
                  scriptManagerBloc: _scriptManagerBloc,
                  currentMode: state.mode,
                  selectedInspector: state.selectedInspector,
                  isCameraActive: state.isCameraVisible,
                  selectedTool: state.selectedTool,
                ),
              ),
              body: buildBody(context, state),
            );
          } else {
            return Scaffold(
              body: Center(child: CircularProgressIndicator()),
            );
          }
        },
      ),
    );
  }

  Widget buildBody(BuildContext context, ScriptManagerLoaded state) {
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
                  Container(
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
              CueEditor(),
          ],
        );
      },
    );
  }
}
