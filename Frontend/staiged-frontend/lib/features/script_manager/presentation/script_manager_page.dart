import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../domain/bloc/script_manager_bloc.dart';
import '../domain/bloc/app_bar_bloc.dart';
import 'widgets/script_canvas.dart';
import 'widgets/inspector/inspector.dart';
import 'widgets/sidebar.dart';
import 'widgets/custom_toolbar/custom_toolbar.dart';
import 'widgets/camera_widget.dart';

class ScriptManagerPage extends StatelessWidget {
  const ScriptManagerPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider<ScriptManagerBloc>(
      create: (_) => ScriptManagerBloc()..add(LoadPdf()),
      child: BlocBuilder<ScriptManagerBloc, ScriptManagerState>(
        builder: (context, state) {
          if (state is ScriptManagerLoaded && state.pdfController != null) {
            // Ensuring the controller is not null before providing it
            return BlocProvider<AppBarBloc>(
              create: (context) => AppBarBloc(state.pdfController!),
              child: BlocConsumer<ScriptManagerBloc, ScriptManagerState>(
                listener: (context, state) {
                  if (state is ScriptManagerLoaded && state.pdfController != null) {
                    context.read<AppBarBloc>().add(InitializeAppBar(state.pdfController!));
                  }
                },
                builder: (context, state) {
                  if (state is ScriptManagerLoaded) {
                    return Scaffold(
                      appBar: PreferredSize(
                        preferredSize: const Size.fromHeight(60.0), // Set the height for the toolbar
                        child: CustomToolbar(
                          appBarBloc: BlocProvider.of<AppBarBloc>(context),
                          scriptManagerBloc: BlocProvider.of<ScriptManagerBloc>(context),
                          currentMode: state.mode,
                          selectedInspector: state.selectedInspector,
                          isCameraActive: state.isCameraVisible,
                          selectedTool: state.selectedTool
                        ),
                      ),
                      body: buildBody(context, state)
                    );
                  } else {
                    return Scaffold(
                      body: Center(child: CircularProgressIndicator()),
                    );
                  }
                },
              ),
            );
          } else {
            // Return a loading or error state when the controller or necessary state is not loaded
            return Scaffold(
              body: Center(child: CircularProgressIndicator()),
            );
          }
        },
      ),
    );
  }
}


Widget buildBody(BuildContext context, ScriptManagerLoaded state) {
  return LayoutBuilder( // This LayoutBuilder will ensure you have constraints to work with
    builder: (context, constraints) {
      return Row(
        children: [
          Sidebar(),
          Expanded( // Ensures that this takes up the remaining space proportionally
            flex: 4,
            child: ScriptCanvas(
                  controller: state.pdfController!,
            ),
          ),
          Container( // Use Container to set explicit width when needed
            width: (constraints.maxWidth / 6).clamp(294, 400),
            child: Column(
              children: [
                if (state.isCameraVisible)
                  LayoutBuilder(
                    builder: (context, camConstraints) => CameraWidget(width: camConstraints.maxWidth),
                  ),
                Expanded(
                  child: Inspector(selectedInspector: state.selectedInspector)
                ),
              ],
            ),
          ),
        ],
      );
    }
  );
}