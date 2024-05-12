import 'package:flutter/material.dart';
import '../../../data/models/cue_TEMP.dart'; // Ensure this import path matches the location of your Cue model

class CueTile extends StatelessWidget {
  final Cue cue;

  CueTile({required this.cue});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.grey[850],
      child: ExpansionTile(
        leading: CircleAvatar(
          backgroundColor: Colors.red[800],
          child: Text(cue.id.split(' ').first, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
        ),
        title: Text(cue.title, style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        subtitle: Text(cue.actScene, style: TextStyle(color: Colors.grey[500])),
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(cue.description, style: TextStyle(color: Colors.white70, fontSize: 16)),
                SizedBox(height: 10),
                ElevatedButton(
                  onPressed: () {
                    // Placeholder for an action - this could be linked to playing the cue or other interactions
                    print("Cue action triggered for: ${cue.title}");
                  },
                  // style: ElevatedButton.styleFrom(
                  //   primary: Colors.blueAccent, // Background color
                  // ),
                  child: Text('GO'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
