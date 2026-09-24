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

  Stream<RealtimeEvent> get events => _eventsController.stream;

  void connect(String token) {
    disconnect();

    final uri = Uri.parse(baseHttpUrl);
    final scheme = uri.scheme == 'https' ? 'wss' : 'ws';
    final websocketUri = uri.replace(
      scheme: scheme,
      path: '/ws',
      queryParameters: {'token': token},
    );

    final channel = WebSocketChannel.connect(websocketUri);
    _channel = channel;

    _subscription = channel.stream.listen(
      (message) {
        try {
          final json = jsonDecode(message as String);
          if (json is Map<String, dynamic>) {
            _eventsController.add(RealtimeEvent.fromJson(json));
          }
        } catch (_) {
          // Ignore malformed realtime frames; the API remains authoritative.
        }
      },
      onError: (Object error, StackTrace stackTrace) {
        _eventsController.addError(error, stackTrace);
      },
      onDone: () {
        _channel = null;
      },
      cancelOnError: false,
    );
  }

  Future<void> sendHeartbeat() async {
    _channel?.sink.add('ping');
  }

  Future<void> disconnect() async {
    await _subscription?.cancel();
    _subscription = null;
    await _channel?.sink.close();
    _channel = null;
  }

  Future<void> dispose() async {
    await disconnect();
    await _eventsController.close();
  }
}
