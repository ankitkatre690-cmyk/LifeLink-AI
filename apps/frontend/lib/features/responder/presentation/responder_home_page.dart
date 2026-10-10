import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/location/location_service.dart';

import '../../../core/auth/auth_state.dart';
import '../../../core/network/api_client.dart';
import '../../../core/realtime/realtime_provider.dart';
import '../../../core/realtime/websocket_service.dart';
import '../data/responder_api.dart';
import '../../notifications/presentation/notification_inbox_page.dart';

List<String> nextResponderAssignmentStatuses(String current) {
  switch (current) {
    case 'Assigned':
      return const ['Accepted', 'Cancelled'];
    case 'Accepted':
      return const ['EnRoute', 'Cancelled'];
    case 'EnRoute':
      return const ['OnScene', 'Cancelled'];
    case 'OnScene':
      return const ['Completed', 'Cancelled'];
    default:
      return const [];
  }
}

final responderApiProvider = Provider<ResponderApi>(
  (ref) => ResponderApi(ref.watch(apiClientProvider)),
);

Map<String, dynamic>? responderAssignmentFromRealtimeEvent(
  RealtimeEvent event,
) {
  if (event.event != 'dispatch.assignment') return null;
  final assignmentId = event.data['assignment_id']?.toString();
  if (assignmentId == null || assignmentId.isEmpty) return null;
  return {
    'id': assignmentId,
    'emergency_id': event.data['emergency_id'],
    'status': event.data['status'] ?? 'Assigned',
    'distance_km': event.data['distance_km'],
    'eta_minutes': event.data['eta_minutes'],
  };
}

class ResponderHomePage extends ConsumerStatefulWidget {
  const ResponderHomePage({super.key});

  @override
  ConsumerState<ResponderHomePage> createState() => _ResponderHomePageState();
}

class _ResponderHomePageState extends ConsumerState<ResponderHomePage> {
  bool _loading = true;
  String? _error;
  Map<String, dynamic>? _profile;
  Map<String, dynamic>? _assignment;
  String? _assignmentId;
  StreamSubscription<RealtimeEvent>? _realtimeSubscription;
  bool _realtimeConnected = false;
  bool _realtimeSyncing = false;
  Timer? _locationTimer;
  bool _locationUpdating = false;

  @override
  void initState() {
    super.initState();
    Future.microtask(() async {
      await _load();
      await _connectRealtime();
      if (_profile != null) {
        await _updateLocation();
        _startLocationUpdates();
      }
    });
  }

  Future<void> _load() async {
    if (!mounted) return;
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      _profile = await ref.read(responderApiProvider).getMyProfile();
      _assignment = await ref.read(responderApiProvider).getActiveAssignment();
      _assignmentId = _assignment?['id']?.toString();
    } on DioException catch (error) {
      if (mounted) {
        setState(() => _error = error.response?.data is Map
            ? error.response?.data['detail']?.toString()
            : 'Unable to load responder profile.');
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _startLocationUpdates() {
    _locationTimer?.cancel();
    _locationTimer = Timer.periodic(
      const Duration(seconds: 60),
      (_) => _updateLocation(),
    );
  }

  Future<void> _updateLocation() async {
    if (_profile == null || _locationUpdating) return;
    _locationUpdating = true;
    try {
      final position = await LocationService().getCurrentPosition();
      final updated = await ref.read(responderApiProvider).updateLocation(
        position.latitude,
        position.longitude,
      );
      if (!mounted) return;
      setState(() {
        _profile = updated;
        _error = null;
      });
    } on LocationException catch (error) {
      if (mounted && _profile != null) {
        setState(() => _error = error.message);
      }
    } on DioException catch (error) {
      if (mounted && _profile != null) {
        setState(() => _error = error.response?.data is Map
            ? error.response?.data['detail']?.toString()
            : 'Unable to update responder location.');
      }
    } finally {
      _locationUpdating = false;
    }
  }

  Future<void> _connectRealtime() async {
    final service = ref.read(realtimeServiceProvider);
    if (!mounted) return;
    setState(() => _realtimeConnected = service.isConnected);
    _realtimeSubscription = service.events.listen(
      (event) {
        if (!mounted) return;
        if (event.event == 'connected') {
          setState(() => _realtimeConnected = true);
          unawaited(_refreshAssignmentAfterReconnect());
          return;
        }
        if (event.event == 'responder.assignment_status_changed') {
          final assignmentId = event.data['assignment_id']?.toString();
          final status = event.data['status']?.toString();
          if (assignmentId == null || assignmentId.isEmpty || status == null) {
            return;
          }
          setState(() {
            _realtimeConnected = true;
            _assignmentId = assignmentId;
            _assignment = {
              ...?_assignment,
              'id': assignmentId,
              'emergency_id': event.data['emergency_id'] ?? _assignment?['emergency_id'],
              'status': status,
              'notes': event.data['notes'],
            };
            _error = null;
          });
          return;
        }
        if (event.event != 'dispatch.assignment') return;

        final assignmentId = event.data['assignment_id']?.toString();
        if (assignmentId == null || assignmentId.isEmpty) return;

        setState(() {
          _realtimeConnected = true;
          _assignmentId = assignmentId;
          _assignment = {
            'id': assignmentId,
            'emergency_id': event.data['emergency_id'],
            'status': event.data['status'] ?? 'Assigned',
            'distance_km': event.data['distance_km'],
            'eta_minutes': event.data['eta_minutes'],
          };
          _error = null;
        });
      },
      onError: (_) {
        if (!mounted) return;
        setState(() {
          _realtimeConnected = false;
          _error = 'Live dispatch connection was interrupted.';
        });
      },
      onDone: () {
        if (!mounted) return;
        setState(() => _realtimeConnected = false);
      },
    );
  }

  Future<void> _refreshAssignmentAfterReconnect() async {
    if (_realtimeSyncing || !mounted) return;
    _realtimeSyncing = true;
    try {
      final assignment = await ref.read(responderApiProvider).getActiveAssignment();
      if (!mounted) return;
      setState(() {
        _assignment = assignment;
        _assignmentId = assignment?['id']?.toString();
        _error = null;
      });
    } on DioException catch (error) {
      if (!mounted) return;
      setState(() {
        _error = error.response?.data is Map
            ? error.response?.data['detail']?.toString()
            : 'Unable to synchronize active assignment.';
      });
    } finally {
      _realtimeSyncing = false;
    }
  }

  Future<void> _changeStatus() async {
    final status = await showDialog<String>(
      context: context,
      builder: (context) => SimpleDialog(
        title: const Text('Responder status'),
        children: [
          for (final value in ['Available', 'Busy', 'Offline'])
            SimpleDialogOption(
              onPressed: () => Navigator.pop(context, value),
              child: Text(value),
            ),
        ],
      ),
    );
    if (status == null) return;
    try {
      _profile = await ref.read(responderApiProvider).updateStatus(status);
      if (mounted) {
        setState(() {});
      }
    } on DioException catch (error) {
      if (mounted) {
        setState(() => _error = error.response?.data is Map
            ? error.response?.data['detail']?.toString()
            : 'Unable to update responder status.');
      }
    }
  }

  Future<void> _loadAssignment() async {
    final id = _assignmentId ?? _assignment?['id']?.toString();
    if (id == null || id.isEmpty) return;
    try {
      _assignment = await ref.read(responderApiProvider).getAssignment(id);
      _error = null;
      if (mounted) {
        setState(() {});
      }
    } on DioException catch (error) {
      if (mounted) {
        setState(() => _error = error.response?.data is Map
            ? error.response?.data['detail']?.toString()
            : 'Unable to load assignment.');
      }
    }
  }


  Future<void> _updateAssignment() async {
    final id = _assignment?['id']?.toString();
    if (id == null) {
      return;
    }
    final currentStatus = _assignment?['status']?.toString() ?? '';
    final nextStatuses = nextResponderAssignmentStatuses(currentStatus);
    if (nextStatuses.isEmpty) return;

    final status = await showDialog<String>(
      context: context,
      builder: (context) => SimpleDialog(
        title: Text('Next status • $currentStatus'),
        children: [
          for (final value in nextStatuses)
            SimpleDialogOption(
              onPressed: () => Navigator.pop(context, value),
              child: Text(value),
            ),
        ],
      ),
    );
    if (status == null) return;
    try {
      _assignment = await ref.read(responderApiProvider).updateAssignment(id, status);
      _error = null;
      if (mounted) {
        setState(() {});
      }
    } on DioException catch (error) {
      if (mounted) {
        setState(() => _error = error.response?.data is Map
            ? error.response?.data['detail']?.toString()
            : 'Unable to update assignment.');
      }
    }
  }

  void _setAssignmentId() {
    final controller = TextEditingController();
    showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Load assignment'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(labelText: 'Assignment UUID'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              _assignmentId = controller.text.trim();
              Navigator.pop(context);
              _loadAssignment();
            },
            child: const Text('Load'),
          ),
        ],
      ),
    ).whenComplete(controller.dispose);
  }

  @override
  void dispose() {
    _locationTimer?.cancel();
    _realtimeSubscription?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('LifeLink AI'),
        actions: [
          IconButton(onPressed: _loading ? null : _load, icon: const Icon(Icons.refresh)),
          IconButton(onPressed: () => ref.read(authProvider.notifier).logout(), icon: const Icon(Icons.logout)),
          IconButton(
            tooltip: 'Notifications',
            onPressed: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const NotificationInboxPage())),
            icon: const Icon(Icons.notifications_outlined),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Text('Responder Dashboard', style: Theme.of(context).textTheme.headlineSmall),
            Text('Role: ${auth.role ?? 'Responder'}'),
            const SizedBox(height: 16),
            Card(child: ListTile(
              leading: Icon(_realtimeConnected ? Icons.wifi : Icons.wifi_off),
              title: Text(_realtimeConnected ? 'Live dispatch channel' : 'Dispatch channel'),
              subtitle: Text(_realtimeConnected
                  ? (_realtimeSyncing ? 'Synchronizing active assignment...' : 'Waiting for new assignments.')
                  : 'Connecting to dispatch updates...'),
            )),
            const SizedBox(height: 8),
            if (_error != null) Card(child: ListTile(
              leading: const Icon(Icons.error_outline),
              title: Text(_error!),
            )),
            if (_loading)
              const Padding(
                padding: EdgeInsets.all(32),
                child: Center(child: CircularProgressIndicator()),
              )
            else if (_profile == null)
              const Card(child: ListTile(
                title: Text('Responder profile not found'),
                subtitle: Text('Create the responder profile before using dispatch features.'),
              ))
            else ...[
              Card(child: ListTile(
                leading: const Icon(Icons.badge_outlined),
                title: Text(_profile!['responder_type']?.toString() ?? 'Responder'),
                subtitle: Text('Status: ${_profile!['status'] ?? 'Unknown'}'),
                trailing: FilledButton(
                  onPressed: _changeStatus,
                  child: const Text('Status'),
                ),
              )),
              Card(child: ListTile(
                leading: const Icon(Icons.local_shipping_outlined),
                title: Text(_profile!['vehicle_number']?.toString() ?? 'No vehicle'),
                subtitle: Text('Location: ${_profile!['latitude'] ?? '-'}, ${_profile!['longitude'] ?? '-'}'),
              )),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Assignment', style: TextStyle(fontWeight: FontWeight.bold)),
                  TextButton.icon(onPressed: _setAssignmentId, icon: const Icon(Icons.search), label: const Text('Load')),
                ],
              ),
              if (_assignment == null)
                const Card(child: ListTile(
                  title: Text('No assignment loaded'),
                  subtitle: Text('Dispatch assignment details will appear here.'),
                ))
              else
                Card(child: ListTile(
                  leading: const Icon(Icons.emergency),
                  title: Text('Emergency: ${_assignment!['emergency_id'] ?? 'Unknown'}'),
                  subtitle: Text('Status: ${_assignment!['status'] ?? 'Unknown'}'),
                  trailing: FilledButton(
                    onPressed: nextResponderAssignmentStatuses(
                      _assignment!['status']?.toString() ?? '',
                    ).isEmpty
                        ? null
                        : _updateAssignment,
                    child: Text(
                      nextResponderAssignmentStatuses(
                        _assignment!['status']?.toString() ?? '',
                      ).isEmpty
                          ? 'Terminal'
                          : 'Update',
                    ),
                  ),
                )),
              if (_assignment != null)
                TextButton.icon(
                  onPressed: _loadAssignment,
                  icon: const Icon(Icons.refresh),
                  label: const Text('Refresh assignment'),
                ),
            ],
          ],
        ),
      ),
    );
  }
}
