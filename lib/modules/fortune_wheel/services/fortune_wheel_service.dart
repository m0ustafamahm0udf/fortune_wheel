import 'dart:math';

import 'package:flutter/material.dart';

import '../../../core/utils/app_colors.dart';

/// Service class for Fortune Wheel logic and calculations
class FortuneWheelService {
  /// Generate segment items labels
  static List<String> generateItems(int count) {
    return List.generate(count, (i) => 'No ${i + 1}');
  }

  /// Generate segment colors from predefined palette
  static List<Color> generateColors(int count) {
    return List.generate(
      count,
      (i) => AppColors.wheelColors[i % AppColors.wheelColors.length],
    );
  }

  /// Calculate the total rotation angle for a spin
  static SpinCalculation calculateSpin({
    required double currentAngle,
    required double rotationsPerSecond,
  }) {
    final random = Random();
    final randomOffset = random.nextDouble() * 2 * pi;
    final startAngle = currentAngle;
    final totalRotationRadians = rotationsPerSecond * 2 * pi + randomOffset;
    final endAngle = startAngle + totalRotationRadians;
    final totalRotations = totalRotationRadians / (2 * pi);

    return SpinCalculation(
      startAngle: startAngle,
      endAngle: endAngle,
      totalRotations: totalRotations,
      totalRotationRadians: totalRotationRadians,
    );
  }

  /// Calculate remaining rotations during animation
  static double calculateRemainingRotations({
    required double currentAngle,
    required double startAngle,
    required double totalRotations,
  }) {
    final completed = (currentAngle - startAngle) / (2 * pi);
    return (totalRotations - completed).clamp(0.0, totalRotations);
  }

  /// Calculate the winning segment index based on final angle
  static WinnerResult calculateWinner({
    required double currentAngle,
    required int itemCount,
  }) {
    final segmentAngle = 2 * pi / itemCount;
    double normalizedAngle = currentAngle % (2 * pi);

    // Adjust angle: The wheel rotates clockwise.
    // The "index" under the arrow is the one whose center is closest to the rolled angle.
    // Normalized angle = 0 means we are at the center of Segment 0.
    // We reverse the rotation to map to index space.
    double adjustedAngle = (2 * pi - normalizedAngle) % (2 * pi);

    // Rounding finds the closest segment center
    int winner = (adjustedAngle / segmentAngle).round() % itemCount;

    if (winner < 0) winner += itemCount;

    final angleInDegrees = (normalizedAngle * 180 / pi).toStringAsFixed(1);

    return WinnerResult(winnerIndex: winner, angleInDegrees: angleInDegrees);
  }

  /// Get color for a segment based on state
  static Color getItemColor({
    required int index,
    required List<Color> segmentColors,
    required bool isSpinning,
    required int winnerIndex,
    required double pulseValue,
  }) {
    if (index >= segmentColors.length) return Colors.grey;

    final baseColor = segmentColors[index];

    if (isSpinning) {
      return baseColor.withOpacity(0.4);
    }

    if (winnerIndex != -1 && index == winnerIndex) {
      return baseColor.withOpacity(pulseValue);
    }

    return baseColor.withOpacity(0.4);
  }
}

/// Data class for spin calculation results
class SpinCalculation {
  final double startAngle;
  final double endAngle;
  final double totalRotations;
  final double totalRotationRadians;

  SpinCalculation({
    required this.startAngle,
    required this.endAngle,
    required this.totalRotations,
    required this.totalRotationRadians,
  });
}

/// Data class for winner calculation results
class WinnerResult {
  final int winnerIndex;
  final String angleInDegrees;

  WinnerResult({required this.winnerIndex, required this.angleInDegrees});
}
