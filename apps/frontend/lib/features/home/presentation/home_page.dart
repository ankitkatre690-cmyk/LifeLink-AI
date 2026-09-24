import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/auth_state.dart';

class HomePage extends ConsumerWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('LifeLink AI'),
        actions: [
          IconButton(
            tooltip: 'Sign out',
            onPressed: () => ref.read(authProvider.notifier).logout(),
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: Center(
        child: Text(
          auth.role == 'pending'
              ? 'Authenticated — role loading'
              : 'Welcome to LifeLink AI',
          style: Theme.of(context).textTheme.headlineSmall,
        ),
      ),
    );
  }
}
