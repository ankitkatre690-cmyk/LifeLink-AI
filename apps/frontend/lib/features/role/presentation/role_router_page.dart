import 'package:flutter/material.dart';

import '../../admin/presentation/admin_home_page.dart';
import '../../citizen/presentation/citizen_home_page.dart';
import '../../family/presentation/family_home_page.dart';
import '../../hospital/presentation/hospital_home_page.dart';
import '../../police/presentation/police_home_page.dart';
import '../../responder/presentation/responder_home_page.dart';

class RoleRouterPage extends StatelessWidget {
  const RoleRouterPage({super.key, required this.role});
  final String role;

  @override
  Widget build(BuildContext context) {
    switch (role) {
      case 'Citizen': return const CitizenHomePage();
      case 'Family': return const FamilyHomePage();
      case 'Responder': return const ResponderHomePage();
      case 'Hospital': return const HospitalHomePage();
      case 'Police': return const PoliceHomePage();
      case 'Admin': return const AdminHomePage();
      default:
        return Scaffold(body: Center(child: Text('Unsupported account role: $role')));
    }
  }
}
