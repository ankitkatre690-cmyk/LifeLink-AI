import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

class RealtimeEvent {
  const RealtimeEvent({
    required this.event,
    required this.data,
    this.timestamp,
  });

  final String event;
  final Map<String, dynamic> data;
  final String? timestamp;

  factory RealtimeEvent.fromJson(Map<String, dynamic> json) {
    return RealtimeEvent(
      event: json['event'] as String? ?? 'unknown',
      timestamp: json['timestamp'] as String?,
      data: Map<String, dynamic>.from(
        (json['data'] as Map?) ?? const <String, dynamic>{},
      ),
    );
  }
}

class WebSocketService {
  WebSocketService({required this.baseHttpUrl});

  final String baseHttpUrl;

  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _subscription;

  final _eventsController = StreamController<RealtimeEvent>.broadcast();
  Timer? _reconnectTimer;
  Timer? _heartbeat;
  String? _token;
  bool _disposed = false;
  bool _connected = false;

  Stream<RealtimeEvent> get events => _eventsController.stream;
  bool get isConnected => _connected;

  void connect(String token) {
    if (_disposed || token.isEmpty) return;
    _token = token;
    _reconnectTimer?.cancel();
    _open();
  }

  void _open() {
    if (_disposed || _token == null || _token!.isEmpty) return;
    final uri = Uri.parse(baseHttpUrl);
    final scheme = uri.scheme == 'https' ? 'wss' : 'ws';
    final websocketUri = uri.replace(
      scheme: scheme,
      path: '/ws',
      queryParameters: {'token': _token!},
    );

    final channel = WebSocketChannel.connect(websocketUri);
    _channel = channel;
    _connected = false;

    _subscription = channel.stream.listen(
      (message) {
        try {
          final json = jsonDecode(message as String);
          if (json is Map<String, dynamic>) {
            final event = RealtimeEvent.fromJson(json);
            if (event.event == 'connected') {
              _connected = true;
              _startHeartbeat();
            }
            _eventsController.add(event);
          }
        } catch (_) {
          // Ignore malformed realtime frames; the API remains authoritative.
        }
      },
      onError: (Object error, StackTrace stackTrace) {
        _connected = false;
        _stopHeartbeat();
        if (!_disposed) _eventsController.addError(error, stackTrace);
      },
      onDone: () {
        _connected = false;
        _stopHeartbeat();
        _channel = null;
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
    _reconnectTimer = Timer(const Duration(seconds: 3), _open);
  }


  Future<void> sendHeartbeat() async {
    if (_connected) _channel?.sink.add('ping');
  }

  Future<void> disconnect() async {
    _reconnectTimer?.cancel();
    _reconnectTimer = null;
    _stopHeartbeat();
    _connected = false;
    await _subscription?.cancel();
    _subscription = null;
    await _channel?.sink.close();
    _channel = null;
  }

  Future<void> dispose() async {
    _disposed = true;
    await disconnect();
    await _eventsController.close();
  }
}
