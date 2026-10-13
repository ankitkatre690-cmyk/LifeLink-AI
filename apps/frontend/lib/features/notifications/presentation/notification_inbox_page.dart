import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/auth_state.dart';
import '../../../core/network/api_client.dart';
import '../data/notification_api.dart';

final notificationApiProvider = Provider<NotificationApi>(
  (ref) => NotificationApi(ref.watch(apiClientProvider)),
);

class NotificationInboxPage extends ConsumerStatefulWidget {
  const NotificationInboxPage({super.key});

  @override
  ConsumerState<NotificationInboxPage> createState() => _NotificationInboxPageState();
}

class _NotificationInboxPageState extends ConsumerState<NotificationInboxPage> {
  bool _loading = true;
  String? _error;
  List<Map<String, dynamic>> _notifications = [];

  int get _unreadCount => _notifications.where((n) => n['is_read'] != true).length;

  @override
  void initState() {
    super.initState();
    Future.microtask(_load);
  }

  Future<void> _load() async {
    if (!mounted) return;
    setState(() { _loading = true; _error = null; });
    try {
      _notifications = await ref.read(notificationApiProvider).listNotifications();
    } on DioException catch (error) {
      if (mounted) {
        setState(() => _error = error.response?.data is Map
            ? error.response?.data['detail']?.toString()
            : 'Unable to load notifications.');
      }
    } catch (_) {
      if (mounted) setState(() => _error = 'Unable to load notifications.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _markRead(String id) async {
    try {
      final updated = await ref.read(notificationApiProvider).markRead(id);
      if (!mounted) return;
      final index = _notifications.indexWhere((n) => n['id']?.toString() == id);
      if (index != -1) setState(() => _notifications[index] = updated);
    } on DioException catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(error.response?.data is Map
            ? error.response?.data['detail']?.toString() ?? 'Unable to update notification.'
            : 'Unable to update notification.')),
      );
    }
  }

  IconData _icon(String? type) {
    switch (type) {
      case 'Emergency': return Icons.emergency_outlined;
      case 'Dispatch': return Icons.local_shipping_outlined;
      case 'Hospital': return Icons.local_hospital_outlined;
      case 'Police': return Icons.local_police_outlined;
      case 'Family': return Icons.family_restroom_outlined;
      default: return Icons.notifications_outlined;
    }
  }

  @override
  Widget build(BuildContext context) {
    final role = ref.watch(authProvider).role ?? 'User';
    return Scaffold(
      appBar: AppBar(
        title: Text(_unreadCount == 0 ? 'Notifications' : 'Notifications ($_unreadCount)'),
        actions: [IconButton(onPressed: _loading ? null : _load, icon: const Icon(Icons.refresh))],
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text('LifeLink AI • $role', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            if (_error != null) Card(child: ListTile(leading: const Icon(Icons.error_outline), title: Text(_error!))),
            if (_loading)
              const Padding(padding: EdgeInsets.all(32), child: Center(child: CircularProgressIndicator()))
            else if (_notifications.isEmpty)
              const Card(child: ListTile(leading: Icon(Icons.notifications_none), title: Text('No notifications'), subtitle: Text('Emergency and response updates will appear here.')))
            else
              ..._notifications.map((n) => Card(child: ListTile(
                leading: Icon(_icon(n['notification_type']?.toString())),
                title: Text(n['title']?.toString() ?? 'LifeLink AI'),
                subtitle: Text(n['message']?.toString() ?? ''),
                trailing: n['is_read'] == true ? const Icon(Icons.check_circle_outline) : const Icon(Icons.mark_email_unread_outlined),
                onTap: n['is_read'] == true ? null : () => _markRead(n['id'].toString()),
              ))),
          ],
        ),
      ),
    );
  }
}
