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
  bool _initialized = false;

  Future<void> initialize() async {
    if (_initialized) return;

    if (kIsWeb) {
      // Web push requires a VAPID key and Firebase web configuration.
      return;
    }

    await Firebase.initializeApp();
    _messaging = FirebaseMessaging.instance;

    await _messaging!.requestPermission(
      alert: true,
      badge: true,
      sound: true,
      provisional: false,
    );

    final token = await _messaging!.getToken();
    if (token != null && token.isNotEmpty) {
      await _registerToken(token);
    }

    _messaging!.onTokenRefresh.listen((refreshedToken) async {
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

  String _platformName() {
    if (kIsWeb) return 'web';
    if (Platform.isAndroid) return 'android';
    if (Platform.isIOS) return 'ios';
    return 'other';
  }
}
