import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:fortune_eyt/web.dart';
import 'modules/fortune_wheel/views/fortune_wheel_view.dart';

void main() {
  runApp(kIsWeb ? WebFixedSizeWrapper(child: MyApp()) : MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Fortune Wheel Demo',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const FortuneWheelView(),
    );
  }
}
