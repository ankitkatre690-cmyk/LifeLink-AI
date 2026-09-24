import 'package:dio/dio.dart';
import '../../../core/network/api_client.dart';

class HospitalApi {
  HospitalApi(this._client);
  final ApiClient _client;

  Future<Map<String, dynamic>> getMyProfile() async {
    final response = await _client.dio.get('/hospitals/me');
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<List<Map<String, dynamic>>> getResources(String hospitalId) async {
    final response = await _client.dio.get('/hospitals/$hospitalId/resources');
    return (response.data as List<dynamic>)
        .map((item) => Map<String, dynamic>.from(item as Map))
        .toList();
  }

  Future<Map<String, dynamic>> updateResource({
    required String resourceId,
    required int totalCount,
    required int availableCount,
    required bool isAvailable,
  }) async {
    final response = await _client.dio.patch(
      '/hospitals/resources/$resourceId',
      data: {
        'total_count': totalCount,
        'available_count': availableCount,
        'is_available': isAvailable,
      },
    );
    return Map<String, dynamic>.from(response.data as Map);
  }
}
