
import '../../../core/network/api_client.dart';

class EmergencyApi {
  EmergencyApi(this._client);

  final ApiClient _client;

  Future<Map<String, dynamic>> getEmergency(String emergencyId) async {
    final response = await _client.dio.get('/emergency/$emergencyId');
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<List<Map<String, dynamic>>> getTimeline(String emergencyId) async {
    final response = await _client.dio.get('/emergency/$emergencyId/timeline');
    return (response.data as List)
        .map((item) => Map<String, dynamic>.from(item as Map))
        .toList();
  }

  Future<Map<String, dynamic>> updateEmergencyStatus({
    required String emergencyId,
    required String status,
    String? remarks,
  }) async {
    final response = await _client.dio.patch(
      '/emergency/$emergencyId',
      data: {
        'status': status,
        if (remarks != null && remarks.trim().isNotEmpty)
          'remarks': remarks.trim(),
      },
    );
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<Map<String, dynamic>> createEmergency({
    required String emergencyType,
    required double latitude,
    required double longitude,
    String? description,
  }) async {
    final response = await _client.dio.post(
      '/emergency',
      data: {
        'emergency_type': emergencyType,
        'latitude': latitude,
        'longitude': longitude,
        if (description != null) 'description': description,
      },
    );
    return Map<String, dynamic>.from(response.data as Map);
  }
}
