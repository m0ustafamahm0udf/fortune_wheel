import 'package:flutter/material.dart';
import 'app_colors.dart';

class AppConstance {
  static const double textScaleFactor = 1.0;
  static const double borderWidth = 0.1;

  static const SizedBox gap5 = SizedBox(height: 5, width: 5);
  static const SizedBox gap10 = SizedBox(height: 10, width: 10);
  static const SizedBox gap20 = SizedBox(height: 20, width: 20);

  static const EdgeInsets padding20 = EdgeInsets.all(20);

  // Helper to show error toast
  void showErrorToast(BuildContext context, {required String msg}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(msg, style: TextStyle(color: AppColors.white)),
        backgroundColor: AppColors.error3c,
      ),
    );
  }

  // Helper to show success toast
  void showSuccesToast(BuildContext context, {required String msg}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(msg, style: TextStyle(color: AppColors.white)),
        backgroundColor: Colors.green,
      ),
    );
  }
}
