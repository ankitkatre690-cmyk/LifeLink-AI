import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

class RealtimeClient {
  RealtimeClient({
    required this.baseUrl,
    required this.accessToken,
    this.reconnectDelay = const Duration(seconds: 3),
  });

  final String baseUrl;
  final String accessToken;
  final Duration reconnectDelay;

  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _subscription;
  Timer? _heartbeat;
  Timer? _reconnectTimer;
  final _events = StreamController<Map<String, dynamic>>.broadcast();

  bool _disposed = false;
  bool _connected = false;

  Stream<Map<String, dynamic>> get events => _events.stream;
  bool get isConnected => _connected;

  void connect() {
    if (_disposed || _connected) return;
    _reconnectTimer?.cancel();
    _open();
  }

  void _open() {
    if (_disposed) return;

    final uri = Uri.parse(baseUrl);
    final wsUri = uri.replace(
      scheme: uri.scheme == 'https' ? 'wss' : 'ws',
      path: '/ws',
      queryParameters: {'token': accessToken},
    );

    final channel = WebSocketChannel.connect(wsUri);
    _channel = channel;

    _subscription = channel.stream.listen(
      (message) {
        if (message is! String) return;
        try {
          final decoded = jsonDecode(message);
          if (decoded is Map) {
            final event = Map<String, dynamic>.from(decoded);
            if (event['event'] == 'connected') {
              _connected = true;
              _startHeartbeat();
            }
            _events.add(event);
          }
        } catch (_) {
          // Ignore malformed realtime messages.
        }
      },
      onError: (Object error, StackTrace stackTrace) {
        _connected = false;
        _stopHeartbeat();
        if (!_disposed) _events.addError(error, stackTrace);
      },
      onDone: () {
        _connected = false;
        _stopHeartbeat();
        _scheduleReconnect();
      },
      cancelOnError: false,
    );
  }

  void _startHeartbeat() {
    _heartbeat?.cancel();
    _heartbeat = Timer.periodic(
      const Duration(seconds: 20),
      (_) => sendHeartbeat(),
    );
  }

  void _stopHeartbeat() {
    _heartbeat?.cancel();
    _heartbeat = null;
  }

  void _scheduleReconnect() {
    if (_disposed || _reconnectTimer?.isActive == true) return;
    _reconnectTimer = Timer(reconnectDelay, connect);
  }

  void sendHeartbeat() {
    if (_connected) {
      _channel?.sink.add('ping');
    }
  }

  Future<void> dispose() async {
    _disposed = true;
    _reconnectTimer?.cancel();
    _stopHeartbeat();
    await _subscription?.cancel();
    await _channel?.sink.close();
    await _events.close();
  }
}
