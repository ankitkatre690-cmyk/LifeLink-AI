import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/auth/auth_state.dart';
import '../../../core/network/api_client.dart';
import '../data/admin_api.dart';

final adminApiProvider = Provider<AdminApi>((ref) => AdminApi(ref.watch(apiClientProvider)));

class AdminHomePage extends ConsumerStatefulWidget {
  const AdminHomePage({super.key});
  @override
  ConsumerState<AdminHomePage> createState() => _AdminHomePageState();
}

class _AdminHomePageState extends ConsumerState<AdminHomePage> {
  bool _loading = true;
  String? _error;
  Map<String, dynamic>? _dashboard;
  List<Map<String, dynamic>> _users = [];

  @override
  void initState() {
    super.initState();
    Future.microtask(_load);
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final api = ref.read(adminApiProvider);
      final results = await Future.wait([api.getDashboard(), api.getUsers()]);
      _dashboard = results[0] as Map<String, dynamic>;
      _users = results[1] as List<Map<String, dynamic>>;
    } catch (e) {
      _error = 'Unable to load admin data.';
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _toggleUser(Map<String, dynamic> user) async {
    final id = user['id']?.toString();
    if (id == null) return;
    final active = user['is_active'] == true;
    try {
      await ref.read(adminApiProvider).updateUserStatus(id, !active);
      await _load();
    } catch (_) {
      if (mounted) setState(() => _error = 'Unable to update user status.');
    }
  }

  Widget _metric(String label, dynamic value, IconData icon) => Card(
    child: ListTile(
      leading: Icon(icon),
      title: Text(label),
      trailing: Text(
        value?.toString() ?? '0',
        style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
      ),
    ),
  );

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
            Text('Admin Dashboard', style: Theme.of(context).textTheme.headlineSmall),
            Text('Role: ${auth.role ?? 'Admin'}'),
            const SizedBox(height: 16),
            if (_error != null) Card(child: ListTile(
              leading: const Icon(Icons.error_outline),
              title: Text(_error!),
            )),
            if (_loading)
              const Padding(padding: EdgeInsets.all(32), child: Center(child: CircularProgressIndicator()))
            else ...[
              const Text('System Overview', style: TextStyle(fontWeight: FontWeight.bold)),
              _metric('Total Users', _dashboard?['users'], Icons.people),
              _metric('Active Users', _dashboard?['active_users'], Icons.person),
              _metric('Total Emergencies', _dashboard?['emergencies'], Icons.emergency),
              _metric('Active Emergencies', _dashboard?['active_emergencies'], Icons.warning),
              _metric('Responders', _dashboard?['responders'], Icons.directions_run),
              _metric('Available Responders', _dashboard?['available_responders'], Icons.check_circle),
              _metric('Hospitals', _dashboard?['hospitals'], Icons.local_hospital),
              _metric('Active Hospitals', _dashboard?['active_hospitals'], Icons.health_and_safety),
              _metric('Police Cases', _dashboard?['police_cases'], Icons.local_police),
              _metric('Open Police Cases', _dashboard?['open_police_cases'], Icons.assignment),
              const SizedBox(height: 20),
              const Text('User Management', style: TextStyle(fontWeight: FontWeight.bold)),
              ..._users.map((user) => Card(
                child: ListTile(
                  leading: Icon(user['is_active'] == true ? Icons.person : Icons.person_off),
                  title: Text(user['email']?.toString() ?? 'Unknown user'),
                  subtitle: Text('Phone: ${user['phone'] ?? '-'}\nRole ID: ${user['role_id'] ?? '-'}'),
                  isThreeLine: true,
                  trailing: Switch(
                    value: user['is_active'] == true,
                    onChanged: (_) => _toggleUser(user),
                  ),
                ),
              )),
            ],
          ],
        ),
      ),
    );
  }
}
