import '../../../core/network/api_client.dart';

class NotificationApi {
  NotificationApi(this._client);
  final ApiClient _client;

  Future<List<Map<String, dynamic>>> listNotifications() async {
    final response = await _client.dio.get('/notifications');
    return (response.data as List<dynamic>)
        .map((item) => Map<String, dynamic>.from(item as Map))
        .toList();
  }

  Future<Map<String, dynamic>> markRead(String notificationId) async {
    final response = await _client.dio.patch('/notifications/$notificationId', data: {'is_read': true});
    return Map<String, dynamic>.from(response.data as Map);
  }
}
