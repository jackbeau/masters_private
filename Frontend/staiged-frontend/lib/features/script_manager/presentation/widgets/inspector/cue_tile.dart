import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import '../../../domain/cue.dart'; // Update this path to wherever your Cue model is defined

class CuePainter extends CustomPainter {
  final Cue cue;

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

class CueTile extends StatelessWidget {
  final Cue cue;

  CueTile({required this.cue});

  @override
  Widget build(BuildContext context) {
    Size cueSize = cue.calculateSize() * 1.1; // Get the calculated size of the cue

    return Card(
      color: Theme.of(context).colorScheme.surfaceVariant,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(5.0),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(5.0),
        onTap: () {
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
                              cue.page,
                              Offset(cueSize.width / (2 / 0.9),
                                  cueSize.height / (2 / 0.9)),
                              cue.type,
                              cue.tags,
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
                        print("Cue ID: ${cue.id}");
                      },
                    ),
                    IconButton(
                      iconSize: 20,
                      icon: Icon(Icons.more_horiz, color: Theme.of(context).colorScheme.onSurface),
                      onPressed: () {
                        // Implement dropdown menu for delete, etc.
                      },
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
                  Text(
                    cue.note,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Theme.of(context).colorScheme.onSurface),
                  ),
                  if (cue.description != "")
                    Padding(
                      padding: const EdgeInsets.only(top: 2),
                      child: Text(
                        cue.description,
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
}
