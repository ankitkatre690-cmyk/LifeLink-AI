import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';

class EmergencyRepository {
  EmergencyRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<Map<String, dynamic>> createEmergency({
    required String emergencyType,
    required String severity,
    required double latitude,
    required double longitude,
    String? description,
  }) async {
    final response = await _apiClient.dio.post(
      '/emergency',
      data: {
        'emergency_type': emergencyType,
        'severity': severity,
        'latitude': latitude,
        'longitude': longitude,
        if (description != null && description.trim().isNotEmpty)
          'description': description.trim(),
      },
    );

    return Map<String, dynamic>.from(response.data as Map);
  }
}
