import 'package:flutter/material.dart';

class EmergencyConfirmationPage extends StatelessWidget {
  const EmergencyConfirmationPage({
    required this.emergencyId,
    super.key,
  });

  final String emergencyId;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Emergency status')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.check_circle_outline,
                size: 80,
                color: Theme.of(context).colorScheme.primary,
              ),
              const SizedBox(height: 20),
              Text(
                'Emergency request received',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 12),
              Text(
                'Emergency ID: $emergencyId',
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              const Text(
                'Keep your phone available for response updates.',
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
