import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../models/remote_command_model.dart';

class RemoteControlService {
  static final RemoteControlService _instance =
      RemoteControlService._internal();
  factory RemoteControlService() => _instance;
  RemoteControlService._internal();

  final _commandController = StreamController<RemoteCommandModel>.broadcast();
  Stream<RemoteCommandModel> get commandStream => _commandController.stream;

  WebSocketChannel? _channel;
  bool _isConnected = false;
  bool get isConnected => _isConnected;
  String _serverIp = "";
  String get serverIp => _serverIp;

  RemoteCommandModel? _pendingAngle;
  Timer? _angleFlushTimer;

  /// Connect to the RPi WebSocket server
  Future<void> connect(String ipInput, {int port = 8080}) async {
    if (_isConnected) await disconnect();

    try {
      // 1. Clean the input (remove ws://, http://, and trailing /ws)
      String cleaned = ipInput
          .trim()
          .replaceAll("ws://", "")
          .replaceAll("wss://", "")
          .replaceAll("http://", "")
          .replaceAll("https://", "");
      if (cleaned.endsWith("/ws"))
        cleaned = cleaned.substring(0, cleaned.length - 3);
      if (cleaned.endsWith("/"))
        cleaned = cleaned.substring(0, cleaned.length - 1);

      // 2. Determine IP and Port
      String finalIp = cleaned;
      int finalPort = port;

      if (cleaned.contains(":")) {
        final parts = cleaned.split(":");
        finalIp = parts[0];
        finalPort = int.tryParse(parts[1]) ?? port;
      }

      final uri = Uri.parse('ws://$finalIp:$finalPort');
      debugPrint("📡 RemoteControlService: Attempting connect to $uri");

      _channel = WebSocketChannel.connect(uri);

      // Wait for the connection to be established with a 5-second timeout
      await _channel!.ready.timeout(const Duration(seconds: 5));

      _serverIp = finalIp;
      _isConnected = true;

      // Send identification message
      _channel!.sink.add(
        jsonEncode({
          "type": "IDENTIFY",
          "platform": kIsWeb ? "Web Browser" : defaultTargetPlatform.toString(),
        }),
      );

      debugPrint("📡 RemoteControlService: Connected to $uri");

      _channel!.stream.listen(
        (data) {
          try {
            if (data is List<int>) {
              final bytes = Uint8List.fromList(data);
              final byteData = ByteData.sublistView(bytes);
              final deltaDegrees = byteData.getInt8(0).toDouble();

              final command = RemoteCommandModel(
                command: 'ANGLE_DELTA',
                params: {'delta': deltaDegrees},
              );
              _pendingAngle = command;
              _angleFlushTimer ??=
                  Timer(const Duration(milliseconds: 16), () {
                _angleFlushTimer = null;
                final pending = _pendingAngle;
                _pendingAngle = null;
                if (pending != null) _commandController.add(pending);
              });
            } else {
              final decoded = jsonDecode(data.toString());
              final command = RemoteCommandModel.fromJson(decoded);
              _commandController.add(command);
            }
          } catch (e) {
            debugPrint("Failed to parse command: $data");
          }
        },
        onDone: () {
          debugPrint("❌ Disconnected from RPi Server");
          _isConnected = false;
        },
        onError: (e) {
          debugPrint("❌ WebSocket Client Error: $e");
          _isConnected = false;
        },
      );
    } catch (e) {
      debugPrint("❌ RemoteControlService Connection Error: $e");
      _isConnected = false;
    }
  }

  Future<void> disconnect() async {
    _angleFlushTimer?.cancel();
    _angleFlushTimer = null;
    _pendingAngle = null;
    await _channel?.sink.close();
    _isConnected = false;
    _serverIp = "";
    debugPrint("🛑 RemoteControlService: Disconnected");
  }

  void stop() {
    disconnect();
  }

  void dispose() {
    stop();
    _commandController.close();
  }
}
