import 'package:flutter/material.dart';
import 'package:fortune_eyt/core/utils/app_colors.dart';

class WebFixedSizeWrapper extends StatelessWidget {
  final Widget child;

  const WebFixedSizeWrapper({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    // مقاس ثابت للعرض والارتفاع (مثال: iPhone X)
    const double fixedWidth = 500;
    const double fixedHeight = 1080;

    return LayoutBuilder(
      builder: (context, constraints) {
        return Container(
          decoration: BoxDecoration(color: AppColors.backgroundDark),
          child: Center(
            child: ConstrainedBox(
              constraints: BoxConstraints(
                maxWidth: fixedWidth,
                maxHeight: fixedHeight,
                minWidth: fixedWidth,
                // minHeight: fixedHeight,
              ),
              child: child,
            ),
          ),
        );
      },
    );
  }
}
