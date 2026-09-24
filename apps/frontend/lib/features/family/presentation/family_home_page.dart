import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/auth_state.dart';
import '../../../core/network/api_client.dart';
import '../data/family_api.dart';

final familyApiProvider = Provider<FamilyApi>(
  (ref) => FamilyApi(ref.watch(apiClientProvider)),
);

class FamilyHomePage extends ConsumerStatefulWidget {
  const FamilyHomePage({super.key});

  @override
  ConsumerState<FamilyHomePage> createState() => _FamilyHomePageState();
}

class _FamilyHomePageState extends ConsumerState<FamilyHomePage> {
  bool _loading = true;
  String? _error;
  Map<String, dynamic>? _family;
  List<Map<String, dynamic>> _members = [];

  @override
  void initState() {
    super.initState();
    Future.microtask(_loadFamily);
  }

  Future<void> _loadFamily() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final api = ref.read(familyApiProvider);
      _family = await api.getFamily();
      _members = await api.getMembers();
    } on DioException catch (error) {
      if (!mounted) return;
      setState(() {
        _error = error.response?.data is Map
            ? error.response?.data['detail']?.toString()
            : 'Unable to load family information.';
      });
    } catch (_) {
      if (mounted) setState(() => _error = 'Unable to load family information.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _createFamily() async {
    final controller = TextEditingController();
    final name = await showDialog<String>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Create Family'),
        content: TextField(
          controller: controller,
          autofocus: true,
          decoration: const InputDecoration(labelText: 'Family name'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(dialogContext, controller.text.trim()),
            child: const Text('Create'),
          ),
        ],
      ),
    );
    controller.dispose();
    if (name == null || name.isEmpty || !mounted) return;
    try {
      await ref.read(familyApiProvider).createFamily(name);
      await _loadFamily();
    } on DioException catch (error) {
      if (mounted) {
        setState(() => _error = error.response?.data is Map
            ? error.response?.data['detail']?.toString()
            : 'Unable to create family.');
      }
    }
  }

  Future<void> _addMember() async {
    if (_family == null) return;
    final userIdController = TextEditingController();
    final relationshipController = TextEditingController();
    final values = await showDialog<List<String>>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Add Family Member'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: userIdController,
              decoration: const InputDecoration(labelText: 'User ID (UUID)'),
            ),
            TextField(
              controller: relationshipController,
              decoration: const InputDecoration(labelText: 'Relationship'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(
              dialogContext,
              [userIdController.text.trim(), relationshipController.text.trim()],
            ),
            child: const Text('Add'),
          ),
        ],
      ),
    );
    userIdController.dispose();
    relationshipController.dispose();
    if (values == null || values.length != 2 || !mounted) return;
    if (values[0].isEmpty || values[1].isEmpty) return;
    try {
      await ref.read(familyApiProvider).addMember(
            userId: values[0],
            relationship: values[1],
          );
      await _loadFamily();
    } on DioException catch (error) {
      if (mounted) {
        setState(() => _error = error.response?.data is Map
            ? error.response?.data['detail']?.toString()
            : 'Unable to add family member.');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('LifeLink AI'),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: _loading ? null : _loadFamily,
            icon: const Icon(Icons.refresh),
          ),
          IconButton(
            tooltip: 'Sign out',
            onPressed: () => ref.read(authProvider.notifier).logout(),
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadFamily,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Text('Family Dashboard', style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 8),
            Text('Role: ${auth.role ?? 'Family'}'),
            const SizedBox(height: 20),
            if (_error != null)
              Card(child: ListTile(
                leading: const Icon(Icons.error_outline),
                title: Text(_error!),
              )),
            if (_loading)
              const Padding(
                padding: EdgeInsets.all(32),
                child: Center(child: CircularProgressIndicator()),
              )
            else if (_family == null)
              Card(child: ListTile(
                leading: const Icon(Icons.family_restroom),
                title: const Text('No family created yet'),
                subtitle: const Text('Create a family group to manage emergency contacts.'),
                trailing: FilledButton(
                  onPressed: _createFamily,
                  child: const Text('Create'),
                ),
              ))
            else ...[
              Card(child: ListTile(
                leading: const Icon(Icons.family_restroom),
                title: Text(_family!['name']?.toString() ?? 'Family'),
                subtitle: Text('${_members.length} member(s)'),
                trailing: IconButton(
                  tooltip: 'Add member',
                  onPressed: _addMember,
                  icon: const Icon(Icons.person_add),
                ),
              )),
              const SizedBox(height: 12),
              if (_members.isEmpty)
                const Card(child: ListTile(
                  title: Text('No family members yet'),
                  subtitle: Text('Add members using their registered user UUID.'),
                ))
              else
                ..._members.map((member) => Card(child: ListTile(
                  leading: const Icon(Icons.person_outline),
                  title: Text(member['relationship']?.toString() ?? 'Member'),
                  subtitle: Text('User: ${member['user_id'] ?? 'Unknown'}'),
                  trailing: member['is_guardian'] == true
                      ? const Chip(label: Text('Guardian'))
                      : null,
                ))),
            ],
          ],
        ),
      ),
    );
  }
}
