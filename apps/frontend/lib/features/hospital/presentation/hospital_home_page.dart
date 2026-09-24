import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/auth/auth_state.dart';
import '../../../core/network/api_client.dart';
import '../../../core/realtime/realtime_client.dart';
import '../../../core/storage/secure_storage.dart';
import '../data/hospital_api.dart';

final hospitalApiProvider = Provider<HospitalApi>((ref) => HospitalApi(ref.watch(apiClientProvider)));

class HospitalHomePage extends ConsumerStatefulWidget {
  const HospitalHomePage({super.key});
  @override
  ConsumerState<HospitalHomePage> createState() => _HospitalHomePageState();
}

class _HospitalHomePageState extends ConsumerState<HospitalHomePage> {
  bool _loading = true;
  String? _error;
  Map<String, dynamic>? _profile;
  List<Map<String, dynamic>> _resources = [];
  RealtimeClient? _realtime;
  StreamSubscription<Map<String, dynamic>>? _subscription;
  final List<String> _incoming = <String>[];
  bool _connected = false;

  @override
  void initState() {
    super.initState();
    Future.microtask(() async { await _load(); await _connectRealtime(); });
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final api = ref.read(hospitalApiProvider);
      final profile = await api.getMyProfile();
      _profile = profile;
      _resources = await api.getResources(profile['id'].toString());
    } on DioException catch (error) {
      if (mounted) setState(() => _error = error.response?.data is Map ? error.response?.data['detail']?.toString() : 'Unable to load hospital information.');
    } finally { if (mounted) setState(() => _loading = false); }
  }

  Future<void> _connectRealtime() async {
    final token = await const SecureStorage().readAccessToken();
    if (!mounted || token == null || token.isEmpty) return;
    final client = RealtimeClient(baseUrl: ref.read(apiClientProvider).dio.options.baseUrl, accessToken: token);
    _realtime = client;
    client.connect();
    _subscription = client.events.listen((event) {
      if (!mounted || event['event']?.toString() != 'dispatch.hospital_incoming') return;
      final data = event['data']; if (data is! Map) return;
      setState(() { _connected = true; _incoming.insert(0, 'Incoming emergency: ${data['emergency_id'] ?? 'Unknown'}'); if (_incoming.length > 5) _incoming.removeLast(); });
    });
  }

  Future<void> _editResource(Map<String, dynamic> resource) async {
    final total = TextEditingController(text: '${resource['total_count'] ?? 0}');
    final available = TextEditingController(text: '${resource['available_count'] ?? 0}');
    final values = await showDialog<List<String>>(context: context, builder: (context) => AlertDialog(
      title: Text(resource['resource_type']?.toString() ?? 'Resource'),
      content: Column(mainAxisSize: MainAxisSize.min, children: [
        TextField(controller: total, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Total')),
        TextField(controller: available, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Available')),
      ]),
      actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(context, [total.text, available.text]), child: const Text('Save'))],
    ));
    total.dispose(); available.dispose();
    if (values == null || !mounted) return;
    final totalCount = int.tryParse(values[0]); final availableCount = int.tryParse(values[1]);
    if (totalCount == null || availableCount == null || totalCount < 0 || availableCount < 0) return;
    try { await ref.read(hospitalApiProvider).updateResource(resourceId: resource['id'].toString(), totalCount: totalCount, availableCount: availableCount, isAvailable: availableCount > 0); await _load(); }
    on DioException catch (error) { if (mounted) setState(() => _error = error.response?.data is Map ? error.response?.data['detail']?.toString() : 'Unable to update hospital resource.'); }
  }

  @override
  void dispose() { _subscription?.cancel(); _realtime?.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('LifeLink AI'), actions: [IconButton(onPressed: _loading ? null : _load, icon: const Icon(Icons.refresh)), IconButton(onPressed: () => ref.read(authProvider.notifier).logout(), icon: const Icon(Icons.logout))]),
      body: RefreshIndicator(onRefresh: _load, child: ListView(padding: const EdgeInsets.all(20), children: [
        Text('Hospital Dashboard', style: Theme.of(context).textTheme.headlineSmall), Text('Role: ${auth.role ?? 'Hospital'}'), const SizedBox(height: 16),
        if (_error != null) Card(child: ListTile(leading: const Icon(Icons.error_outline), title: Text(_error!))),
        Card(child: ListTile(leading: Icon(_connected ? Icons.wifi : Icons.wifi_off), title: Text(_connected ? 'Live dispatch channel' : 'Dispatch channel'), subtitle: Text(_connected ? 'Listening for incoming emergencies.' : 'Connecting to hospital dispatch updates...'))),
        if (_incoming.isNotEmpty) ...[const SizedBox(height: 12), const Text('Incoming emergencies', style: TextStyle(fontWeight: FontWeight.bold)), ..._incoming.map((item) => Card(child: ListTile(leading: const Icon(Icons.local_hospital), title: Text(item))) )],
        const SizedBox(height: 12),
        if (_loading) const Padding(padding: EdgeInsets.all(32), child: Center(child: CircularProgressIndicator()))
        else if (_profile == null) const Card(child: ListTile(title: Text('Hospital profile not found'), subtitle: Text('Create the hospital profile before managing resources.')))
        else ...[Card(child: ListTile(leading: const Icon(Icons.local_hospital), title: Text(_profile!['name']?.toString() ?? 'Hospital'), subtitle: Text(_profile!['address']?.toString() ?? ''))), const SizedBox(height: 12), const Text('Resources', style: TextStyle(fontWeight: FontWeight.bold)), if (_resources.isEmpty) const Card(child: ListTile(title: Text('No resources configured.'))) else ..._resources.map((resource) => Card(child: ListTile(leading: const Icon(Icons.medical_services_outlined), title: Text(resource['resource_type']?.toString() ?? 'Resource'), subtitle: Text('Available: ${resource['available_count'] ?? 0} / ${resource['total_count'] ?? 0}'), trailing: IconButton(onPressed: () => _editResource(resource), icon: const Icon(Icons.edit)))))],
      ])),
    );
  }
}
