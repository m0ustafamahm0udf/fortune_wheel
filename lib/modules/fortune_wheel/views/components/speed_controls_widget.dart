import 'package:flutter/material.dart';

import '../../../../core/utils/app_colors.dart';

/// Widget for speed and duration slider controls - Premium Design
class SpeedControlsWidget extends StatelessWidget {
  final double rotationsPerSecond;
  final double durationSeconds;
  final bool isSpinning;
  final ValueChanged<double> onRotationsChanged;
  final ValueChanged<double> onDurationChanged;

  const SpeedControlsWidget({
    Key? key,
    required this.rotationsPerSecond,
    required this.durationSeconds,
    required this.isSpinning,
    required this.onRotationsChanged,
    required this.onDurationChanged,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.cardDark,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.primary.withOpacity(0.3), width: 1),
      ),
      child: Column(
        children: [
          // Speed control (Rotations per second)
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(Icons.speed, color: AppColors.accentCyan, size: 16),
                  const SizedBox(width: 6),
                  Text(
                    "Speed",
                    style: TextStyle(
                      color: AppColors.white.withOpacity(0.7),
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  "${rotationsPerSecond.toInt()} rotations",
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    color: AppColors.accentCyan,
                    fontSize: 11,
                  ),
                ),
              ),
            ],
          ),
          SliderTheme(
            data: SliderTheme.of(context).copyWith(
              activeTrackColor: AppColors.accentCyan,
              inactiveTrackColor: AppColors.surfaceDark,
              thumbColor: AppColors.accentCyan,
              overlayColor: AppColors.accentCyan.withOpacity(0.2),
              trackHeight: 4,
            ),
            child: Slider(
              value: rotationsPerSecond,
              min: 1,
              max: 300,
              divisions: 299,
              onChanged: isSpinning ? null : onRotationsChanged,
            ),
          ),

          const SizedBox(height: 10),

          // Duration control
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(Icons.timer, color: AppColors.accentGold, size: 16),
                  const SizedBox(width: 6),
                  Text(
                    "Duration",
                    style: TextStyle(
                      color: AppColors.white.withOpacity(0.7),
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: AppColors.accentGold.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  "${durationSeconds.toInt()} sec",
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    color: AppColors.accentGold,
                    fontSize: 11,
                  ),
                ),
              ),
            ],
          ),
          SliderTheme(
            data: SliderTheme.of(context).copyWith(
              activeTrackColor: AppColors.accentGold,
              inactiveTrackColor: AppColors.surfaceDark,
              thumbColor: AppColors.accentGold,
              overlayColor: AppColors.accentGold.withOpacity(0.2),
              trackHeight: 4,
            ),
            child: Slider(
              value: durationSeconds,
              min: 1,
              max: 60,
              divisions: 59,
              onChanged: isSpinning ? null : onDurationChanged,
            ),
          ),
        ],
      ),
    );
  }
}
