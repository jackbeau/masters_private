import 'package:flutter/material.dart';

// @jackb
// Custom crossfade widget as the flutter one has a glitch which causes it to go to black
// See https://github.com/flutter/flutter/issues/80075
// But the fix there does not work as we need the alpha layer to work. So I came up with this


class CustomCrossfade extends StatefulWidget {
  final Widget firstChild;
  final Widget secondChild;
  final bool showFirst;
  final Duration duration;

  const CustomCrossfade({
    Key? key,
    required this.firstChild,
    required this.secondChild,
    required this.showFirst,
    this.duration = const Duration(milliseconds: 300),
  }) : super(key: key);

  @override
  _CustomCrossfadeState createState() => _CustomCrossfadeState();
}

class _CustomCrossfadeState extends State<CustomCrossfade> with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(duration: widget.duration, vsync: this);
    widget.showFirst ? _controller.reverse() : _controller.forward();
  }

  @override
  void didUpdateWidget(CustomCrossfade oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.showFirst != oldWidget.showFirst) {
      widget.showFirst ? _controller.reverse() : _controller.forward();
    }
  }

  @override
  void dispose() {
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
