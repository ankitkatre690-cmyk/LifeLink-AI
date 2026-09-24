import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../network/api_client.dart';
import '../storage/secure_storage.dart';

final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());

final secureStorageProvider = Provider<SecureStorage>((ref) => const SecureStorage());

final authProvider = NotifierProvider<AuthController, AuthState>(
  AuthController.new,
);

class AuthState {
  const AuthState({
    this.isLoading = false,
    this.isAuthenticated = false,
    this.role,
    this.error,
  });

  final bool isLoading;
  final bool isAuthenticated;
  final String? role;
  final String? error;

  AuthState copyWith({
    bool? isLoading,
    bool? isAuthenticated,
    String? role,
    String? error,
    bool clearError = false,
  }) {
    return AuthState(
      isLoading: isLoading ?? this.isLoading,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      role: role ?? this.role,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

class AuthController extends Notifier<AuthState> {
  late final ApiClient _api;
  late final SecureStorage _storage;

  @override
  AuthState build() {
    _api = ref.read(apiClientProvider);
    _storage = ref.read(secureStorageProvider);
    return const AuthState();
  }

  Future<void> restoreSession() async {
    final token = await _storage.readAccessToken();
    final role = await _storage.readRole();

    if (token == null || role == null) {
      state = const AuthState();
      return;
    }

    _api.setAccessToken(token);
    state = AuthState(isAuthenticated: true, role: role);
  }

  Future<bool> login({
    required String email,
    required String password,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final response = await _api.dio.post(
        '/auth/login',
        data: {'email': email, 'password': password},
      );

      final token = response.data['access_token'] as String?;
      final tokenType = response.data['token_type'] as String?;

      if (token == null || tokenType == null) {
        throw const FormatException('Invalid authentication response.');
      }

      _api.setAccessToken(token);

      // The current backend login response contains only the token.
      // Role retrieval is completed by the authenticated /auth/me endpoint
      // in the next authentication increment.
      await _storage.saveSession(accessToken: token, role: 'pending');

      state = AuthState(isAuthenticated: true, role: 'pending');
      return true;
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        isAuthenticated: false,
        error: 'Login failed. Check your credentials and try again.',
      );
      return false;
    }
  }

  Future<void> logout() async {
    await _storage.clearSession();
    _api.clearAccessToken();
    state = const AuthState();
  }
}
