import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/auth_state.dart';
import '../../../core/network/api_client.dart';
import '../data/police_api.dart';

final policeApiProvider = Provider<PoliceApi>(
  (ref) => PoliceApi(ref.watch(apiClientProvider)),
);

class PoliceHomePage extends ConsumerStatefulWidget {
  const PoliceHomePage({super.key});

  @override
  ConsumerState<PoliceHomePage> createState() => _PoliceHomePageState();
}

class _PoliceHomePageState extends ConsumerState<PoliceHomePage> {
  bool _loading = true;
  String? _error;
  List<Map<String, dynamic>> _emergencies = [];
  Map<String, dynamic>? _selectedCase;

  @override
  void initState() {
    super.initState();
    Future.microtask(_load);
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      _emergencies = await ref.read(policeApiProvider).getActiveEmergencies();
    } on DioException catch (error) {
      if (mounted) {
        setState(() => _error = error.response?.data is Map
            ? error.response?.data['detail']?.toString()
            : 'Unable to load active emergencies.');
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _openEmergency(Map<String, dynamic> emergency) async {
    final emergencyId = emergency['id']?.toString();
    if (emergencyId == null) return;
    final notesController = TextEditingController();
    final create = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Open Police Case'),
        content: TextField(
          controller: notesController,
          maxLines: 3,
          decoration: const InputDecoration(labelText: 'Notes (optional)'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Open Case')),
        ],
      ),
    );
    if (create != true || !mounted) {
      notesController.dispose();
      return;
    }
    try {
      _selectedCase = await ref.read(policeApiProvider).createCase(
        emergencyId,
        notes: notesController.text.trim(),
      );
      if (mounted) setState(() {});
    } on DioException catch (error) {
      if (mounted) setState(() => _error = error.response?.data is Map
          ? error.response?.data['detail']?.toString()
          : 'Unable to create police case.');
    } finally {
      notesController.dispose();
    }
  }

  Future<void> _updateCase() async {
    final caseData = _selectedCase;
    if (caseData == null) return;
    final caseId = caseData['id']?.toString();
    if (caseId == null) return;
    final status = await showDialog<String>(
      context: context,
      builder: (context) => SimpleDialog(
        title: const Text('Case status'),
        children: [
          for (final value in ['Open', 'InProgress', 'Closed', 'Cancelled'])
            SimpleDialogOption(
              onPressed: () => Navigator.pop(context, value),
              child: Text(value),
            ),
        ],
      ),
    );
    if (status == null) return;
    try {
      _selectedCase = await ref.read(policeApiProvider).updateCase(
        caseId,
        status: status,
        notes: caseData['notes']?.toString(),
      );
      if (mounted) setState(() {});
    } on DioException catch (error) {
      if (mounted) setState(() => _error = error.response?.data is Map
          ? error.response?.data['detail']?.toString()
          : 'Unable to update police case.');
    }
  }

  Future<void> _dispatch() async {
    final emergencyId = _selectedCase?['emergency_id']?.toString();
    if (emergencyId == null) return;
    try {
      await ref.read(policeApiProvider).dispatch(emergencyId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Dispatch request submitted.')),
        );
      }
    } on DioException catch (error) {
      if (mounted) setState(() => _error = error.response?.data is Map
          ? error.response?.data['detail']?.toString()
          : 'Unable to dispatch responder.');
    }
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
            Text('Police Dashboard', style: Theme.of(context).textTheme.headlineSmall),
            Text('Role: ${auth.role ?? 'Police'}'),
            const SizedBox(height: 16),
            if (_error != null)
              Card(child: ListTile(
                leading: const Icon(Icons.error_outline),
                title: Text(_error!),
              )),
            if (_selectedCase != null)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text('Selected Police Case', style: TextStyle(fontWeight: FontWeight.bold)),
                      Text('Emergency: ${_selectedCase!['emergency_id'] ?? 'Unknown'}'),
                      Text('Status: ${_selectedCase!['case_status'] ?? 'Unknown'}'),
                      const SizedBox(height: 12),
                      Wrap(
                        spacing: 8,
                        children: [
                          OutlinedButton(onPressed: _updateCase, child: const Text('Update Case')),
                          FilledButton.icon(onPressed: _dispatch, icon: const Icon(Icons.send), label: const Text('Dispatch')),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            const SizedBox(height: 12),
            const Text('Active Emergencies', style: TextStyle(fontWeight: FontWeight.bold)),
            if (_loading)
              const Padding(
                padding: EdgeInsets.all(32),
                child: Center(child: CircularProgressIndicator()),
              )
            else if (_emergencies.isEmpty)
              const Card(child: ListTile(
                leading: Icon(Icons.check_circle_outline),
                title: Text('No active emergencies'),
              ))
            else
              ..._emergencies.map((emergency) => Card(
                    child: ListTile(
                      leading: const Icon(Icons.emergency),
                      title: Text(emergency['emergency_type']?.toString() ?? 'Emergency'),
                      subtitle: Text(
                        'Severity: ${emergency['severity'] ?? '-'}\n'
                        'Status: ${emergency['status'] ?? '-'}\n'
                        'Location: ${emergency['latitude'] ?? '-'}, ${emergency['longitude'] ?? '-'}',
                      ),
                      isThreeLine: true,
                      trailing: FilledButton(
                        onPressed: () => _openEmergency(emergency),
                        child: const Text('Case'),
                      ),
                    ),
                  )),
          ],
        ),
      ),
    );
  }
}
