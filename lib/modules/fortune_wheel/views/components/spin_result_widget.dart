import 'package:flutter/material.dart';

import '../../../../core/utils/app_colors.dart';

/// Widget to display spin info - Premium Design
class SpinResultWidget extends StatelessWidget {
  final String finalAngleDisplay;
  final String actualRotationsDisplay;
  final String remainingRotationsDisplay;
  final String remainingTimeDisplay;
  final bool isSpinning;

  const SpinResultWidget({
    Key? key,
    required this.finalAngleDisplay,
    required this.actualRotationsDisplay,
    required this.remainingRotationsDisplay,
    required this.remainingTimeDisplay,
    required this.isSpinning,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Don't show if no data
    if (!isSpinning && finalAngleDisplay.isEmpty) {
      return const SizedBox.shrink();
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [AppColors.surfaceDark, AppColors.cardDark],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isSpinning
              ? AppColors.accentCyan.withOpacity(0.5)
              : Colors.greenAccent.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          // Angle
          _buildInfoItem(
            icon: Icons.rotate_right,
            label: "Angle",
            value: isSpinning ? "..." : finalAngleDisplay,
            color: Colors.greenAccent,
          ),
          _buildDivider(),
          // Total Rotations
          _buildInfoItem(
            icon: Icons.loop,
            label: "Total",
            value: actualRotationsDisplay,
            color: Colors.orangeAccent,
          ),
          _buildDivider(),
          // Remaining Rotations
          _buildInfoItem(
            icon: Icons.hourglass_empty,
            label: "Remaining",
            value: isSpinning ? remainingRotationsDisplay : "0.0",
            color: AppColors.accentCyan,
            highlight: isSpinning,
          ),
          _buildDivider(),
          // Remaining Time
          _buildInfoItem(
            icon: Icons.timer,
            label: "Time",
            value: isSpinning ? "${remainingTimeDisplay}s" : "0.0s",
            color: Colors.pinkAccent,
            highlight: isSpinning,
          ),
        ],
      ),
    );
  }

  Widget _buildDivider() {
    return Container(
      height: 35,
      width: 1,
      color: Colors.white.withOpacity(0.1),
    );
  }

  Widget _buildInfoItem({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
    bool highlight = false,
  }) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: color, size: 16),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            color: AppColors.white.withOpacity(0.5),
            fontSize: 10,
          ),
        ),
        Text(
          value,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: color,
            fontSize: 14,
          ),
        ),
      ],
    );
  }
}
