import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/api_client.dart';
import '../../../core/realtime/realtime_client.dart';
import '../../../core/storage/secure_storage.dart';

class EmergencyTrackingPage extends ConsumerStatefulWidget {
  const EmergencyTrackingPage({required this.emergencyId, super.key});
  final String emergencyId;

  @override
  ConsumerState<EmergencyTrackingPage> createState() => _EmergencyTrackingPageState();
}

class _EmergencyTrackingPageState extends ConsumerState<EmergencyTrackingPage> {
  RealtimeClient? _client;
  StreamSubscription<Map<String, dynamic>>? _subscription;
  String _status = 'Pending';
  String _message = 'Waiting for emergency response updates.';
  bool _connected = false;

  @override
  void initState() {
    super.initState();
    _connect();
  }

  Future<void> _connect() async {
    final token = await const SecureStorage().readAccessToken();
    if (!mounted || token == null || token.isEmpty) {
      setState(() => _message = 'Your session token is unavailable.');
      return;
    }
    final client = RealtimeClient(
      baseUrl: ref.read(apiClientProvider).dio.options.baseUrl,
      accessToken: token,
    );
    _client = client;
    client.connect();
    _subscription = client.events.listen((event) {
      final data = event['data'];
      if (data is! Map) return;
      final eventEmergencyId = data['emergency_id']?.toString();
      if (eventEmergencyId != null && eventEmergencyId != widget.emergencyId) return;
      if (!mounted) return;
      final eventType = event['event']?.toString() ?? 'update';
      setState(() {
        _connected = eventType == 'connected' || _connected;
        _status = data['status']?.toString() ?? _status;
        _message = _eventMessage(eventType);
      });
    });
  }

  String _eventMessage(String eventType) {
    switch (eventType) {
      case 'connected': return 'Live emergency channel connected.';
      case 'emergency.created': return 'Emergency registered. Waiting for response assignment.';
      case 'emergency.status_changed': return 'Emergency status updated.';
      case 'dispatch.assigned': return 'A responder has been assigned to your emergency.';
      case 'responder.assignment_status_changed': return 'Responder assignment status updated.';
      case 'dispatch.hospital_incoming': return 'Hospital coordination has been initiated.';
      default: return 'New emergency response update received.';
    }
  }

  @override
  void dispose() {
    _subscription?.cancel();
    _client?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Emergency Tracking')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(child: ListTile(
              leading: Icon(_connected ? Icons.wifi : Icons.wifi_off),
              title: Text(_connected ? 'Live connection' : 'Connecting...'),
              subtitle: Text(_message),
            )),
            const SizedBox(height: 16),
            Card(child: ListTile(
              leading: const Icon(Icons.emergency),
              title: const Text('Emergency status'),
              subtitle: Text(_status),
            )),
            const SizedBox(height: 16),
            const Text('This screen receives updates from the existing LifeLink realtime service. It does not create or modify emergencies.'),
          ],
        ),
      ),
    );
  }
}
