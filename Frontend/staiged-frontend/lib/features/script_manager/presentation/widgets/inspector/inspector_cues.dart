import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../domain/bloc/inspector_cues_bloc.dart';
import '../../../domain/models/cue.dart'; // Update this path to wherever your Cue model is defined
import 'cue_tile.dart';
import '../../../data/repositories/annotations_repository.dart';

class InspectorCues extends StatelessWidget {

  InspectorCues();

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => InspectorCuesBloc(RepositoryProvider.of<AnnotationsRepository>(context))..add(LoadCues()),
      child: BlocBuilder<InspectorCuesBloc, InspectorCuesState>(
        builder: (context, state) {
          if (state is InspectorCuesLoaded) {
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 18, horizontal: 14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    "All cues",
                    textAlign: TextAlign.left,
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(color: Theme.of(context).colorScheme.onBackground)
                  ),
                  SizedBox(height: 8),
                  Expanded(
                    child: Container(
                      color: Theme.of(context).colorScheme.surface,
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
