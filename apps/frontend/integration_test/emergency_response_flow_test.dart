import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  const baseUrl = String.fromEnvironment('LIFELINK_TEST_BASE_URL');
  const citizenEmail = String.fromEnvironment('LIFELINK_TEST_CITIZEN_EMAIL');
  const citizenPassword = String.fromEnvironment('LIFELINK_TEST_CITIZEN_PASSWORD');
  const policeEmail = String.fromEnvironment('LIFELINK_TEST_POLICE_EMAIL');
  const policePassword = String.fromEnvironment('LIFELINK_TEST_POLICE_PASSWORD');
  const responderEmail = String.fromEnvironment('LIFELINK_TEST_RESPONDER_EMAIL');
  const responderPassword = String.fromEnvironment('LIFELINK_TEST_RESPONDER_PASSWORD');

  final configured = baseUrl.isNotEmpty &&
      citizenEmail.isNotEmpty &&
      citizenPassword.isNotEmpty &&
      policeEmail.isNotEmpty &&
      policePassword.isNotEmpty &&
      responderEmail.isNotEmpty &&
      responderPassword.isNotEmpty;

  test(
    'Citizen -> Police -> Responder emergency flow',
    () async {

    Dio api(String token) => Dio(BaseOptions(
          baseUrl: '$baseUrl/api/v1',
          headers: {'Authorization': 'Bearer $token'},
        ));

    Future<String> login(String email, String password) async {
      final response = await Dio(BaseOptions(baseUrl: '$baseUrl/api/v1')).post(
        '/auth/login',
        data: {'username': email, 'password': password},
        options: Options(contentType: Headers.formUrlEncodedContentType),
      );
      return response.data['access_token'] as String;
    }

    final citizen = api(await login(citizenEmail, citizenPassword));
    final emergencyResponse = await citizen.post('/emergency', data: {
      'emergency_type': 'medical',
      'latitude': 20.5937,
      'longitude': 78.9629,
      'description': 'Automated LifeLink E2E test emergency',
    });
    final emergency = Map<String, dynamic>.from(emergencyResponse.data as Map);
    final emergencyId = emergency['id']?.toString() ?? emergency['emergency_id']?.toString();
    expect(emergencyId, isNotNull);

    final police = api(await login(policeEmail, policePassword));
    final dispatchResponse = await police.post(
      '/dispatch',
      data: {'emergency_id': emergencyId},
    );
    final dispatch = Map<String, dynamic>.from(dispatchResponse.data as Map);
    final assignmentId = dispatch['assignment_id']?.toString();
    expect(assignmentId, isNotNull);

    final responder = api(await login(responderEmail, responderPassword));

    Future<void> updateAssignment(String status) async {
      final response = await responder.patch(
        '/responders/assignments/$assignmentId',
        data: {'status': status},
      );
      expect(response.statusCode, inInclusiveRange(200, 299));
    }

    await updateAssignment('Accepted');
    await updateAssignment('EnRoute');
    await updateAssignment('OnScene');
    await updateAssignment('Completed');

    final finalEmergency = await citizen.get('/emergency/$emergencyId');
    expect(finalEmergency.statusCode, 200);
    expect(finalEmergency.data['status'], 'Completed');
    },
    skip: !configured,
  );
}
