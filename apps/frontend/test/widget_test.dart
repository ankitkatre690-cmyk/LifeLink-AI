import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:lifelink_ai/app.dart';

void main() {
  testWidgets('LifeLink AI shows the login screen', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: LifeLinkApp(),
      ),
    );
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('Sign in'), findsOneWidget);
    expect(find.text('Email'), findsOneWidget);
    expect(find.text('Password'), findsOneWidget);
  });
}
