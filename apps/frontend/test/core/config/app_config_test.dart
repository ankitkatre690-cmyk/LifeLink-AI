import 'package:flutter_test/flutter_test.dart';

import 'package:lifelink_ai/core/config/app_config.dart';

void main() {
  test('uses Android emulator API default', () {
    expect(
      AppConfig.apiBaseUrl,
      'http://10.0.2.2:8000/api/v1',
    );
  });

  test('derives websocket backend URL from API URL', () {
    expect(
      AppConfig.realtimeBaseHttpUrl,
      'http://10.0.2.2:8000',
    );
  });
}
