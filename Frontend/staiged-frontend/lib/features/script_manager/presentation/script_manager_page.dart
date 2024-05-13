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
                        ),
                      ),
                      body: Row(
                        children: [
                          Sidebar(),
                          Expanded(
                            flex: 4,
                            child: ScriptCanvas(
                              controller: state.pdfController!
                            ),
                          ),
                          Expanded(
                                    flex: 1,
                                    child: Column(
                                      children: [
                                        if (state.isCameraVisible)
                                          LayoutBuilder(
                                            builder: (context, constraints) {
                                              return CameraWidget(width: constraints.maxWidth);
                                            }
                                          ),
                                        Expanded(
                                          child: Inspector(selectedInspector: state.selectedInspector)
                                        ),
                                      ],
                                    ),
                                  ),
                        ],
                      ),
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
