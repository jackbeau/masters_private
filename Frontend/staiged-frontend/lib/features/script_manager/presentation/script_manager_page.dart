import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../domain/bloc/script_manager_bloc.dart';
import '../domain/bloc/app_bar_bloc.dart';
import 'widgets/script_canvas.dart';
import 'widgets/inspector/inspector.dart';
import 'widgets/sidebar.dart';
import 'widgets/custom_app_bar/custom_app_bar.dart';

class ScriptManagerPage extends StatelessWidget {
  ScriptManagerPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider<ScriptManagerBloc>(
      create: (_) => ScriptManagerBloc()..add(LoadPdf()),
      child: BlocBuilder<ScriptManagerBloc, ScriptManagerState>(
        builder: (context, state) {
          // Provide AppBarBloc here at a higher level with the correct controller
          return state is ScriptManagerLoaded ? BlocProvider<AppBarBloc>(
            create: (context) => AppBarBloc(state.pdfController),
            child: BlocConsumer<ScriptManagerBloc, ScriptManagerState>(
              listener: (context, state) {
                if (state is ScriptManagerLoaded) {
                  context.read<AppBarBloc>().add(InitializeAppBar(state.pdfController));
                }
              },
              builder: (context, state) {
                if (state is ScriptManagerLoaded) {
                  return Scaffold(
                    appBar: CustomAppBar(
                    segmentedControlValue: state.segmentedControlValue,
                    onSegmentChanged: (value) {
                    // Do something with the new segment value
                    },
                  appBarBloc: BlocProvider.of<AppBarBloc>(context),
            ),
                    body: Row(
                      children: [
                        Sidebar(),
                        Expanded(
                          flex: 4,
                          child: ScriptCanvas(controller: state.pdfController),
                        ),
                        Expanded(
                          flex: 1,
                          child: Inspector(selectedPanel: state.segmentedControlValue),
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
          ) : Scaffold(
            body: Center(child: Text("Waiting for PDF loading")),
          );
        },
      ),
    );
  }
}