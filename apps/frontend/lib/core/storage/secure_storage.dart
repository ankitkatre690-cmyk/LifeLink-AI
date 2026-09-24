import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorage {
  const SecureStorage();

  static const _accessTokenKey = 'access_token';
  static const _roleKey = 'user_role';

  static const FlutterSecureStorage _storage = FlutterSecureStorage();

  Future<void> saveSession({
    required String accessToken,
    required String role,
  }) async {
    await _storage.write(key: _accessTokenKey, value: accessToken);
    await _storage.write(key: _roleKey, value: role);
  }

  Future<String?> readAccessToken() {
    return _storage.read(key: _accessTokenKey);
  }

  Future<String?> readRole() {
    return _storage.read(key: _roleKey);
  }

  Future<void> clearSession() async {
    await _storage.delete(key: _accessTokenKey);
    await _storage.delete(key: _roleKey);
  }
}
