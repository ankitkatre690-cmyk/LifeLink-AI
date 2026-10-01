import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../auth/auth_state.dart';
import '../../features/auth/presentation/login_page.dart';
import '../../features/citizen/presentation/emergency_sos_page.dart';
import '../../features/citizen/presentation/emergency_tracking_page.dart';
import '../../features/role/presentation/role_router_page.dart';

GoRouter buildAppRouter(AuthState auth) {
  return GoRouter(
    initialLocation: auth.isAuthenticated ? '/home' : '/login',
    redirect: (context, state) {
      final isLogin = state.matchedLocation == '/login';
      if (auth.isLoading) return null;
      if (!auth.isAuthenticated && !isLogin) return '/login';
      if (auth.isAuthenticated && isLogin) return '/home';
      return null;
    },
    routes: [
      GoRoute(path: '/login', builder: (context, state) => const LoginPage()),
      GoRoute(
        path: '/home',
        builder: (context, state) => RoleRouterPage(role: auth.role ?? ''),
      ),
      GoRoute(
        path: '/citizen/emergency-sos',
        builder: (context, state) => const EmergencySosPage(),
      ),
      GoRoute(
        path: '/citizen/emergency/:emergencyId',
        builder: (context, state) {
          final emergencyId = state.pathParameters['emergencyId'];
          if (emergencyId == null || emergencyId.isEmpty) {
            return const Scaffold(
              body: Center(child: Text('Emergency ID is missing.')),
            );
          }
          return EmergencyTrackingPage(emergencyId: emergencyId);
        },
      ),
    ],
  );
}
