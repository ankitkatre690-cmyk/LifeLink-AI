import 'package:flutter_test/flutter_test.dart';

import 'package:lifelink_ai/features/responder/presentation/responder_home_page.dart';

void main() {
  test('allows only valid responder assignment transitions', () {
    expect(
      nextResponderAssignmentStatuses('Assigned'),
      ['Accepted', 'Cancelled'],
    );
    expect(
      nextResponderAssignmentStatuses('Accepted'),
      ['EnRoute', 'Cancelled'],
    );
    expect(
      nextResponderAssignmentStatuses('EnRoute'),
      ['OnScene', 'Cancelled'],
    );
    expect(
      nextResponderAssignmentStatuses('OnScene'),
      ['Completed', 'Cancelled'],
    );
  });

  test('does not offer transitions for terminal or unknown assignments', () {
    expect(nextResponderAssignmentStatuses('Completed'), isEmpty);
    expect(nextResponderAssignmentStatuses('Cancelled'), isEmpty);
    expect(nextResponderAssignmentStatuses('Unknown'), isEmpty);
  });
}
