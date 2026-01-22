import 'package:flutter/material.dart';
import 'package:flutter_colorpicker/flutter_colorpicker.dart';

import '../../../../core/utils/app_colors.dart';

/// Widget for customizing segments (count and colors) - Premium Design
class SegmentCustomizationWidget extends StatelessWidget {
  final int segmentCount;
  final List<Color> segmentColors;
  final bool isSpinning;
  final ValueChanged<int> onCountChanged;
  final Function(int index, Color color) onColorChanged;

  const SegmentCustomizationWidget({
    Key? key,
    required this.segmentCount,
    required this.segmentColors,
    required this.isSpinning,
    required this.onCountChanged,
    required this.onColorChanged,
  }) : super(key: key);

  void _showColorPicker(BuildContext context, int index) {
    Color currentColor = segmentColors[index];

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppColors.cardDark,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Text(
          'Segment ${index + 1} Color',
          style: const TextStyle(color: AppColors.white),
        ),
        content: SingleChildScrollView(
          child: ColorPicker(
            pickerColor: currentColor,
            onColorChanged: (color) {
              currentColor = color;
            },
            enableAlpha: false,
            labelTypes: const [],
            pickerAreaHeightPercent: 0.7,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Cancel',
              style: TextStyle(color: AppColors.white.withOpacity(0.7)),
            ),
          ),
          Container(
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [AppColors.primary, Color(0xFF4834D4)],
              ),
              borderRadius: BorderRadius.circular(20),
            ),
            child: TextButton(
              onPressed: () {
                onColorChanged(index, currentColor);
                Navigator.pop(context);
              },
              child: const Padding(
                padding: EdgeInsets.symmetric(horizontal: 8),
                child: Text(
                  'Apply',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.cardDark,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: AppColors.accentPink.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        children: [
          // Segment count selector
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.pie_chart_outline,
                    color: AppColors.accentPink,
                    size: 16,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    "Segments",
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
                  color: AppColors.accentPink.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  "$segmentCount",
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    color: AppColors.accentPink,
                    fontSize: 14,
                  ),
                ),
              ),
            ],
          ),
          SliderTheme(
            data: SliderTheme.of(context).copyWith(
              activeTrackColor: AppColors.accentPink,
              inactiveTrackColor: AppColors.surfaceDark,
              thumbColor: AppColors.accentPink,
              overlayColor: AppColors.accentPink.withOpacity(0.2),
              trackHeight: 4,
            ),
            child: Slider(
              value: segmentCount.toDouble(),
              min: 2,
              max: 12,
              divisions: 10,
              onChanged: isSpinning
                  ? null
                  : (val) => onCountChanged(val.toInt()),
            ),
          ),

          const SizedBox(height: 8),

          // Color boxes label
          Row(
            children: [
              Icon(
                Icons.palette,
                color: AppColors.accentPink.withOpacity(0.7),
                size: 16,
              ),
              const SizedBox(width: 6),
              Text(
                "Tap to customize colors",
                style: TextStyle(
                  color: AppColors.white.withOpacity(0.5),
                  fontSize: 12,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),

          // Color boxes for each segment
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: List.generate(segmentCount, (index) {
              return GestureDetector(
                onTap: isSpinning
                    ? null
                    : () => _showColorPicker(context, index),
                child: Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    color: segmentColors[index],
                    borderRadius: BorderRadius.circular(8),
                    boxShadow: [
                      BoxShadow(
                        color: segmentColors[index].withOpacity(0.5),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                    border: Border.all(
                      color: Colors.white.withOpacity(0.3),
                      width: 2,
                    ),
                  ),
                  child: Center(
                    child: Text(
                      '${index + 1}',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                        shadows: [
                          Shadow(
                            color: Colors.black.withOpacity(0.5),
                            blurRadius: 2,
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              );
            }),
          ),
        ],
      ),
    );
  }
}
