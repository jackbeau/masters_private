/*
 * Author: Jack Beaumont
 * Date: 06/06/2024
 * 
 * This file contains the InspectorCues widget, which displays a list of cues 
 * fetched by the InspectorCuesBloc from the AnnotationsRepository.
 */

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../domain/bloc/inspector_cues_bloc.dart';
import 'cue_tile.dart';
import '../../../data/repositories/annotations_repository.dart';

class InspectorCues extends StatelessWidget {
  const InspectorCues({super.key});

  /// Builds the InspectorCues widget.
  ///
  /// The widget is wrapped in a BlocProvider that initializes the InspectorCuesBloc
  /// with the AnnotationsRepository. It uses a BlocBuilder to build the UI based on
  /// the current state of the InspectorCuesBloc.
  ///
  /// If the state is InspectorCuesLoaded, it displays a list of cues.
  /// Otherwise, it shows a CircularProgressIndicator.
  ///
  /// Parameters:
  /// - context: BuildContext for the widget.
  ///
  /// Returns:
  /// - A widget tree that displays the cues or a loading indicator.
  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => InspectorCuesBloc(
        RepositoryProvider.of<AnnotationsRepository>(context),
      )..add(LoadCues()),
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
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      color: Theme.of(context).colorScheme.onBackground,
                    ),
                  ),
                  const SizedBox(height: 8),
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
            return const Center(child: CircularProgressIndicator());
          }
        },
      ),
    );
  }
}
