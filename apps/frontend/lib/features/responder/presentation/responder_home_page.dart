import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/auth_state.dart';
import '../../../core/network/api_client.dart';
import '../../../core/realtime/realtime_client.dart';
import '../../../core/storage/secure_storage.dart';
import '../data/responder_api.dart';

final responderApiProvider = Provider<ResponderApi>(
  (ref) => ResponderApi(ref.watch(apiClientProvider)),
);

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
  RealtimeClient? _realtime;
  StreamSubscription<Map<String, dynamic>>? _realtimeSubscription;
  bool _realtimeConnected = false;

  @override
  void initState() {
    super.initState();
    Future.microtask(() async {
      await _load();
      await _connectRealtime();
    });
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      _profile = await ref.read(responderApiProvider).getMyProfile();
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

  Future<void> _connectRealtime() async {
    final token = await const SecureStorage().readAccessToken();
    if (!mounted || token == null || token.isEmpty) return;

    final client = RealtimeClient(
      baseUrl: ref.read(apiClientProvider).dio.options.baseUrl,
      accessToken: token,
    );
    _realtime = client;
    client.connect();
    _realtimeSubscription = client.events.listen((event) {
      if (!mounted) return;
      final type = event['event']?.toString() ?? '';
      final data = event['data'];
      if (type != 'dispatch.assignment' || data is! Map) return;
      final assignmentId = data['assignment_id']?.toString();
      if (assignmentId == null || assignmentId.isEmpty) return;

      setState(() {
        _realtimeConnected = true;
        _assignmentId = assignmentId;
        _assignment = {
          'id': assignmentId,
          'emergency_id': data['emergency_id'],
          'status': data['status'] ?? 'Assigned',
          'distance_km': data['distance_km'],
          'eta_minutes': data['eta_minutes'],
        };
      });
    });
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
      if (mounted) setState(() {});
    } on DioException catch (error) {
      if (mounted) setState(() => _error = error.response?.data is Map
          ? error.response?.data['detail']?.toString()
          : 'Unable to update responder status.');
    }
  }

  Future<void> _loadAssignment() async {
    final id = _assignmentId ?? _assignment?['id']?.toString();
    if (id == null || id.isEmpty) return;
    try {
      _assignment = await ref.read(responderApiProvider).getAssignment(id);
      if (mounted) setState(() {});
    } on DioException catch (error) {
      if (mounted) setState(() => _error = error.response?.data is Map
          ? error.response?.data['detail']?.toString()
          : 'Unable to load assignment.');
    }
  }

  Future<void> _updateAssignment() async {
    final id = _assignment?['id']?.toString();
    if (id == null) return;
    final status = await showDialog<String>(
      context: context,
      builder: (context) => SimpleDialog(
        title: const Text('Assignment status'),
        children: [
          for (final value in ['Accepted', 'EnRoute', 'OnScene', 'Completed', 'Cancelled'])
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
      if (mounted) setState(() {});
    } on DioException catch (error) {
      if (mounted) setState(() => _error = error.response?.data is Map
          ? error.response?.data['detail']?.toString()
          : 'Unable to update assignment.');
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
    _realtimeSubscription?.cancel();
    _realtime?.dispose();
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
              subtitle: Text(_realtimeConnected ? 'Waiting for new assignments.' : 'Connecting to dispatch updates...'),
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
                    onPressed: _updateAssignment,
                    child: const Text('Update'),
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
