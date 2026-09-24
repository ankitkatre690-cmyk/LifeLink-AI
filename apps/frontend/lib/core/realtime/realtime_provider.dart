import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/auth_state.dart';
import 'websocket_service.dart';

final realtimeServiceProvider = Provider<WebSocketService>((ref) {
  final service = WebSocketService(
    baseHttpUrl: 'http://10.0.2.2:8000',
  );

  ref.onDispose(service.dispose);
  return service;
});

void connectRealtime(WidgetRef ref, String token) {
  ref.read(realtimeServiceProvider).connect(token);
}
