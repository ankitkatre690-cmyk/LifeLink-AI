import 'dart:async';

import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/auth_state.dart';
import '../../../core/notifications/push_notification_service.dart';
import 'emergency_sos_page.dart';

class CitizenHomePage extends ConsumerStatefulWidget {
  const CitizenHomePage({super.key});

  @override
  ConsumerState<CitizenHomePage> createState() => _CitizenHomePageState();
}

class _CitizenHomePageState extends ConsumerState<CitizenHomePage> {
  StreamSubscription<RemoteMessage>? _notificationSubscription;

  @override
  void initState() {
    super.initState();
    Future.microtask(_listenForNotifications);
  }

  void _listenForNotifications() {
    final service = ref.read(pushNotificationServiceProvider);
    _notificationSubscription = service.foregroundMessages.listen((message) {
      if (!mounted) return;

      final title = message.notification?.title ?? 'LifeLink AI';
      final body = message.notification?.body ?? 'New emergency update received.';

      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          SnackBar(
            content: Text('$title: $body'),
            duration: const Duration(seconds: 5),
          ),
        );
    });
  }

  @override
  void dispose() {
    _notificationSubscription?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
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
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text('Citizen Dashboard', style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 8),
          Text('Role: ${auth.role ?? 'Citizen'}'),
          const SizedBox(height: 24),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Icon(Icons.emergency_share_outlined, size: 52),
                  const SizedBox(height: 12),
                  Text(
                    'Emergency Assistance',
                    style: Theme.of(context).textTheme.titleLarge,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Send an SOS with your current location through the existing emergency workflow.',
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 20),
                  FilledButton.icon(
                    onPressed: () => Navigator.of(context).push(
                      MaterialPageRoute<void>(
                        builder: (_) => const EmergencySosPage(),
                      ),
                    ),
                    icon: const Icon(Icons.sos),
                    label: const Text('Emergency SOS'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          const Card(
            child: ListTile(
              leading: Icon(Icons.family_restroom_outlined),
              title: Text('Family Safety'),
              subtitle: Text('Family alerts and emergency updates will appear here.'),
            ),
          ),
          const Card(
            child: ListTile(
              leading: Icon(Icons.notifications_active_outlined),
              title: Text('Notifications'),
              subtitle: Text('Emergency and response notifications will appear here.'),
            ),
          ),
        ],
      ),
    );
  }
}
