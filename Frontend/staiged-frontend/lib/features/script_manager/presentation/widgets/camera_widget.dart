import 'package:flutter/material.dart';

class CameraWidget extends StatelessWidget {
 
  final double width;

  const CameraWidget({Key? key, required this.width}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Using an AssetImage as a placeholder; replace with your camera functionality
    return Image.asset(
      'assets/images/no_input.png',
      width: width,
      fit: BoxFit.cover,
    );
  }
}