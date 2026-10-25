import 'package:dio/dio.dart';

class ApiClient {
  ApiClient()
      : _dio = Dio(BaseOptions(
          baseUrl: 'http://127.0.0.1:8765/api/v1',
          connectTimeout: const Duration(seconds: 3),
          receiveTimeout: const Duration(seconds: 20),
          contentType: Headers.jsonContentType,
        ));

  final Dio _dio;

  void setToken(String token) {
    _dio.options.headers['Authorization'] = 'Bearer $token';
  }

  Future<dynamic> get(String path) async => (await _dio.get<dynamic>(path)).data;
  Future<dynamic> post(String path, [Object? data]) async =>
      (await _dio.post<dynamic>(path, data: data)).data;
  Future<dynamic> patch(String path, Object data) async =>
      (await _dio.patch<dynamic>(path, data: data)).data;
  Future<void> delete(String path) async => _dio.delete<dynamic>(path);
}

String readableError(Object error) {
  if (error is DioException) {
    if (error.type == DioExceptionType.connectionError ||
        error.type == DioExceptionType.connectionTimeout) {
      return 'The local backend is unavailable. Start it, then try again.';
    }
    if (error.response?.statusCode == 401) {
      return 'Session token rejected. Copy the token from the backend terminal.';
    }
    final detail = error.response?.data;
    if (detail is Map && detail['detail'] is String) return detail['detail'] as String;
    if (error.response?.statusCode == 422) return 'Check the form values and try again.';
    return 'Request failed (${error.response?.statusCode ?? 'network'}). Please try again.';
  }
  return 'Something went wrong. Please try again.';
}
