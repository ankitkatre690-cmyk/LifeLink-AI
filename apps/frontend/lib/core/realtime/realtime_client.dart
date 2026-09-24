import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

class RealtimeClient {
  RealtimeClient({required this.baseUrl, required this.accessToken});

  final String baseUrl;
  final String accessToken;

  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _subscription;
  final _events = StreamController<Map<String, dynamic>>.broadcast();

  Stream<Map<String, dynamic>> get events => _events.stream;

  void connect() {
    final uri = Uri.parse(baseUrl);
    final wsUri = uri.replace(
      scheme: uri.scheme == 'https' ? 'wss' : 'ws',
      path: '/ws',
      queryParameters: {'token': accessToken},
    );
    _channel = WebSocketChannel.connect(wsUri);
    _subscription = _channel!.stream.listen(
      (message) {
        if (message is! String) return;
        try {
          final decoded = jsonDecode(message);
          if (decoded is Map) _events.add(Map<String, dynamic>.from(decoded));
        } catch (_) {}
      },
      onError: _events.addError,
    );
  }

  void sendHeartbeat() => _channel?.sink.add('ping');

  Future<void> dispose() async {
    await _subscription?.cancel();
    await _channel?.sink.close();
    await _events.close();
  }
}
