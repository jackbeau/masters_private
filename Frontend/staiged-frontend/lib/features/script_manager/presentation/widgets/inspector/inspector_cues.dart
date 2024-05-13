import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../domain/bloc/inspector_cues_bloc.dart';
import '../../../domain/cue.dart'; // Update this path to wherever your Cue model is defined
import 'cue_tile.dart';

class InspectorCues extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => InspectorPanelABloc()..add(LoadCues()),
      child: BlocBuilder<InspectorPanelABloc, InspectorPanelAState>(
        builder: (context, state) {
          if (state is InspectorPanelALoaded) {
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 18, horizontal: 14),
              child: Container(
                color: Colors.black,
                child: ListView.separated(
                  itemCount: state.cues.length,
                  itemBuilder: (context, index) {
                    return CueTile(cue: state.cues[index]);
                  },
                  separatorBuilder: (context, index) => Divider(color: Colors.grey[800]),
                ),
              ),
            );
          } else {
            return Center(child: CircularProgressIndicator());
          }
        },
      ),
    );
  }
}
