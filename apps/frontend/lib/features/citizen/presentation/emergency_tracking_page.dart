import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

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
  Timer? _responderAnimationTimer;
  String _status = 'Pending';
  String _message = 'Waiting for emergency response updates.';
  double? _emergencyLatitude;
  double? _emergencyLongitude;
  bool _connected = false;
  final List<String> _updates = <String>[];
  List<Map<String, dynamic>> _timeline = <Map<String, dynamic>>[];
  bool _timelineLoading = true;
  bool _cancelling = false;
  double? _responderLatitude;
  double? _responderLongitude;
  String? _responderAssignmentStatus;

  String get _trackingHeadline {
    switch (_responderAssignmentStatus) {
      case 'Assigned':
        return 'Responder assigned';
      case 'Accepted':
        return 'Responder accepted';
      case 'EnRoute':
        return 'Responder is on the way';
      case 'OnScene':
        return 'Responder is on scene';
      case 'Completed':
        return 'Response completed';
      case 'Cancelled':
        return 'Responder assignment cancelled';
      default:
        return 'Waiting for responder';
    }
  }

  IconData get _trackingIcon {
    switch (_responderAssignmentStatus) {
      case 'OnScene':
        return Icons.location_on;
      case 'Completed':
        return Icons.check_circle_outline;
      case 'Cancelled':
        return Icons.cancel_outlined;
      case 'EnRoute':
        return Icons.directions_car;
      case 'Accepted':
        return Icons.thumb_up_alt_outlined;
      case 'Assigned':
        return Icons.assignment_turned_in_outlined;
      default:
        return Icons.hourglass_top;
    }
  }
  DateTime? _responderLocationUpdatedAt;
  double? _displayedResponderLatitude;
  double? _displayedResponderLongitude;

  LatLng? get _mapCenter {
    if (_emergencyLatitude != null &&
        _emergencyLongitude != null &&
        _responderLatitude != null &&
        _responderLongitude != null) {
      return LatLng(
        (_emergencyLatitude! + _responderLatitude!) / 2,
        (_emergencyLongitude! + _responderLongitude!) / 2,
      );
    }
    if (_responderLatitude != null && _responderLongitude != null) {
      return LatLng(_responderLatitude!, _responderLongitude!);
    }
    if (_emergencyLatitude != null && _emergencyLongitude != null) {
      return LatLng(_emergencyLatitude!, _emergencyLongitude!);
    }
    return null;
  }

  double _mapZoomForDistance(double distanceKm) {
    if (distanceKm <= 0.5) return 15;
    if (distanceKm <= 1) return 14;
    if (distanceKm <= 3) return 13;
    if (distanceKm <= 7) return 12;
    if (distanceKm <= 15) return 11;
    if (distanceKm <= 30) return 10;
    if (distanceKm <= 60) return 9;
    return 8;
  }

  double get _mapZoom {
    final distance = _responderDistanceKm;
    return distance == null ? 15 : _mapZoomForDistance(distance);
  }

  double? get _responderDistanceKm {
    if (_emergencyLatitude == null ||
        _emergencyLongitude == null ||
        _responderLatitude == null ||
        _responderLongitude == null) {
      return null;
    }

    const earthRadiusKm = 6371.0;
    final lat1 = _emergencyLatitude! * math.pi / 180;
    final lat2 = _responderLatitude! * math.pi / 180;
    final deltaLat = (_responderLatitude! - _emergencyLatitude!) * math.pi / 180;
    final deltaLon = (_responderLongitude! - _emergencyLongitude!) * math.pi / 180;
    final haversine = math.pow(math.sin(deltaLat / 2), 2) +
        math.cos(lat1) *
            math.cos(lat2) *
            math.pow(math.sin(deltaLon / 2), 2);
    final centralAngle = 2 * math.atan2(math.sqrt(haversine), math.sqrt(1 - haversine));
    return earthRadiusKm * centralAngle;
  }

  String? get _estimatedArrival {
    final distanceKm = _responderDistanceKm;
    if (distanceKm == null) return null;
    // V1 estimate: straight-line distance at a conservative 30 km/h.
    final minutes = math.max(1, (distanceKm / 30 * 60).round());
    if (minutes < 60) return '~$minutes min estimated';
    final hours = minutes ~/ 60;
    final remainingMinutes = minutes % 60;
    return remainingMinutes == 0
        ? '~${hours}h estimated'
        : '~${hours}h ${remainingMinutes}m estimated';
  }

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
      _emergencyLatitude = (emergency['latitude'] as num?)?.toDouble();
      _emergencyLongitude = (emergency['longitude'] as num?)?.toDouble();
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

  void _animateResponderTo(double latitude, double longitude) {
    final startLatitude = _displayedResponderLatitude ?? latitude;
    final startLongitude = _displayedResponderLongitude ?? longitude;
    _responderAnimationTimer?.cancel();

    const durationMs = 700;
    const frameMs = 35;
    var elapsedMs = 0;

    void tick() {
      elapsedMs += frameMs;
      final progress = (elapsedMs / durationMs).clamp(0.0, 1.0);
      final eased = 1 - math.pow(1 - progress, 3);

      if (!mounted) return;
      setState(() {
        _displayedResponderLatitude =
            startLatitude + (latitude - startLatitude) * eased;
        _displayedResponderLongitude =
            startLongitude + (longitude - startLongitude) * eased;
      });

      if (progress >= 1.0) {
        _responderAnimationTimer?.cancel();
        return;
      }
    }

    tick();
    _responderAnimationTimer = Timer.periodic(
      const Duration(milliseconds: frameMs),
      (_) => tick(),
    );
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
      if (event.event == 'responder.location_updated') {
        final latitude = (event.data['latitude'] as num?)?.toDouble();
        final longitude = (event.data['longitude'] as num?)?.toDouble();
        _responderLatitude = latitude;
        _responderLongitude = longitude;
        if (latitude != null && longitude != null) {
          _animateResponderTo(latitude, longitude);
        }
        _responderAssignmentStatus = event.data['assignment_status']?.toString();
        _responderLocationUpdatedAt = DateTime.tryParse(event.timestamp ?? '');
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
      case 'responder.location_updated':
        return 'Responder location updated.';
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
            if (_responderAssignmentStatus != null) ...[
              Card(
                child: ListTile(
                  leading: Icon(_trackingIcon),
                  title: Text(_trackingHeadline),
                  subtitle: Text(
                    _responderAssignmentStatus!,
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],
            if (_responderLatitude != null && _responderLongitude != null) ...[
              const SizedBox(height: 16),
              Card(
                clipBehavior: Clip.antiAlias,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    SizedBox(
                      height: 220,
                      child: FlutterMap(
                        options: MapOptions(
                          initialCenter: _mapCenter!,
                          initialZoom: _mapZoom,
                        ),
                        children: [
                          TileLayer(
                            urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                            userAgentPackageName: 'com.lifelink.ai',
                          ),
                          MarkerLayer(
                            markers: [
                              if (_emergencyLatitude != null && _emergencyLongitude != null)
                                Marker(
                                  point: LatLng(_emergencyLatitude!, _emergencyLongitude!),
                                  width: 48,
                                  height: 48,
                                  child: const Icon(Icons.emergency, size: 36),
                                ),
                              Marker(
                                point: LatLng(
                                  _displayedResponderLatitude ?? _responderLatitude!,
                                  _displayedResponderLongitude ?? _responderLongitude!,
                                ),
                                width: 48,
                                height: 48,
                                child: const Icon(Icons.local_shipping, size: 36),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const ListTile(
                      leading: Icon(Icons.emergency_outlined),
                      title: Text('Emergency location'),
                      subtitle: Text('Emergency origin'),
                    ),
                    if (_responderDistanceKm != null)
                      ListTile(
                        leading: const Icon(Icons.route_outlined),
                        title: Text(
                          '${_responderDistanceKm!.toStringAsFixed(2)} km from emergency',
                        ),
                        subtitle: Text(
                          _estimatedArrival ?? 'Travel estimate unavailable',
                        ),
                      ),
                    ListTile(
                      leading: const Icon(Icons.location_on_outlined),
                      title: const Text('Responder location'),
                      subtitle: Text(
                        '${_responderLatitude!.toStringAsFixed(5)}, '
                        '${_responderLongitude!.toStringAsFixed(5)}'
                        '${_responderAssignmentStatus == null ? '' : ' • $_responderAssignmentStatus'}'
                        '${_responderLocationUpdatedAt == null ? '' : ' • Updated ${_responderLocationUpdatedAt!.toLocal().toString().substring(0, 19)}'}',
                      ),
                    ),
                    const Padding(
                      padding: EdgeInsets.fromLTRB(16, 0, 16, 12),
                      child: Text(
                        'Map data is provided by OpenStreetMap. Location updates are delivered through LifeLink realtime events.',
                      ),
                    ),
                  ],
                ),
              ),
            ],
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
