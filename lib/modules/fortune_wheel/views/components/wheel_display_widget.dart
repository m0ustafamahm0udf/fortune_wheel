import 'package:flutter/material.dart';

import '../../../../core/utils/app_colors.dart';
import 'wheel_painters.dart';

/// Widget that displays the rotating wheel with arrow indicator - Premium Design
class WheelDisplayWidget extends StatelessWidget {
  final double wheelSize;
  final double currentAngle;
  final double arrowOffset;
  final List<String> items;
  final Color Function(int) getColor;
  final int winnerIndex;
  final bool isSpinning;

  const WheelDisplayWidget({
    Key? key,
    required this.wheelSize,
    required this.currentAngle,
    required this.arrowOffset,
    required this.items,
    required this.getColor,
    required this.winnerIndex,
    required this.isSpinning,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      width: wheelSize + 60,
      height: wheelSize + 80,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        // boxShadow: [
        //   BoxShadow(
        //     color: AppColors.primary.withOpacity(0.31),
        //     blurRadius: 1,
        //     spreadRadius: 5,
        //   ),
        // ],
      ),
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Outer glow ring
          Positioned(
            top: 25,
            child: Container(
              width: wheelSize + 20,
              height: wheelSize + 20,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: LinearGradient(
                  colors: [
                    AppColors.accentGold.withOpacity(0.5),
                    AppColors.primary.withOpacity(0.3),
                    AppColors.accentCyan.withOpacity(0.5),
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.accentGold.withOpacity(0.4),
                    blurRadius: 20,
                    spreadRadius: 2,
                  ),
                ],
              ),
            ),
          ),
          // The rotating wheel
          Positioned(
            top: 35,
            child: Transform.rotate(
              angle: currentAngle,
              child: Container(
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.5),
                      blurRadius: 15,
                      offset: const Offset(0, 5),
                    ),
                  ],
                ),
                child: CustomPaint(
                  size: Size(wheelSize, wheelSize),
                  painter: WheelPainter(
                    items: items,
                    getColor: getColor,
                    winnerIndex: winnerIndex,
                    isSpinning: isSpinning,
                  ),
                ),
              ),
            ),
          ),
          // Center circle with gradient
          Positioned(
            top: 35 + wheelSize / 2 - 35,
            child: Container(
              width: 70,
              height: 70,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: LinearGradient(
                  colors: [AppColors.cardDark, AppColors.surfaceDark],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                border: Border.all(color: AppColors.accentGold, width: 3),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.accentGold.withOpacity(0.5),
                    blurRadius: 10,
                    spreadRadius: 2,
                  ),
                ],
              ),
              child: Center(
                child: Icon(
                  Icons.diamond,
                  color: AppColors.accentGold,
                  size: 30,
                ),
              ),
            ),
          ),
          // Arrow indicator at TOP, with animation
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: Center(
              child: Transform.translate(
                offset: Offset(0, arrowOffset),
                child: Container(
                  width: 25,
                  height: 20,
                  child: CustomPaint(painter: ArrowPainter()),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
