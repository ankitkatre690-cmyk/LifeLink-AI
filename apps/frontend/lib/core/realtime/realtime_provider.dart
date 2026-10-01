import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../config/app_config.dart';

import 'websocket_service.dart';

final realtimeServiceProvider = Provider<WebSocketService>((ref) {
  final service = WebSocketService(
    baseHttpUrl: AppConfig.realtimeBaseHttpUrl,
  );

  ref.onDispose(service.dispose);
  return service;
});

void connectRealtime(WidgetRef ref, String token) {
  ref.read(realtimeServiceProvider).connect(token);
}
