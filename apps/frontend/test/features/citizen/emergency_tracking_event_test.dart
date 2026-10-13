import 'package:flutter_test/flutter_test.dart';

import 'package:lifelink_ai/features/citizen/presentation/emergency_tracking_page.dart';

void main() {
  test('maps emergency status events to emergency state only', () {
    final mapping = mapEmergencyTrackingEvent(
      'emergency.status_changed',
      {'status': 'Assigned'},
    );

    expect(mapping.emergencyStatus, 'Assigned');
    expect(mapping.assignmentStatus, isNull);
  });

  test('maps dispatch assignment status without overwriting emergency state', () {
    final mapping = mapEmergencyTrackingEvent(
      'dispatch.assigned',
      {'status': 'Assigned'},
    );

    expect(mapping.emergencyStatus, isNull);
    expect(mapping.assignmentStatus, 'Assigned');
  });

  test('maps responder assignment and authoritative emergency status separately', () {
    final mapping = mapEmergencyTrackingEvent(
      'responder.assignment_status_changed',
      {
        'status': 'EnRoute',
        'emergency_status': 'InProgress',
      },
    );

    expect(mapping.assignmentStatus, 'EnRoute');
    expect(mapping.emergencyStatus, 'InProgress');
  });

  test('ignores location events for emergency and assignment status', () {
    final mapping = mapEmergencyTrackingEvent(
      'responder.location_updated',
      {
        'assignment_status': 'EnRoute',
        'latitude': 20.0,
        'longitude': 79.0,
      },
    );

    expect(mapping.emergencyStatus, isNull);
    expect(mapping.assignmentStatus, isNull);
  });

  test('ignores unrelated events', () {
    final mapping = mapEmergencyTrackingEvent(
      'dispatch.hospital_incoming',
      {'status': 'Assigned'},
    );

    expect(mapping.emergencyStatus, isNull);
    expect(mapping.assignmentStatus, isNull);
  });
}
