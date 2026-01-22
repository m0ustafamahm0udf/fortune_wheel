import 'dart:math';

import 'package:flutter/material.dart';

/// Custom painter for the wheel segments - Premium Design
class WheelPainter extends CustomPainter {
  final List<String> items;
  final Color Function(int) getColor;
  final int winnerIndex;
  final bool isSpinning;

  WheelPainter({
    required this.items,
    required this.getColor,
    required this.winnerIndex,
    required this.isSpinning,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2;
    final segmentAngle = 2 * pi / items.length;

    for (int i = 0; i < items.length; i++) {
      final color = getColor(i);

      // Create gradient paint for each segment
      final paint = Paint()
        ..shader = RadialGradient(
          colors: [color, color.withOpacity(0.7)],
          stops: const [0.5, 1.0],
        ).createShader(Rect.fromCircle(center: center, radius: radius))
        ..style = PaintingStyle.fill;

      // Segment 0 starts centered at TOP
      // Shift back by half segment so the center of the segment aligns with -pi/2
      final startAngle = i * segmentAngle - pi / 2 - segmentAngle / 2;
      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        startAngle,
        segmentAngle,
        true,
        paint,
      );

      // Draw subtle segment divider
      final dividerPaint = Paint()
        ..color = Colors.white.withOpacity(0.2)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1;

      final dividerStartX = center.dx + radius * 0.15 * cos(startAngle);
      final dividerStartY = center.dy + radius * 0.15 * sin(startAngle);
      final dividerEndX = center.dx + radius * cos(startAngle);
      final dividerEndY = center.dy + radius * sin(startAngle);

      canvas.drawLine(
        Offset(dividerStartX, dividerStartY),
        Offset(dividerEndX, dividerEndY),
        dividerPaint,
      );

      // Draw text at segment center
      final textAngle = startAngle + segmentAngle / 2;
      final textRadius = radius * 0.65;
      final textX = center.dx + textRadius * cos(textAngle);
      final textY = center.dy + textRadius * sin(textAngle);

      final textPainter = TextPainter(
        text: TextSpan(
          text: items[i],
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 14,
            shadows: [
              Shadow(
                color: Colors.black.withOpacity(0.5),
                blurRadius: 4,
                offset: const Offset(1, 1),
              ),
            ],
          ),
        ),
        textDirection: TextDirection.ltr,
      );
      textPainter.layout();

      canvas.save();
      canvas.translate(textX, textY);
      canvas.rotate(textAngle + pi / 2);
      textPainter.paint(
        canvas,
        Offset(-textPainter.width / 2, -textPainter.height / 2),
      );
      canvas.restore();
    }

    // Draw outer ring
    final outerRingPaint = Paint()
      ..color = Colors.white.withOpacity(0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3;
    canvas.drawCircle(center, radius, outerRingPaint);
  }

  @override
  bool shouldRepaint(covariant WheelPainter oldDelegate) => true;
}

/// Custom painter for the arrow indicator - Premium Design
class ArrowPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    // Arrow shadow
    final shadowPath = Path()
      ..moveTo(size.width / 2, size.height + 2)
      ..lineTo(-2, -2)
      ..lineTo(size.width + 2, -2)
      ..close();

    canvas.drawPath(
      shadowPath,
      Paint()
        ..color = Colors.black.withOpacity(0.3)
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 4),
    );

    // Arrow gradient fill
    final paint = Paint()
      ..shader = const LinearGradient(
        colors: [
          Color(0xFFFFD700), // Gold
          Color(0xFFFF8C00), // Dark Orange
        ],
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));

    // Triangle pointing DOWN
    final path = Path()
      ..moveTo(size.width / 2, size.height) // Bottom point
      ..lineTo(0, 0) // Top left
      ..lineTo(size.width, 0) // Top right
      ..close();

    canvas.drawPath(path, paint);

    // Add white border for visibility
    final borderPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;
    canvas.drawPath(path, borderPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
