import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/auth/auth_state.dart';
import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';

class LifeLinkApp extends ConsumerStatefulWidget {
  const LifeLinkApp({super.key});

  @override
  ConsumerState<LifeLinkApp> createState() => _LifeLinkAppState();
}

class _LifeLinkAppState extends ConsumerState<LifeLinkApp> {
  @override
  void initState() {
    super.initState();
    Future.microtask(
      () => ref.read(authProvider.notifier).restoreSession(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);

    return MaterialApp.router(
      title: 'LifeLink AI',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      routerConfig: buildAppRouter(auth),
    );
  }
}
