class AppConfig {
  AppConfig._();

  /// Override with:
  /// flutter run --dart-define=LIFELINK_API_URL=http://<host>:8000/api/v1
  static const apiBaseUrl = String.fromEnvironment(
    'LIFELINK_API_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1',
  );

  /// The realtime service uses the same backend host as the REST API.
  static String get realtimeBaseHttpUrl {
    final uri = Uri.parse(apiBaseUrl);
    final path = uri.path.endsWith('/api/v1')
        ? uri.path.substring(0, uri.path.length - '/api/v1'.length)
        : uri.path;
    return uri.replace(path: path.isEmpty ? '/' : path).toString().replaceFirst(
          RegExp(r'/$'),
          '',
        );
  }
}
