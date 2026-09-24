import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/auth/auth_state.dart';
import '../data/emergency_repository.dart';

final emergencyRepositoryProvider = Provider<EmergencyRepository>(
  (ref) => EmergencyRepository(ref.read(apiClientProvider)),
);

class CitizenDashboardPage extends ConsumerStatefulWidget {
  const CitizenDashboardPage({super.key});

  @override
  ConsumerState<CitizenDashboardPage> createState() =>
      _CitizenDashboardPageState();
}

class _CitizenDashboardPageState
    extends ConsumerState<CitizenDashboardPage> {
  bool _isSending = false;

  Future<void> _sendEmergency() async {
    if (_isSending) return;

    setState(() => _isSending = true);

    try {
      // Real GPS is connected in the location-service increment.
      // Do not treat these placeholder coordinates as production location.
      final emergency = await ref
          .read(emergencyRepositoryProvider)
          .createEmergency(
            emergencyType: 'GeneralEmergency',
            severity: 'High',
            latitude: 0,
            longitude: 0,
            description: 'Citizen emergency SOS initiated from the app.',
          );

      if (!mounted) return;

      await showDialog<void>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Emergency created'),
          content: Text(
            'Emergency ID: ${emergency['id'] ?? 'created'}',
          ),
          actions: [
            FilledButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('OK'),
            ),
          ],
        ),
      );
    } catch (_) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Emergency could not be created. Please try again.',
          ),
        ),
      );
    } finally {
      if (mounted) setState(() => _isSending = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Citizen Dashboard'),
        actions: [
          IconButton(
            tooltip: 'Sign out',
            onPressed: () => ref.read(authProvider.notifier).logout(),
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            'Emergency assistance',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          const Text(
            'Use SOS when you need emergency assistance. '
            'Location integration will be connected before production use.',
          ),
          const SizedBox(height: 24),
          SizedBox(
            height: 64,
            child: FilledButton.icon(
              onPressed: _isSending ? null : _sendEmergency,
              icon: const Icon(Icons.sos),
              label: Text(_isSending ? 'Sending…' : 'EMERGENCY SOS'),
            ),
          ),
          const SizedBox(height: 16),
          const Card(
            child: ListTile(
              leading: Icon(Icons.family_restroom),
              title: Text('Family alerts'),
              subtitle: Text(
                'Family notification integration follows the emergency pipeline.',
              ),
            ),
          ),
          const Card(
            child: ListTile(
              leading: Icon(Icons.local_hospital_outlined),
              title: Text('Emergency response'),
              subtitle: Text(
                'Responder and hospital coordination is handled by the backend.',
              ),
            ),
          ),
        ],
      ),
    );
  }
}
