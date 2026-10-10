import 'package:flutter_test/flutter_test.dart';

import 'package:lifelink_ai/features/responder/presentation/responder_home_page.dart';
import 'package:lifelink_ai/core/realtime/websocket_service.dart';

void main() {
  test('maps dispatch assignment realtime events', () {
    final assignment = responderAssignmentFromRealtimeEvent(
      const RealtimeEvent(
        event: 'dispatch.assignment',
        data: {
          'assignment_id': 'assignment-1',
          'emergency_id': 'emergency-1',
          'status': 'Assigned',
          'distance_km': 4.2,
          'eta_minutes': 9,
        },
      ),
    );

    expect(assignment?['id'], 'assignment-1');
    expect(assignment?['emergency_id'], 'emergency-1');
    expect(assignment?['status'], 'Assigned');
    expect(assignment?['distance_km'], 4.2);
    expect(assignment?['eta_minutes'], 9);
  });

  test('ignores non-assignment realtime events', () {
    final assignment = responderAssignmentFromRealtimeEvent(
      const RealtimeEvent(
        event: 'connected',
        data: {},
      ),
    );

    expect(assignment, isNull);
  });

  test('ignores assignments without an assignment id', () {
    final assignment = responderAssignmentFromRealtimeEvent(
      const RealtimeEvent(
        event: 'dispatch.assignment',
        data: {'emergency_id': 'emergency-1'},
      ),
    );

    expect(assignment, isNull);
  });
}
