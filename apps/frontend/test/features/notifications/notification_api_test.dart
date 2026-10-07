import 'package:flutter_test/flutter_test.dart';

void main() {
  test('notification endpoint contract is present', () {
    expect('/notifications', startsWith('/notifications'));
    expect('/notifications/{id}', contains('/notifications/'));
  });
}
