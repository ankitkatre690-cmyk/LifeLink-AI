import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/emergency_api.dart';
import '../../../core/network/api_client.dart';

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
  late final EmergencyApi _emergencyApi;
  StreamSubscription<RealtimeEvent>? _subscription;
  String _status = 'Pending';
  String _message = 'Waiting for emergency response updates.';
  bool _connected = false;
  final List<String> _updates = <String>[];
  List<Map<String, dynamic>> _timeline = <Map<String, dynamic>>[];
  bool _timelineLoading = true;
  bool _cancelling = false;

  bool get _isTerminal =>
      _status == 'Completed' || _status == 'Cancelled';

  @override
  void initState() {
    super.initState();
    _emergencyApi = EmergencyApi(ref.read(apiClientProvider));
    _loadEmergency();
    _loadTimeline();
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

  Future<void> _loadEmergency() async {
    try {
      final emergency = await _emergencyApi.getEmergency(widget.emergencyId);
      if (!mounted) return;
      final status = emergency['status']?.toString();
      if (status == null || status.isEmpty) return;
      setState(() {
        _status = status;
        _message = 'Emergency state synchronized with the server.';
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _message = 'Unable to synchronize emergency state. Live updates remain active.';
      });
    }
  }

  Future<void> _cancelEmergency() async {
    if (_cancelling || _isTerminal) return;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Cancel emergency?'),
        content: const Text(
          'Cancel this emergency only if you no longer need emergency assistance.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(false),
            child: const Text('Keep emergency'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(dialogContext).pop(true),
            child: const Text('Cancel emergency'),
          ),
        ],
      ),
    );

    if (confirmed != true || !mounted) return;

    setState(() => _cancelling = true);
    try {
      final emergency = await _emergencyApi.updateEmergencyStatus(
        emergencyId: widget.emergencyId,
        status: 'Cancelled',
        remarks: 'Cancelled by citizen from emergency tracking.',
      );
      if (!mounted) return;
      setState(() {
        _status = emergency['status']?.toString() ?? 'Cancelled';
        _message = 'Emergency cancelled successfully.';
      });
      await _loadTimeline();
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'The emergency could not be cancelled. It may already have an active responder assignment.',
          ),
        ),
      );
    } finally {
      if (mounted) setState(() => _cancelling = false);
    }
  }

  Future<void> _loadTimeline() async {
    try {
      final timeline = await _emergencyApi.getTimeline(widget.emergencyId);
      if (!mounted) return;
      setState(() {
        _timeline = timeline;
        _timelineLoading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() => _timelineLoading = false);
    }
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
              'Emergency timeline',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            if (_timelineLoading)
              const LinearProgressIndicator()
            else if (_timeline.isEmpty)
              const Text('No server timeline entries yet.')
            else
              ..._timeline.map(
                (item) => ListTile(
                  dense: true,
                  leading: const Icon(Icons.history),
                  title: Text(item['status']?.toString() ?? 'Status update'),
                  subtitle: Text(item['remarks']?.toString() ?? ''),
                ),
              ),
            if (_updates.isNotEmpty) ...[
              const SizedBox(height: 16),
              const Text(
                'Live updates',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              ..._updates.map(
                (update) => ListTile(
                  dense: true,
                  leading: const Icon(Icons.circle, size: 8),
                  title: Text(update),
                ),
              ),
            ],
            const SizedBox(height: 8),
            if (!_isTerminal) ...[
              const SizedBox(height: 16),
              OutlinedButton.icon(
                onPressed: _cancelling ? null : _cancelEmergency,
                icon: _cancelling
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.cancel_outlined),
                label: Text(
                  _cancelling ? 'Cancelling…' : 'Cancel Emergency',
                ),
              ),
            ] else ...[
              const SizedBox(height: 16),
              Card(
                child: ListTile(
                  leading: Icon(
                    _status == 'Completed'
                        ? Icons.check_circle_outline
                        : Icons.cancel_outlined,
                  ),
                  title: Text(
                    _status == 'Completed'
                        ? 'Emergency completed'
                        : 'Emergency cancelled',
                  ),
                  subtitle: const Text(
                    'No further emergency actions are available.',
                  ),
                ),
              ),
            ],
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
