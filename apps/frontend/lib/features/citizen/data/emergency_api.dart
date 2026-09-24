import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';

class EmergencyApi {
  EmergencyApi(this._client);

  final ApiClient _client;

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
