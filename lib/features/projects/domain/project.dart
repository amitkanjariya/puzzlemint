class AdventureProject {
  const AdventureProject({
    required this.id,
    required this.title,
    required this.theme,
    required this.occasion,
    required this.difficulty,
    required this.durationMinutes,
    required this.puzzleCount,
    required this.randomSeed,
    required this.status,
    required this.playerAlias,
    required this.finalMessage,
  });

  final String id, title, theme, occasion, difficulty, status, playerAlias, finalMessage;
  final int durationMinutes, puzzleCount, randomSeed;

  factory AdventureProject.fromJson(Map<String, dynamic> json) => AdventureProject(
        id: json['id'] as String,
        title: json['title'] as String,
        theme: json['theme'] as String,
        occasion: json['occasion'] as String,
        difficulty: json['difficulty'] as String,
        durationMinutes: json['duration_minutes'] as int,
        puzzleCount: json['puzzle_count'] as int,
        randomSeed: json['random_seed'] as int,
        status: json['status'] as String,
        playerAlias: json['player_alias'] as String,
        finalMessage: json['final_message'] as String,
      );
}

class AdventurePuzzle {
  const AdventurePuzzle({required this.id, required this.type, required this.title, required this.position,
    required this.parameters, required this.solution, required this.hints, required this.dependencies,
    required this.validationStatus});

  final String id, type, title, validationStatus;
  final int position;
  final Map<String, dynamic> parameters, solution;
  final List<String> hints, dependencies;

  factory AdventurePuzzle.fromJson(Map<String, dynamic> json) => AdventurePuzzle(
        id: json['id'] as String,
        type: json['type'] as String,
        title: json['title'] as String,
        position: json['position'] as int,
        parameters: Map<String, dynamic>.from(json['parameters'] as Map),
        solution: Map<String, dynamic>.from(json['solution'] as Map),
        hints: (json['hints'] as List).cast<String>(),
        dependencies: (json['dependencies'] as List).cast<String>(),
        validationStatus: json['validation_status'] as String,
      );
}

abstract class ProjectRepository {
  Future<List<AdventureProject>> list();
  Future<AdventureProject> get(String id);
  Future<AdventureProject> create(Map<String, dynamic> values);
  Future<AdventureProject> update(String id, Map<String, dynamic> values);
  Future<void> delete(String id);
  Future<AdventureProject> duplicate(String id);
  Future<List<AdventurePuzzle>> puzzles(String id);
  Future<void> generate(String id);
  Future<Map<String, dynamic>> validate(String id);
  Future<Map<String, dynamic>> exportHtml(String id);
  Future<Map<String, dynamic>> exportPdf(String id);
  Future<AdventurePuzzle> updatePuzzle(String id, Map<String, dynamic> values);
}
