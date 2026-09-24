import 'dart:async';
import 'dart:io' show Platform;

import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../network/api_client.dart';
import '../storage/secure_storage.dart';

final pushNotificationServiceProvider = Provider<PushNotificationService>(
  (ref) => PushNotificationService(
    ref.watch(apiClientProvider),
    ref.watch(secureStorageProvider),
  ),
);

class PushNotificationService {
  PushNotificationService(this._api, this._storage);

  final ApiClient _api;
  final SecureStorage _storage;
  FirebaseMessaging? _messaging;
  StreamSubscription<String>? _tokenSubscription;
  StreamSubscription<RemoteMessage>? _foregroundSubscription;
  bool _initialized = false;

  final _messages = StreamController<RemoteMessage>.broadcast();

  Stream<RemoteMessage> get foregroundMessages => _messages.stream;

  Future<void> initialize() async {
    if (_initialized || kIsWeb) return;

    await Firebase.initializeApp();
    _messaging = FirebaseMessaging.instance;

    await _messaging!.requestPermission(
      alert: true,
      badge: true,
      sound: true,
      provisional: false,
    );

    _foregroundSubscription = FirebaseMessaging.onMessage.listen(
      _messages.add,
    );

    final token = await _messaging!.getToken();
    if (token != null && token.isNotEmpty) {
      await _registerToken(token);
    }

    _tokenSubscription = _messaging!.onTokenRefresh.listen((refreshedToken) async {
      if (refreshedToken.isNotEmpty) {
        await _registerToken(refreshedToken);
      }
    });

    _initialized = true;
  }

  Future<void> _registerToken(String token) async {
    final response = await _api.dio.post(
      '/notifications/device-tokens',
      data: {
        'token': token,
        'platform': _platformName(),
      },
    );
    final id = response.data['id']?.toString();
    if (id != null && id.isNotEmpty) {
      await _storage.saveDeviceTokenId(id);
    }
  }

  Future<void> unregisterCurrentToken() async {
    final id = await _storage.readDeviceTokenId();
    if (id == null || id.isEmpty) return;

    try {
      await _api.dio.delete('/notifications/device-tokens/$id');
    } finally {
      await _storage.clearDeviceTokenId();
    }
  }

  Future<void> dispose() async {
    await _tokenSubscription?.cancel();
    await _foregroundSubscription?.cancel();
    await _messages.close();
  }

  String _platformName() {
    if (kIsWeb) return 'web';
    if (Platform.isAndroid) return 'android';
    if (Platform.isIOS) return 'ios';
    return 'other';
  }
}

@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
}
