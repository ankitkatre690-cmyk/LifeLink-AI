import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/location/location_service.dart';
import '../../../core/network/api_client.dart';
import '../data/emergency_api.dart';
import 'emergency_tracking_page.dart';

final emergencyApiProvider = Provider<EmergencyApi>(
  (ref) => EmergencyApi(ref.watch(apiClientProvider)),
);

class EmergencySosPage extends ConsumerStatefulWidget {
  const EmergencySosPage({super.key});

  @override
  ConsumerState<EmergencySosPage> createState() => _EmergencySosPageState();
}

class _EmergencySosPageState extends ConsumerState<EmergencySosPage> {
  bool _isSubmitting = false;
  String? _error;

  Future<void> _sendSos() async {
    if (_isSubmitting) return;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Confirm Emergency SOS'),
        content: const Text(
          'This will create an emergency using your current location and start the existing LifeLink response workflow.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(dialogContext).pop(true),
            child: const Text('Send SOS'),
          ),
        ],
      ),
    );

    if (confirmed != true || !mounted) return;

    setState(() {
      _isSubmitting = true;
      _error = null;
    });

    try {
      final position =
          await const LocationService().getCurrentEmergencyLocation();
      final emergency = await ref.read(emergencyApiProvider).createEmergency(
            emergencyType: 'GeneralSOS',
            latitude: position.latitude,
            longitude: position.longitude,
            description: 'Citizen emergency SOS',
          );

      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute<void>(
          builder: (_) => EmergencyTrackingPage(
            emergencyId: emergency['id'].toString(),
          ),
        ),
      );
    } on LocationServiceException catch (error) {
      if (mounted) setState(() => _error = error.message);
    } on DioException catch (error) {
      if (mounted) {
        final detail = error.response?.data is Map
            ? (error.response?.data['detail']?.toString() ??
                'Emergency request failed.')
            : 'Unable to contact the emergency service.';
        setState(() => _error = detail);
      }
    } catch (_) {
      if (mounted) {
        setState(() => _error = 'Unable to send SOS. Please try again.');
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Emergency SOS')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Icon(Icons.sos, size: 72),
          const SizedBox(height: 16),
          Text(
            'Emergency Assistance',
            style: Theme.of(context).textTheme.headlineSmall,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12),
          const Text(
            'Your current location will be sent to the existing emergency API after confirmation.',
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          if (_error != null) ...[
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Text(
                  _error!,
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.error,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],
          FilledButton.icon(
            onPressed: _isSubmitting ? null : _sendSos,
            icon: _isSubmitting
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.emergency),
            label: Text(
              _isSubmitting ? 'Sending SOS...' : 'Send Emergency SOS',
            ),
          ),
        ],
      ),
    );
  }
}
