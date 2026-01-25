import 'package:flutter/material.dart';

import '../../../core/utils/app_colors.dart';
import '../../../core/utils/app_constance.dart';
import '../services/fortune_wheel_service.dart';
import 'components/wheel_display_widget.dart';
import 'components/speed_controls_widget.dart';
import 'components/spin_result_widget.dart';
import 'components/control_buttons_widget.dart';
import 'components/segment_customization_widget.dart';
import '../services/remote_control_service.dart';
import '../models/remote_command_model.dart';

class FortuneWheelView extends StatefulWidget {
  const FortuneWheelView({Key? key}) : super(key: key);

  @override
  State<FortuneWheelView> createState() => _FortuneWheelViewState();
}

class _FortuneWheelViewState extends State<FortuneWheelView>
    with TickerProviderStateMixin {
  // Segment state
  int _segmentCount = 8;
  late List<String> _items;
  late List<Color> _segmentColors;

  // Animation controllers
  late AnimationController _rotationController;
  late Animation<double> _rotationAnimation;
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;
  late AnimationController _arrowController;
  late Animation<double> _arrowAnimation;

  // State
  bool _isSpinning = false;
  int _winnerIndex = -1;
  double _rotationsPerSecond = 1.0;
  double _durationSeconds = 3.0;
  double _currentAngle = 0.0;

  // Display values
  String _finalAngleDisplay = "";
  String _actualRotationsDisplay = "";
  String _remainingRotationsDisplay = "";
  String _remainingTimeDisplay = "";
  bool _isRemoteMode = false;
  bool _isConnecting = false;
  final TextEditingController _ipController = TextEditingController(
    text: "localhost",
  );

  // Spin calculation storage
  double _spinStartAngle = 0.0;
  double _totalRotations = 0.0;

  @override
  void initState() {
    super.initState();
    _initSegments();
    _initAnimations();
    _initRemoteControl();
  }

  void _initRemoteControl() {
    RemoteControlService().commandStream.listen((command) {
      if (!mounted || !_isRemoteMode) return;
      _handleRemoteCommand(command);
    });
  }

  void _toggleRemoteMode() {
    setState(() {
      _isRemoteMode = !_isRemoteMode;
      if (!_isRemoteMode) {
        RemoteControlService().disconnect();
        AppConstance().showErrorToast(context, msg: "Remote Mode Disabled");
      }
    });
  }

  Future<void> _connectToRpi() async {
    final ip = _ipController.text.trim();
    if (ip.isEmpty) {
      AppConstance().showErrorToast(context, msg: "Please enter a valid IP");
      return;
    }

    setState(() => _isConnecting = true);

    try {
      await RemoteControlService().connect(ip);
      if (mounted) {
        if (RemoteControlService().isConnected) {
          AppConstance().showSuccesToast(context, msg: "Connected to RPi");
        } else {
          AppConstance().showErrorToast(
            context,
            msg: "Failed to connect to RPi",
          );
        }
      }
    } catch (e) {
      if (mounted) {
        AppConstance().showErrorToast(context, msg: "Connection Error: $e");
      }
    } finally {
      if (mounted) setState(() => _isConnecting = false);
    }
  }

  void _handleRemoteCommand(RemoteCommandModel command) {
    if (mounted) {
      AppConstance().showSuccesToast(
        context,
        msg: "Remote: ${command.command}",
      );
    }
    switch (command.command.toUpperCase()) {
      case 'SPIN':
        if (!_isSpinning) {
          if (command.params != null) {
            final rps = command.params!['rps'];
            final duration = command.params!['duration'];
            setState(() {
              if (rps != null) _rotationsPerSecond = (rps as num).toDouble();
              if (duration != null)
                _durationSeconds = (duration as num).toDouble();
            });
          }
          _start();
        }
        break;
      case 'STOP':
        if (_isSpinning) _stop();
        break;
      case 'RESET':
        _resetConfiguration();
        break;
      case 'UPDATE_CONFIG':
        if (command.params != null) {
          final rps = command.params!['rps'];
          final duration = command.params!['duration'];
          final segments = command.params!['segments'];

          setState(() {
            if (rps != null) {
              _rotationsPerSecond = (rps as num).toDouble();
            }
            if (duration != null) {
              _durationSeconds = (duration as num).toDouble();
            }
            if (segments != null) {
              _updateSegmentCount((segments as num).toInt());
            }
          });
        }
        break;
    }
  }

  void _initSegments() {
    _items = FortuneWheelService.generateItems(_segmentCount);
    _segmentColors = FortuneWheelService.generateColors(_segmentCount);
  }

  void _initAnimations() {
    _rotationController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    );
    _rotationController.addStatusListener((status) {
      if (status == AnimationStatus.completed) _onSpinComplete();
    });

    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    );
    _pulseAnimation = Tween<double>(begin: 0.4, end: 1.0).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
    _pulseController.addListener(() => setState(() {}));

    _arrowController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 400),
    );
    _arrowAnimation = Tween<double>(
      begin: 0,
      end: -15,
    ).animate(CurvedAnimation(parent: _arrowController, curve: Curves.easeOut));
    _arrowController.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    _rotationController.dispose();
    _pulseController.dispose();
    _arrowController.dispose();
    _ipController.dispose();
    super.dispose();
  }

  void _updateSegmentCount(int count) {
    setState(() {
      _segmentCount = count;
      _items = FortuneWheelService.generateItems(count);
      _segmentColors = FortuneWheelService.generateColors(count);
      _winnerIndex = -1;
    });
  }

  void _resetConfiguration() {
    setState(() {
      _segmentCount = 8;
      _items = FortuneWheelService.generateItems(_segmentCount);
      _segmentColors = FortuneWheelService.generateColors(_segmentCount);
      _rotationsPerSecond = 1.0;
      _durationSeconds = 3.0;
      _winnerIndex = -1;
      _finalAngleDisplay = "";
      _actualRotationsDisplay = "";
      _remainingRotationsDisplay = "";
      _remainingTimeDisplay = "";
      _currentAngle = 0.0;
      _remainingTimeDisplay = "";
      _currentAngle = 0.0;
    });
    _sendToArduino(command: "RESET", targetAngle: 0.0, speed: 1.0);
  }

  void _start() {
    if (_isSpinning) return;

    setState(() {
      _isSpinning = true;
      _winnerIndex = -1;
      _pulseController.stop();
      _pulseController.reset();
      _arrowController.forward();
    });

    final calc = FortuneWheelService.calculateSpin(
      currentAngle: _currentAngle,
      rotationsPerSecond: _rotationsPerSecond,
    );

    _spinStartAngle = calc.startAngle;
    _totalRotations = calc.totalRotations;
    _actualRotationsDisplay = calc.totalRotations.toStringAsFixed(2);

    _rotationAnimation =
        Tween<double>(begin: calc.startAngle, end: calc.endAngle).animate(
          CurvedAnimation(
            parent: _rotationController,
            curve: Curves.easeOutQuart,
          ),
        );

    _rotationAnimation.addListener(() {
      final remaining = FortuneWheelService.calculateRemainingRotations(
        currentAngle: _rotationAnimation.value,
        startAngle: _spinStartAngle,
        totalRotations: _totalRotations,
      );

      // Calculate remaining time
      final totalDuration = _rotationController.duration?.inMilliseconds ?? 0;
      final remainingMillis = totalDuration * (1 - _rotationController.value);
      final remainingSeconds = (remainingMillis / 1000).clamp(
        0.0,
        _durationSeconds,
      );

      setState(() {
        _currentAngle = _rotationAnimation.value;
        _remainingRotationsDisplay = remaining.toStringAsFixed(1);
        _remainingTimeDisplay = remainingSeconds.toStringAsFixed(1);
      });
    });

    _rotationController.duration = Duration(seconds: _durationSeconds.toInt());
    _rotationController.reset();
    _rotationController.forward();

    _sendToArduino(
      command: "SPIN",
      durationMs: _rotationController.duration!.inMilliseconds,
      totalRotations: calc.totalRotations,
      targetAngle: calc.endAngle * 180 / 3.14159, // Approx degrees
    );
  }

  void _stop() {
    if (!_isSpinning) return;

    _rotationController.stop();
    _sendToArduino(
      command: "STOP",
      currentAngle: _currentAngle * 180 / 3.14159,
    );
    _onSpinComplete();
  }

  void _sendToArduino({
    required String command,
    int? durationMs,
    double? totalRotations,
    double? targetAngle,
    double? currentAngle,
    double? speed,
  }) {
    // Simulation of sending data to a Serial port
    debugPrint("--------------------------------------------------");
    debugPrint("📡 ARDUINO OUTPUT SIMULATION");
    debugPrint("--------------------------------------------------");
    debugPrint("Command: $command");
    if (durationMs != null) debugPrint("Duration: ${durationMs}ms");
    if (speed != null) debugPrint("Speed: ${speed.toStringAsFixed(1)} rps");
    if (totalRotations != null)
      debugPrint("Total Rotations: ${totalRotations.toStringAsFixed(2)}");
    if (targetAngle != null)
      debugPrint("Target Angle: ${targetAngle.toStringAsFixed(1)}°");
    if (currentAngle != null)
      debugPrint("Stop Angle: ${currentAngle.toStringAsFixed(1)}°");
    debugPrint("--------------------------------------------------");
  }

  void _onSpinComplete() {
    final result = FortuneWheelService.calculateWinner(
      currentAngle: _currentAngle,
      itemCount: _items.length,
    );

    setState(() {
      _isSpinning = false;
      _winnerIndex = result.winnerIndex;
      _finalAngleDisplay = "${result.angleInDegrees}°";
      _pulseController.repeat(reverse: true);
      _arrowController.reverse();
    });
  }

  Color _getItemColor(int index) {
    return FortuneWheelService.getItemColor(
      index: index,
      segmentColors: _segmentColors,
      isSpinning: _isSpinning,
      winnerIndex: _winnerIndex,
      pulseValue: _pulseAnimation.value,
    );
  }

  void _showSettingsSheet() {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.cardDark,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      isScrollControlled: true,
      builder: (context) => StatefulBuilder(
        builder: (context, setSheetState) => Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const SizedBox(height: 20),
              const Text(
                '⚙️ Customize Wheel',
                style: TextStyle(
                  color: AppColors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              SegmentCustomizationWidget(
                segmentCount: _segmentCount,
                segmentColors: _segmentColors,
                isSpinning: false,
                onCountChanged: (count) {
                  _updateSegmentCount(count);
                  setSheetState(() {});
                },
                onColorChanged: (index, color) {
                  setState(() => _segmentColors[index] = color);
                  setSheetState(() {});
                },
              ),
              const SizedBox(height: 20),
              GestureDetector(
                onTap: () => Navigator.pop(context),
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [AppColors.primary, Color(0xFF4834D4)],
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Center(
                    child: Text(
                      'Done',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 10),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    const double wheelSize = 350;

    return Scaffold(
      backgroundColor: AppColors.backgroundDark,
      appBar: AppBar(
        title: const Text(
          '🎡 Fortune Wheel',
          style: TextStyle(
            color: AppColors.white,
            fontWeight: FontWeight.bold,
            fontSize: 22,
          ),
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              color: _isRemoteMode
                  ? AppColors.primary.withOpacity(0.2)
                  : AppColors.cardDark,
              borderRadius: BorderRadius.circular(12),
              border: _isRemoteMode
                  ? Border.all(color: AppColors.primary, width: 1)
                  : null,
            ),
            child: IconButton(
              icon: Icon(
                _isRemoteMode ? Icons.developer_board : Icons.language,
                color: _isRemoteMode ? AppColors.primary : AppColors.greya8,
              ),
              onPressed: _isSpinning ? null : _toggleRemoteMode,
              tooltip: _isRemoteMode
                  ? 'Switch to Web App Mode'
                  : 'Switch to Raspberry Pi Mode',
            ),
          ),
          Container(
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              color: AppColors.cardDark,
              borderRadius: BorderRadius.circular(12),
            ),
            child: IconButton(
              icon: const Icon(Icons.restore, color: AppColors.error3c),
              onPressed: _isSpinning ? null : _resetConfiguration,
              tooltip: 'Reset to Defaults',
            ),
          ),
          Container(
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              color: AppColors.cardDark,
              borderRadius: BorderRadius.circular(12),
            ),
            child: IconButton(
              icon: const Icon(Icons.settings, color: AppColors.accentGold),
              onPressed: _isSpinning ? null : _showSettingsSheet,
              tooltip: 'Customize Wheel',
            ),
          ),
        ],
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [AppColors.primary.withOpacity(0.3), Colors.transparent],
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
            ),
          ),
        ),
      ),
      body: SingleChildScrollView(
        padding: AppConstance.padding20,
        child: Column(
          children: [
            if (_isRemoteMode) ...[
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.primary.withOpacity(0.5)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "📡 Raspberry Pi Connection",
                      style: TextStyle(
                        color: AppColors.primary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    AppConstance.gap10,
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _ipController,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 13,
                            ),
                            decoration: InputDecoration(
                              hintText:
                                  "IP from RPi screen (e.g. 192.168.1.18)",
                              hintStyle: TextStyle(
                                color: Colors.white.withOpacity(0.3),
                              ),
                              contentPadding: const EdgeInsets.symmetric(
                                horizontal: 10,
                              ),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        _isConnecting
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : ElevatedButton(
                                onPressed: _connectToRpi,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: AppColors.primary,
                                ),
                                child: Text(
                                  RemoteControlService().isConnected
                                      ? "Reconnect"
                                      : "Connect",
                                ),
                              ),
                      ],
                    ),
                    if (RemoteControlService().isConnected) ...[
                      AppConstance.gap5,
                      Text(
                        "Status: Connected to ${RemoteControlService().serverIp}",
                        style: const TextStyle(
                          color: Colors.green,
                          fontSize: 11,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              AppConstance.gap20,
            ],
            AppConstance.gap20,
            Center(
              child: WheelDisplayWidget(
                wheelSize: wheelSize,
                currentAngle: _currentAngle,
                arrowOffset: _arrowAnimation.value,
                items: _items,
                getColor: _getItemColor,
                winnerIndex: _winnerIndex,
                isSpinning: _isSpinning,
              ),
            ),
            AppConstance.gap20,
            SpinResultWidget(
              finalAngleDisplay: _finalAngleDisplay,
              actualRotationsDisplay: _actualRotationsDisplay,
              remainingRotationsDisplay: _remainingRotationsDisplay,
              remainingTimeDisplay: _remainingTimeDisplay,
              isSpinning: _isSpinning,
            ),
            AppConstance.gap10,
            SpeedControlsWidget(
              rotationsPerSecond: _rotationsPerSecond,
              durationSeconds: _durationSeconds,
              isSpinning: _isSpinning,
              onRotationsChanged: (val) {
                setState(() => _rotationsPerSecond = val.roundToDouble());
              },
              onDurationChanged: (val) {
                setState(() => _durationSeconds = val.roundToDouble());
              },
            ),
            AppConstance.gap20,
            ControlButtonsWidget(
              isSpinning: _isSpinning,
              onStart: _start,
              onStop: _stop,
            ),
            AppConstance.gap20,
          ],
        ),
      ),
    );
  }
}
