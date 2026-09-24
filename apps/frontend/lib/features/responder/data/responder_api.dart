import 'package:dio/dio.dart';
import '../../../core/network/api_client.dart';

class ResponderApi {
  ResponderApi(this._client);
  final ApiClient _client;

  Future<Map<String, dynamic>> getMyProfile() async {
    final response = await _client.dio.get('/responders/me');
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<Map<String, dynamic>> updateStatus(String status) async {
    final response = await _client.dio.patch(
      '/responders/me/status',
      data: {'status': status},
    );
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<Map<String, dynamic>> updateLocation(double latitude, double longitude) async {
    final response = await _client.dio.patch(
      '/responders/me/location',
      data: {'latitude': latitude, 'longitude': longitude},
    );
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<Map<String, dynamic>> getAssignment(String assignmentId) async {
    final response = await _client.dio.get('/responders/assignments/$assignmentId');
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<Map<String, dynamic>> updateAssignment(
    String assignmentId,
    String status, {
    String? notes,
  }) async {
    final response = await _client.dio.patch(
      '/responders/assignments/$assignmentId',
      data: {
        'status': status,
        if (notes != null && notes.isNotEmpty) 'notes': notes,
      },
    );
    return Map<String, dynamic>.from(response.data as Map);
  }
}
