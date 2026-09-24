import 'package:dio/dio.dart';
import '../../../core/network/api_client.dart';

class AdminApi {
  AdminApi(this._client);
  final ApiClient _client;

  Future<Map<String, dynamic>> getDashboard() async {
    final response = await _client.dio.get('/admin/dashboard');
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<List<Map<String, dynamic>>> getUsers({int limit = 50, int offset = 0}) async {
    final response = await _client.dio.get(
      '/admin/users',
      queryParameters: {'limit': limit, 'offset': offset},
    );
    return (response.data as List<dynamic>)
        .map((item) => Map<String, dynamic>.from(item as Map))
        .toList();
  }

  Future<Map<String, dynamic>> updateUserStatus(
    String userId,
    bool isActive,
  ) async {
    final response = await _client.dio.patch(
      '/admin/users/$userId/status',
      data: {'is_active': isActive},
    );
    return Map<String, dynamic>.from(response.data as Map);
  }
}
