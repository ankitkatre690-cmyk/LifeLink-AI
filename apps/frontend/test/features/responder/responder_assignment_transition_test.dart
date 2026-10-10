import 'package:flutter_test/flutter_test.dart';

import 'package:lifelink_ai/features/responder/presentation/responder_home_page.dart';

void main() {
  test('allows Assigned to transition to Accepted or Cancelled', () {
    expect(
      nextResponderAssignmentStatuses('Assigned'),
      ['Accepted', 'Cancelled'],
    );
  });

  test('allows Accepted to transition to EnRoute or Cancelled', () {
    expect(
      nextResponderAssignmentStatuses('Accepted'),
      ['EnRoute', 'Cancelled'],
    );
  });

  test('allows EnRoute to transition to OnScene or Cancelled', () {
    expect(
      nextResponderAssignmentStatuses('EnRoute'),
      ['OnScene', 'Cancelled'],
    );
  });

  test('allows OnScene to transition to Completed or Cancelled', () {
    expect(
      nextResponderAssignmentStatuses('OnScene'),
      ['Completed', 'Cancelled'],
    );
  });

  test('does not expose transitions for terminal or unknown states', () {
    expect(nextResponderAssignmentStatuses('Completed'), isEmpty);
    expect(nextResponderAssignmentStatuses('Cancelled'), isEmpty);
    expect(nextResponderAssignmentStatuses('Unknown'), isEmpty);
  });
}
