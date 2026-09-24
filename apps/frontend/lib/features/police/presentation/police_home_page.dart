import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/auth/auth_state.dart';

class PoliceHomePage extends ConsumerWidget {
  const PoliceHomePage({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) => Scaffold(
    appBar: AppBar(title: const Text('LifeLink AI'), actions: [
      IconButton(tooltip: 'Sign out', onPressed: () => ref.read(authProvider.notifier).logout(), icon: const Icon(Icons.logout)),
    ]),
    body: Center(child: Text('$title', style: Theme.of(context).textTheme.headlineSmall)),
  );
}
