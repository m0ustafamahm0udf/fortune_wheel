class RemoteCommandModel {
  final String command;
  final Map<String, dynamic>? params;

  RemoteCommandModel({required this.command, this.params});

  factory RemoteCommandModel.fromJson(Map<String, dynamic> json) {
    return RemoteCommandModel(
      command: json['command'] ?? 'IDLE',
      params: json['params'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {'command': command, 'params': params};
  }
}
