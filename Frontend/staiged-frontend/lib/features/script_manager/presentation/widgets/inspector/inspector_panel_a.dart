import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../domain/bloc/inspecor_panel_a.dart';
import '../../../data/models/cue.dart';
import 'cue_tile.dart';

class InspectorPanelA extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => InspectorPanelABloc()..add(LoadCues()),
      child: BlocBuilder<InspectorPanelABloc, InspectorPanelAState>(
        builder: (context, state) {
          if (state is InspectorPanelALoaded) {
            return Container(
              color: Colors.black,
              child: ListView.builder(
                itemCount: state.cues.length,
                itemBuilder: (context, index) {
                  return CueTile(cue: state.cues[index]);
                },
              ),
            );
          } else {
            return CircularProgressIndicator(); // Show loading indicator
          }
        },
      ),
    );
  }
}
