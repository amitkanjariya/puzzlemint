import '../../../core/api_client.dart';
import '../domain/project.dart';

class ApiProjectRepository implements ProjectRepository {
  ApiProjectRepository(this._api);
  final ApiClient _api;

  @override
  Future<List<AdventureProject>> list() async =>
      ((await _api.get('/projects')) as List).map((item) => AdventureProject.fromJson(Map<String, dynamic>.from(item as Map))).toList();

  @override
  Future<AdventureProject> get(String id) async => AdventureProject.fromJson(Map<String, dynamic>.from(await _api.get('/projects/$id') as Map));

  @override
  Future<AdventureProject> create(Map<String, dynamic> values) async => AdventureProject.fromJson(Map<String, dynamic>.from(await _api.post('/projects', values) as Map));

  @override
  Future<AdventureProject> update(String id, Map<String, dynamic> values) async => AdventureProject.fromJson(Map<String, dynamic>.from(await _api.patch('/projects/$id', values) as Map));

  @override
  Future<void> delete(String id) => _api.delete('/projects/$id');

  @override
  Future<AdventureProject> duplicate(String id) async => AdventureProject.fromJson(
    Map<String, dynamic>.from(await _api.post('/projects/$id/duplicate') as Map));

  @override
  Future<List<AdventurePuzzle>> puzzles(String id) async =>
      ((await _api.get('/projects/$id/puzzles')) as List).map((item) => AdventurePuzzle.fromJson(Map<String, dynamic>.from(item as Map))).toList();

  @override
  Future<void> generate(String id) async { await _api.post('/projects/$id/generate'); }

  @override
  Future<Map<String, dynamic>> validate(String id) async => Map<String, dynamic>.from(await _api.post('/projects/$id/validate') as Map);

  @override
  Future<Map<String, dynamic>> repair(String id) async => Map<String, dynamic>.from(await _api.post('/projects/$id/repair') as Map);

  @override
  Future<AdventurePuzzle> regeneratePuzzle(String id) async => AdventurePuzzle.fromJson(
    Map<String, dynamic>.from(await _api.post('/puzzles/$id/regenerate') as Map));

  @override
  Future<Map<String, dynamic>> exportHtml(String id) async => Map<String, dynamic>.from(await _api.post('/projects/$id/export/html') as Map);

  @override
  Future<Map<String, dynamic>> exportPdf(String id) async => Map<String, dynamic>.from(await _api.post('/projects/$id/export/pdf') as Map);

  @override
  Future<AdventurePuzzle> updatePuzzle(String id, Map<String, dynamic> values) async => AdventurePuzzle.fromJson(Map<String, dynamic>.from(await _api.patch('/puzzles/$id', values) as Map));
}
