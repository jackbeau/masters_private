// Author: Jack Beaumont
// Date: 06/06/2024

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../domain/models/cue.dart'; // Update this path to wherever your Cue model is defined
import '../../../domain/bloc/script_editor_bloc.dart';
import '../../../domain/bloc/inspector_cues_bloc.dart';
import 'package:logging/logging.dart';

// Initialize logging
final Logger _logger = Logger('CueTile');

/// A custom painter for drawing a Cue object on a Canvas.
class CuePainter extends CustomPainter {
  final Cue cue;

  /// Constructs a [CuePainter] with a given [Cue].
  CuePainter(this.cue);

  @override
  void paint(Canvas canvas, Size size) {
    canvas.scale(1.1);
    cue.draw(canvas);
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) {
    return false;
  }
}

/// A widget representing a tile for a [Cue] object.
class CueTile extends StatelessWidget {
  final Cue cue;

  /// Constructs a [CueTile] with a given [Cue].
  const CueTile({super.key, required this.cue});

  @override
  Widget build(BuildContext context) {
    Size cueSize = cue.calculateSize() * 1.1; // Get the calculated size of the cue

    return Card(
      margin: EdgeInsets.zero,
      color: Theme.of(context).colorScheme.surfaceVariant,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(5.0),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(5.0),
        onTap: () {
          _logger.info('CueTile tapped');
          // Add functionality for tap if needed
        },
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start, // Align items to the top
              children: [
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(12, 12, 0, 0),
                    child: Wrap(
                      alignment: WrapAlignment.start,
                      spacing: 8, // Horizontal space between children
                      runSpacing: 4, // Vertical space between lines
                      children: [
                        CustomPaint(
                          size: cueSize, // Use the size calculated by the Cue object
                          painter: CuePainter(Cue(
                            page: cue.page,
                            pos: Offset(cueSize.width / (2 / 0.9),
                                cueSize.height / (2 / 0.9)),
                            type: cue.type,
                            tags: cue.tags,
                          )),
                        ),
                        SizedBox(
                          height: cueSize.height,
                          child: Container(
                            decoration: BoxDecoration(
                              color: Theme.of(context).colorScheme.secondary,
                              borderRadius: BorderRadius.circular(2.0),
                            ),
                            padding: const EdgeInsets.symmetric(horizontal: 4),
                            child: Baseline(
                              baselineType: TextBaseline.alphabetic,
                              baseline: 13,
                              child: Text(
                                'Act I Scene 2',
                                style: Cue.labelStyle.copyWith(
                                    color: Theme.of(context).colorScheme.onSecondary),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                Row( // Vertically align the icons without affecting Wrap
                  children: [
                    IconButton(
                      iconSize: 20,
                      icon: Icon(Icons.edit, color: Theme.of(context).colorScheme.onSurface),
                      onPressed: () {
                        _logger.info('Edit button pressed for cue: ${cue.title}');
                        context.read<ScriptEditorBloc>().add(UpdateSelectedAnnotationEvent(cue));
                        context.read<ScriptEditorBloc>().add(EditorChanged(EditorPanel.addCue));
                      },
                    ),
                    PopupMenuButton<String>(
                      onSelected: (value) {
                        if (value == 'Delete') {
                          _logger.info('Delete option selected for cue: ${cue.title}');
                          _deleteCue(context, cue);
                        }
                      },
                      itemBuilder: (BuildContext context) {
                        return <PopupMenuEntry<String>>[
                          const PopupMenuItem<String>(
                            value: 'Delete',
                            child: Text('Delete'),
                          ),
                        ];
                      },
                      icon: Icon(Icons.more_horiz, color: Theme.of(context).colorScheme.onSurface),
                      offset: const Offset(0, 0),  // This offset moves the menu down by 40 pixels relative to the IconButton
                      position: PopupMenuPosition.under, // Ensures the menu opens below the anchor
                    ),
                  ],
                ),
              ],
            ),
            // Additional text and padding here, if needed
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (cue.title != "")
                    Text(
                      cue.title,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Theme.of(context).colorScheme.onSurface),
                    ),
                  if (cue.note != "")
                    Padding(
                      padding: const EdgeInsets.only(top: 2),
                      child: Text(
                        cue.note,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant),
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Deletes the given [Cue] and updates the state accordingly.
  ///
  /// This method reads the [InspectorCuesBloc] and [ScriptEditorBloc] from the [BuildContext]
  /// to dispatch the appropriate events to delete the cue and update the selected annotation.
  void _deleteCue(BuildContext context, Cue cue) {
    _logger.info('Deleting cue: ${cue.title}');
    context.read<InspectorCuesBloc>().add(DeleteAnnotationEvent(cue));
    context.read<ScriptEditorBloc>().add(UpdateSelectedAnnotationEvent(null));
  }
}
