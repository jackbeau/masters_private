import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';  
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../domain/bloc/app_bar_bloc.dart';

class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  @override
  final Size preferredSize = Size.fromHeight(56.0);

  final int segmentedControlValue;
  final Function(int) onSegmentChanged;

  CustomAppBar({
    Key? key,
    required this.segmentedControlValue,
    required this.onSegmentChanged,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    AppBarBloc appBarBloc = BlocProvider.of<AppBarBloc>(context); // Get the AppBarBloc

    return AppBar(
      backgroundColor: Colors.black,
      leading: IconButton(
        icon: Icon(Icons.menu, color: Colors.white),
        onPressed: () {
          // Logic to handle menu opening
        },
      ),
      title: Text('PDF Viewer Example', style: TextStyle(color: Colors.white)),
      actions: <Widget>[
        IconButton(
          icon: Icon(Icons.zoom_in, color: Colors.white),
          onPressed: () => appBarBloc.add(ZoomIn()),
        ),
        IconButton(
          icon: Icon(Icons.zoom_out, color: Colors.white),
          onPressed: () => appBarBloc.add(ZoomOut()),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8),
          child: CupertinoSegmentedControl<int>(
            children: {
              0: Padding(padding: EdgeInsets.symmetric(horizontal: 8), child: Text("A", style: TextStyle(color: Colors.white))),
              1: Padding(padding: EdgeInsets.symmetric(horizontal: 8), child: Text("B", style: TextStyle(color: Colors.white))),
              2: Padding(padding: EdgeInsets.symmetric(horizontal: 8), child: Text("C", style: TextStyle(color: Colors.white))),
            },
            onValueChanged: onSegmentChanged,
            groupValue: segmentedControlValue,
            unselectedColor: Colors.black,
            selectedColor: Colors.red,
            borderColor: Colors.red,
          ),
        ),
        IconButton(
          icon: Icon(Icons.first_page, color: Colors.white),
          onPressed: () {
            appBarBloc.add(GoToPage(1));
          },
        ),
        IconButton(
          icon: Icon(Icons.last_page, color: Colors.white),
          onPressed: () {
            var pages = appBarBloc.state.controller.pages.length; // Example of accessing pages count
            appBarBloc.add(GoToPage(pages));
          },
        ),
      ],
    );
  }
}
