import 'package:flutter/material.dart';

import '../../../../core/utils/app_colors.dart';

/// Widget for start and stop control buttons - Premium Design
class ControlButtonsWidget extends StatelessWidget {
  final bool isSpinning;
  final VoidCallback onStart;
  final VoidCallback onStop;

  const ControlButtonsWidget({
    Key? key,
    required this.isSpinning,
    required this.onStart,
    required this.onStop,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // START Button
        GestureDetector(
          onTap: isSpinning ? null : onStart,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: isSpinning
                    ? [Colors.grey, Colors.grey.shade700]
                    : [AppColors.primary, const Color(0xFF4834D4)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(30),
              boxShadow: isSpinning
                  ? []
                  : [
                      BoxShadow(
                        color: AppColors.primary.withOpacity(0.5),
                        blurRadius: 15,
                        offset: const Offset(0, 5),
                      ),
                    ],
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  isSpinning ? Icons.loop : Icons.play_arrow,
                  color: Colors.white,
                  size: 24,
                ),
                const SizedBox(width: 8),
                Text(
                  isSpinning ? "SPINNING..." : "START",
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
                    letterSpacing: 1,
                  ),
                ),
              ],
            ),
          ),
        ),

        if (isSpinning) ...[
          const SizedBox(width: 16),
          // STOP Button
          GestureDetector(
            onTap: onStop,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 16),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFFFF6B6B), Color(0xFFEE5A24)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(30),
                boxShadow: [
                  BoxShadow(
                    color: Colors.red.withOpacity(0.5),
                    blurRadius: 15,
                    offset: const Offset(0, 5),
                  ),
                ],
              ),
              child: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.stop, color: Colors.white, size: 24),
                  SizedBox(width: 8),
                  Text(
                    "STOP",
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                      letterSpacing: 1,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ],
    );
  }
}
