import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';

class FamilyApi {
  FamilyApi(this._client);

  final ApiClient _client;

  Future<Map<String, dynamic>> getFamily() async {
    final response = await _client.dio.get('/family');
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<List<Map<String, dynamic>>> getMembers() async {
    final response = await _client.dio.get('/family/members');
    final data = response.data as List<dynamic>;
    return data
        .map((item) => Map<String, dynamic>.from(item as Map))
        .toList();
  }

  Future<Map<String, dynamic>> createFamily(String name) async {
    final response = await _client.dio.post('/family', data: {'name': name});
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<Map<String, dynamic>> addMember({
    required String userId,
    required String relationship,
    bool isGuardian = false,
  }) async {
    final response = await _client.dio.post(
      '/family/member',
      data: {
        'user_id': userId,
        'relationship': relationship,
        'is_guardian': isGuardian,
      },
    );
    return Map<String, dynamic>.from(response.data as Map);
  }
}
