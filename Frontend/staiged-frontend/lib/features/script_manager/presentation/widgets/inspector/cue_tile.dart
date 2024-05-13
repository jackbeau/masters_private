import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import '../../../domain/cue.dart'; // Update this path to wherever your Cue model is defined

class CuePainter extends CustomPainter {
  final Cue cue;

  CuePainter(this.cue);

  @override
  void paint(Canvas canvas, Size size) {
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
    Size cueSize = cue.calculateSize(); // Get the calculated size of the cue
    print(cueSize);

    return Card(
      color: Theme.of(context).colorScheme.surfaceVariant,
      // margin: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8.0),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(8.0),
        onTap: () {
          // Add functionality for tap if needed
        },
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      SizedBox(
                          height: cueSize.height,
                          child: Container(
                              decoration: BoxDecoration(
                                color: Theme.of(context).colorScheme.secondary,
                                borderRadius: BorderRadius.circular(2.0),
                              ),
                              padding: const EdgeInsets.symmetric(horizontal: 4),
                              child: Text('FS',
                                  style: Theme.of(context)
                                      .textTheme
                                      .labelMedium
                                      ?.copyWith(
                                          color: Theme.of(context)
                                              .colorScheme
                                              .onSecondary)))
                          // height: 20,
                          // child: Chip(
                          //   label: const Text('Act 1 Scene 3'),
                          //   labelStyle: Theme.of(context).textTheme.labelSmall?.copyWith(color: Theme.of(context).colorScheme.onSecondary),
                          //
                          //   labelPadding: const EdgeInsets.all(0),
                          //   // padding: const EdgeInsets.all(0),
                          //   visualDensity: const VisualDensity(horizontal: 0.0, vertical: -4),
                          //   // materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                          // ),
                          ),
                      SizedBox(width: 8),
                      Container(
                        color: Colors.red,
                        child: CustomPaint(
                          size:
                              cueSize, // Use the size calculated by the Cue object
                          painter: CuePainter(Cue(
                            cue.page,
                            Offset(cueSize.width / 2, cueSize.height / 2),
                            cue.type,
                            cue.tags,
                          )),
                        ),
                      ),
                    ],
                  ),
                  // Placeholder for label; adjust as needed
                  IconButton(
                    icon: Icon(Icons.more_vert, color: Colors.white),
                    onPressed: () {
                      // Implement dropdown menu for delete, etc.
                    },
                  ),
                  IconButton(
                    icon: Icon(Icons.zoom_out_map, color: Colors.white),
                    onPressed: () {
                      print("Cue ID: ${cue.id}");
                    },
                  ),
                ],
              ),
            ),
            SizedBox(height: 8),
            Text("Cue: ${cue.type.text}",
                style: TextStyle(
                    color: Colors.white, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
}
