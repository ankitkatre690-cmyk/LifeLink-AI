import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/realtime/realtime_provider.dart';
import '../../../core/realtime/websocket_service.dart';

class EmergencyConfirmationPage extends ConsumerStatefulWidget {
  const EmergencyConfirmationPage({
    required this.emergencyId,
    super.key,
  });

  final String emergencyId;

  @override
  ConsumerState<EmergencyConfirmationPage> createState() =>
      _EmergencyConfirmationPageState();
}

class _EmergencyConfirmationPageState
    extends ConsumerState<EmergencyConfirmationPage> {
  StreamSubscription<RealtimeEvent>? _subscription;
  String _status = 'Pending';
  String? _responderId;
  double? _etaMinutes;

  @override
  void initState() {
    super.initState();

    _subscription = ref.read(realtimeServiceProvider).events.listen(
      _handleEvent,
    );
  }

  void _handleEvent(RealtimeEvent event) {
    final eventEmergencyId = event.data['emergency_id']?.toString();
    if (eventEmergencyId != widget.emergencyId) return;

    if (event.event == 'emergency.status_changed' ||
        event.event == 'emergency.created') {
      final status = event.data['status']?.toString();
      if (status != null && mounted) {
        setState(() => _status = status);
      }
    }

    if (event.event == 'dispatch.assigned' && mounted) {
      setState(() {
        _status = event.data['status']?.toString() ?? 'Assigned';
        _responderId = event.data['responder_id']?.toString();
        _etaMinutes = (event.data['eta_minutes'] as num?)?.toDouble();
      });
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
      appBar: AppBar(title: const Text('Emergency status')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.emergency,
                size: 80,
                color: Theme.of(context).colorScheme.primary,
              ),
              const SizedBox(height: 20),
              Text(
                'Emergency request received',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 12),
              Text(
                'Emergency ID: ${widget.emergencyId}',
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              Card(
                child: ListTile(
                  leading: const Icon(Icons.sync),
                  title: const Text('Live status'),
                  subtitle: Text(_status),
                ),
              ),
              if (_responderId != null)
                Card(
                  child: ListTile(
                    leading: const Icon(Icons.directions_car),
                    title: const Text('Responder assigned'),
                    subtitle: Text(
                      _etaMinutes == null
                          ? 'Responder: ${_responderId!}'
                          : 'ETA: ${_etaMinutes!.toStringAsFixed(1)} minutes',
                    ),
                  ),
                ),
              const SizedBox(height: 12),
              const Text(
                'Updates are received in real time. Keep your phone available.',
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
