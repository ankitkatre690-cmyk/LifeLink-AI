import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../auth/auth_state.dart';
import '../../features/auth/presentation/login_page.dart';
import '../../features/citizen/presentation/citizen_dashboard_page.dart';
import '../../features/citizen/presentation/emergency_confirmation_page.dart';
import '../../features/home/presentation/home_page.dart';

GoRouter buildAppRouter(AuthState auth) {
  final isCitizen = auth.role == 'Citizen';

  return GoRouter(
    initialLocation: auth.isAuthenticated
        ? (isCitizen ? '/citizen' : '/home')
        : '/login',
    redirect: (context, state) {
      final isLogin = state.matchedLocation == '/login';

      if (auth.isLoading) return null;
      if (!auth.isAuthenticated && !isLogin) return '/login';
      if (auth.isAuthenticated && isLogin) {
        return isCitizen ? '/citizen' : '/home';
      }
      if (auth.isAuthenticated &&
          isCitizen &&
          (state.matchedLocation == '/home')) {
        return '/citizen';
      }

      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginPage(),
      ),
      GoRoute(
        path: '/home',
        builder: (context, state) => const HomePage(),
      ),
      GoRoute(
        path: '/citizen',
        builder: (context, state) => const CitizenDashboardPage(),
      ),
      GoRoute(
        path: '/citizen/emergency/:id',
        builder: (context, state) => EmergencyConfirmationPage(
          emergencyId: state.pathParameters['id']!,
        ),
      ),
    ],
  );
}
