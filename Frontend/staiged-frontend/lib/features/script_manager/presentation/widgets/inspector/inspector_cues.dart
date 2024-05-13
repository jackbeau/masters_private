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
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start, // Ensure alignment is to the start
                children: [
                  Text(
                    "All cues",
                    textAlign: TextAlign.left, // Align text to the left
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(color: Theme.of(context).colorScheme.onBackground)
                  ),

                  SizedBox(height: 8),
                  
                  Expanded(
                    child: Container(
                      color: Colors.black,
                      child: ListView.builder(
                        itemCount: state.cues.length,
                        itemBuilder: (context, index) {
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 4.0),
                            child: CueTile(cue: state.cues[index]),
                          );
                        },
                      ),
                    ),
                  ),
                ],
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
