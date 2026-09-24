import 'package:dio/dio.dart';
import '../../../core/network/api_client.dart';

class PoliceApi {
  PoliceApi(this._client);
  final ApiClient _client;

  Future<List<Map<String, dynamic>>> getActiveEmergencies() async {
    final response = await _client.dio.get('/police/emergencies/active');
    return (response.data as List<dynamic>)
        .map((item) => Map<String, dynamic>.from(item as Map))
        .toList();
  }

  Future<Map<String, dynamic>> createCase(String emergencyId, {String? notes}) async {
    final response = await _client.dio.post(
      '/police/cases/$emergencyId',
      data: {if (notes != null && notes.isNotEmpty) 'notes': notes},
    );
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<Map<String, dynamic>> getCase(String caseId) async {
    final response = await _client.dio.get('/police/cases/$caseId');
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<Map<String, dynamic>> updateCase(
    String caseId, {
    required String status,
    String? notes,
  }) async {
    final response = await _client.dio.patch(
      '/police/cases/$caseId',
      data: {
        'case_status': status,
        if (notes != null) 'notes': notes,
      },
    );
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<Map<String, dynamic>> dispatch(String emergencyId) async {
    final response = await _client.dio.post(
      '/police/dispatch',
      data: {'emergency_id': emergencyId},
    );
    return Map<String, dynamic>.from(response.data as Map);
  }
}
