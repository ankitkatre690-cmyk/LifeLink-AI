import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/realtime/realtime_provider.dart';
import '../../../core/realtime/websocket_service.dart';

class EmergencyTrackingPage extends ConsumerStatefulWidget {
  const EmergencyTrackingPage({required this.emergencyId, super.key});

  final String emergencyId;

  @override
  ConsumerState<EmergencyTrackingPage> createState() =>
      _EmergencyTrackingPageState();
}

class _EmergencyTrackingPageState
    extends ConsumerState<EmergencyTrackingPage> {
  StreamSubscription<RealtimeEvent>? _subscription;
  String _status = 'Pending';
  String _message = 'Waiting for emergency response updates.';
  bool _connected = false;
  final List<String> _updates = <String>[];

  @override
  void initState() {
    super.initState();
    _subscription = ref.read(realtimeServiceProvider).events.listen(
      _handleEvent,
      onError: (_) {
        if (!mounted) return;
        setState(() {
          _connected = false;
          _message = 'Live emergency connection was interrupted.';
        });
      },
    );
  }

  void _handleEvent(RealtimeEvent event) {
    final eventEmergencyId = event.data['emergency_id']?.toString();
    if (eventEmergencyId != null &&
        eventEmergencyId != widget.emergencyId) {
      return;
    }

    if (!mounted) return;

    setState(() {
      if (event.event == 'connected') {
        _connected = true;
      }

      final nextStatus = event.data['status']?.toString();
      if (nextStatus != null && nextStatus.isNotEmpty) {
        _status = nextStatus;
      }

      _message = _eventMessage(event.event);

      if (event.event != 'connected') {
        _updates.insert(0, _message);
        if (_updates.length > 5) {
          _updates.removeLast();
        }
      }
    });
  }

  String _eventMessage(String eventType) {
    switch (eventType) {
      case 'connected':
        return 'Live emergency channel connected.';
      case 'emergency.created':
        return 'Emergency registered. Waiting for response assignment.';
      case 'emergency.status_changed':
        return 'Emergency status updated.';
      case 'dispatch.assigned':
        return 'A responder has been assigned to your emergency.';
      case 'responder.assignment_status_changed':
        return 'Responder assignment status updated.';
      case 'dispatch.hospital_incoming':
        return 'Hospital coordination has been initiated.';
      default:
        return 'New emergency response update received.';
    }
  }

  @override
  void dispose() {
    _subscription?.cancel();
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
            Card(
              child: ListTile(
                leading: Icon(
                  _connected ? Icons.wifi : Icons.wifi_off,
                ),
                title: Text(
                  _connected
                      ? 'Live connection'
                      : 'Waiting for connection...',
                ),
                subtitle: Text(_message),
              ),
            ),
            const SizedBox(height: 16),
            Card(
              child: ListTile(
                leading: const Icon(Icons.emergency),
                title: const Text('Emergency status'),
                subtitle: Text(_status),
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Recent updates',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            if (_updates.isEmpty)
              const Text('No response updates received yet.')
            else
              ..._updates.map(
                (update) => ListTile(
                  dense: true,
                  leading: const Icon(Icons.circle, size: 8),
                  title: Text(update),
                ),
              ),
            const SizedBox(height: 8),
            const Text(
              'This screen uses the shared LifeLink realtime service. '
              'The API remains authoritative for emergency state.',
            ),
          ],
        ),
      ),
    );
  }
}
