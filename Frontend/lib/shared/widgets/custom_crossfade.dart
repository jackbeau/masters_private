import 'package:flutter/material.dart';
import 'package:logger/logger.dart';

/// Custom crossfade widget to address a glitch in the default Flutter crossfade widget.
/// This widget ensures that the alpha layer works correctly.
/// See https://github.com/flutter/flutter/issues/80075 for more details.
///
/// Author: Jack Beaumont
/// Date: 06/06/2024

class CustomCrossfade extends StatefulWidget {
  final Widget firstChild;
  final Widget secondChild;
  final bool showFirst;
  final Duration duration;

  /// Creates a [CustomCrossfade] widget.
  ///
  /// [firstChild] and [secondChild] are the widgets to crossfade between.
  /// [showFirst] determines which widget to show initially.
  /// [duration] sets the duration of the crossfade animation.
  const CustomCrossfade({
    super.key,
    required this.firstChild,
    required this.secondChild,
    required this.showFirst,
    this.duration = const Duration(milliseconds: 300),
  });

  @override
  CustomCrossfadeState createState() => CustomCrossfadeState();
}

class CustomCrossfadeState extends State<CustomCrossfade> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  final Logger _logger = Logger();

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(duration: widget.duration, vsync: this);
    _logger.i('CustomCrossfade initialized with showFirst: ${widget.showFirst}');
    widget.showFirst ? _controller.reverse() : _controller.forward();
  }

  @override
  void didUpdateWidget(CustomCrossfade oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.showFirst != oldWidget.showFirst) {
      _logger.i('CustomCrossfade showFirst updated: ${widget.showFirst}');
      widget.showFirst ? _controller.reverse() : _controller.forward();
    }
  }

  @override
  void dispose() {
    _logger.i('CustomCrossfade disposed');
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      alignment: Alignment.center,
      children: <Widget>[
        FadeTransition(
          opacity: _controller.drive(Tween<double>(begin: 0.0, end: 1.0).chain(CurveTween(curve: Curves.easeOut))),
          child: widget.firstChild,
        ),
        FadeTransition(
          opacity: _controller.drive(Tween<double>(begin: 1.0, end: 0.0).chain(CurveTween(curve: Curves.easeIn))),
          child: widget.secondChild,
        ),
      ],
    );
  }
}
